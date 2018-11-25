# ECS / AWS Spawner for Juputer HUB

[![Build Status](https://travis-ci.org/elviejokike/awsspawner4jhub.svg?branch=master)](https://travis-ci.org/elviejokike/awsspawner4jhub)

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

- ECSSpawnerHandler: Let Amazon ECS to run the *Task* based on the task definition
- ECSxEC2SpawnerHandler: Create a EC2 instance on the cluster, and start the ECS task on the created EC2 instance

**cluster_name**: ECS cluster name.

**ecs_task_definition**: When using ECS spawning mechanim, a task definition string is mandatory. The task definition must point to a definition where a Jupyter notebook is specified.

**ec2_instance_template**: When using EC2/ECSxEC2 mechanism, an AWS ECS instance template is required to determine EC2 instantiation.

```python
c.Spawner.strategy = 'ECSxEC2SpawnerHandler'
c.Spawner.strategy_parms = {
    'cluster_name': 'notebook-cluster',
    'ec2_instance_template': 'ec2-demo-template',
    'ecs_task_definition': 'jupyter-notebook-template',
    'port': 8888
}
```


