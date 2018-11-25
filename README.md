# ECS / AWS Spawner for Juputer HUB

[![Build Status](https://travis-ci.org/elviejokike/ecsspawner.svg?branch=master)](https://travis-ci.org/elviejokike/ecsspawner)

The ecsspawner (also known as JupyterHub ECS/AWS Spawner) enables JupyterHub to spawn single-user notebook servers on a ECS cluster in AWS.

### Introduction

Amazon ECS (Elastic Container Service) is a highly scalable, high-performance
container orchestration service which allows us to easily run and scale containerized applications on AWS.

#### ECS Task

Jupyter Notebooks are instantiated using ECS Tasks. A *Task** is the mechanism offered by Amazon
ECS to encapsulate containers allowing us to specificy the charateristics of the tasks using
[Task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html).

A task definition includes:
- The Docker image to use
- CPU and memory requirements
- AWS Network, logging, volumens and IAM roles
- Launch types: EC2 or Fargate. [Read more about](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html)


When using EC2 launch type, we have some alternatives for starting ECS tasks:

1. Let Amazon ECS to run the *Task* based on the task definition using the current cluster capacity.
2. Create a EC2 instance on the cluster, and start the ECS task on the created EC2 instance.
3. Combined: Let amazon to run the task (1) and as a fallback scenario use (2) when no cluster capacity is available.

### How to

```python
## Spawner Configuration

c.JupyterHub.spawner_class = 'awsspawner.EcsTaskSpawner'
```

### Spawner Configuration

**strategy**: Defines the spawning mechanism to be used. Possible values are

- ECSSpawnerHandler:
- EC2SpawnerHandler:
- ECSxEC2SpawnerHandler:

**cluster_name**: When using ECS spawning mechanim, a cluster name is mandatory

**ecs_task_definition**: When using ECS spawning mechanim, a task definition string is mandatory. The task definition must point to a definition where a jupyter notebook is instantiated.

**ec2_instance_template**: When using EC2/ECSxEC2 mechanism, an AWS launch template is required to determine for EC2 instantiation.

```python
c.Spawner.strategy = 'ECSxEC2SpawnerHandler'
c.Spawner.strategy_parms = {
    'cluster_name': os.environ.get('AWS_CLUSTER', 'notebook-cluster'),
    'ec2_instance_template': 'demo01',
    'ecs_task_definition': 'hello-world:230',
    'port': 8888
}
```


