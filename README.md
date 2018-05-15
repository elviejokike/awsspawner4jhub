# ECS / AWS Spawner for Juputer HUB

[![Build Status](https://travis-ci.org/elviejokike/ecsspawner.svg?branch=master)](https://travis-ci.org/elviejokike/ecsspawner)

The ecsspawner (also known as JupyterHub ECS/AWS Spawner) enables JupyterHub to spawn single-user notebook servers on a ECS cluster in AWS.

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
    'cluster_name': os.environ.get('AWS_CLUSTER', 'pathis-dev-ecs-cluster-notebook1'),
    'ec2_instance_template': 'demo01',
    'ecs_task_definition': 'hello-world:230',
    'port': 8888
}
```


