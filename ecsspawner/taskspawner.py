import logging
import os
import string
from textwrap import dedent

import boto3
import escapism
from jupyterhub.spawner import Spawner
from tornado import gen
from traitlets import (
    Integer,
    Unicode,
    Bool
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EcsTaskSpawner(Spawner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """ Creates and boots a new server to host the worker instance."""
        self.log.info("function create_new_instance %s" % self.user.name)
        self.ecs_client = boto3.client('ecs')
        self.ec2_client = boto3.client('ec2')
        self.cluster_name = os.environ.get('AWS_CLUSTER', 'pathis-dev-ecs-cluster-notebook1')

        self.task_name = self._expand_user_properties(self.task_name_template)

        self.user_task = None

    task_name_template = Unicode(
        'notebook-{username}{servername}',
        config=True,
        help=dedent(
            """
            Template to use to form the name of user's task
            """
        )
    )

    cluster_name = Unicode("",
       help="""
            Cluster Name to be used for the Spawner
       """
    ).tag(config=True)

    ecs_task_on_ec2_instance = Bool(True,
        help="""
            Indicates if the ECS Spawner mechanism must create an EC2 instance itself, or let ECS to choose one for us.
        """
    ).tag(config=True)

    ip = Unicode('0.0.0.0',
        help="""
            The IP address (or hostname) the single-user server should listen on.
        """
    ).tag(config=True)

    port = Integer(8888,
        help="""
            Default port to 8888
        """
    ).tag(config=True)

    def get_state(self):
        """
        Save state required to reinstate this user's task from scratch
        We save the `task_name`, even though we could easily compute it,
        because JupyterHub requires you save *some* state! Otherwise
        it assumes your server is dead. This works around that.
        It's also useful for cases when the `task_template` changes between
        restarts - this keeps the old pods around.
        """
        state = super().get_state()
        state['task_name'] = self.task_name
        return state

    def load_state(self, state):
        """
        Load state from storage required to reinstate this user's task.
        """
        if 'task_name' in state:
            self.pod_name = state['task_name']



    @gen.coroutine
    def start(self):
        self.log.info("function start for user %s" % self.user.name)

        task = yield self.get_task()
        if task is None:
            ip_address = yield self.create_new_task()
            return ip_address, self.port


    @gen.coroutine
    def stop(self, now=False):
        self.log.info("function stop called for %s" % self.user.name)
        self.user_task = None

        task = yield self.get_task()
        if task:
            self.ecs_client.stop_task(
                cluster=self.cluster_name,
                task=task['taskArn']
            )

        else:
            self.log.info("No ECS task found to be stopped %s" % self.user.name)

        self.clear_state()

    @gen.coroutine
    def poll(self):
        self.log.debug("function poll for user %s" % self.user.name)
        task = yield self.get_task()
        if task:
            return None # Still running
        else:
            return 0


    @gen.coroutine
    def get_task(self):
        tasks = self.ecs_client.list_tasks(
            cluster=self.cluster_name,
            startedBy=self._get_task_identifier(),
            desiredStatus='RUNNING'
        )
        if tasks and len(tasks['taskArns']) > 0:
            return self.ecs_client.describe_tasks(
                cluster=self.cluster_name,
                tasks=[
                    tasks['taskArns'][0]
                ]

            )['tasks'][0]
        else:
            return None


    @gen.coroutine
    def create_new_task(self):

        if self.ecs_task_on_ec2_instance:

            self.log.info("function create new task for user %s" % self.user.name)
            task_def =  yield self._get_task_definition()

            response = self.ecs_client.register_task_definition(**task_def)
            task_def_arn = response['taskDefinition']['taskDefinitionArn']

            instance = yield self._create_instance()

            selected_container_instance = yield self._get_container_instance(instance['InstanceId'])

            env = self.get_env()
            env['JPY_USER'] = self.user.name
            env['JPY_BASE_URL'] = self.user.server.base_url
            env['JPY_COOKIE_NAME'] = self.user.server.cookie_name

            container_env = self._expand_env(env)

            self.log.info("starting ecs task for user %s" % self.user.name)

            task = self.ecs_client.start_task(taskDefinition=task_def_arn,
               cluster = self.cluster_name,
               startedBy = self._get_task_identifier(),
               overrides={
                   'containerOverrides': [
                       {
                           'name': 'hello-world',
                           'environment': container_env
                       }
                   ]
               },
               containerInstances = [selected_container_instance['containerInstanceArn']]
            )['tasks'][0]

            waiter = self.ecs_client.get_waiter('tasks_running')
            waiter.wait(cluster=self.cluster_name, tasks=[task['taskArn']])

            self.user_task = task

            self.log.info("ecs task up and running for %s" % self.user.name)

            return instance['NetworkInterfaces'][0]['PrivateIpAddress']

        else:
            raise ValueError('Work in progress for ECS only')
        #return instance['PublicIpAddress']

    @gen.coroutine
    def _create_instance(self):

        self.log.info("function create instance for user %s" % self.user.name)

        instance = self.ec2_client.run_instances(
            # Use the official ECS image
            MinCount=1,
            MaxCount=1,
            KeyName='pathis-dev-eu-central-1',
            LaunchTemplate={
                'LaunchTemplateName':'thisonefirst'
            },
            UserData="#!/bin/bash \n echo ECS_CLUSTER=" + self.cluster_name + " >> /etc/ecs/ecs.config",
            NetworkInterfaces=[
                {
                    'AssociatePublicIpAddress': True,
                    'DeviceIndex': 0,
                    'SubnetId': 'subnet-e30aa088'
                }
            ]
        )['Instances'][0]

        waiter = self.ec2_client.get_waiter('instance_status_ok')
        waiter.wait(InstanceIds=[instance['InstanceId']])

        instance = self.ec2_client.describe_instances(InstanceIds=[instance['InstanceId']])['Reservations'][0]['Instances'][0]

        return instance

    @gen.coroutine
    def _get_container_instance(self, ec2_instance_id):
        """
        Look for container instance related to the instance ID created
        :param ec2_instance_id:
        :return:
        """

        selected_container_instance = None
        container_instances_arns = self.ecs_client.list_container_instances(cluster=self.cluster_name)['containerInstanceArns']
        container_instances = self.ecs_client.describe_container_instances(cluster=self.cluster_name, containerInstances=container_instances_arns)['containerInstances']
        for container_instance in container_instances:
            if container_instance['ec2InstanceId'] == ec2_instance_id:
                selected_container_instance = container_instance

        return selected_container_instance

    @gen.coroutine
    def _get_task_definition(self):

        self.log.info("function get task definition for user %s" % self.user.name)

        task_def = {
            'family': 'hello-world',
            'volumes': [],
            'containerDefinitions': [
                {
                    'memory': 1024,
                    'cpu': 0,
                    'essential': True,
                    'name': 'hello-world',
                    'image': 'jupyter/scipy-notebook:ae885c0a6226',
                    'portMappings': [
                        {
                            'containerPort': self.port,
                            'hostPort': 8888,
                            'protocol': 'tcp'
                        }
                    ],
                    'command': [
                        'start-notebook.sh',
                    ],
                }
            ]
        }
        return task_def


    def _get_task_identifier(self):
        """
        Return Task identifier
        :return:
        """
        return 'EcsTaskSpawner:'+ self.user.name

    def _expand_env(self, env):
        """
        Expand get_env to ECS task environment
        """
        result = []

        if env:
            for key in env.keys():
                entry = {
                    'name': key,
                    'value': env.get(key)
                }
                result.append(entry)

        return result

    def get_env(self):
        env = super().get_env()

        env['JPY_HUB_API_URL'] = 'http://' + os.environ.get('HUB_HOST_IP', None) + ':8080/jupyter/hub/api'
        # env['JPY_HUB_API_URL'] = self.hub.api_url
        env['JPY_HUB_PREFIX'] = self.hub.server.base_url


        env.update(dict(
            JPY_USER=self.user.name,
            JPY_COOKIE_NAME=self.user.server.cookie_name,
            JPY_BASE_URL=self.user.server.base_url,
            JPY_HUB_PREFIX=self.hub.server.base_url
        ))

        return env


    def _expand_user_properties(self, template):
        # Make sure username and servername match the restrictions for DNS labels
        safe_chars = set(string.ascii_lowercase + string.digits)

        # Set servername based on whether named-server initialised
        servername = ''

        legacy_escaped_username = ''.join([s if s in safe_chars else '-' for s in self.user.name.lower()])
        safe_username = escapism.escape(self.user.name, safe=safe_chars, escape_char='-').lower()
        return template.format(
            userid=self.user.id,
            username=safe_username,
            legacy_escape_username=legacy_escaped_username,
            servername=servername
        )
