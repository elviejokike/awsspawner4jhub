# ECS / AWS Spawner for Juputer HUB
ECS Spawner for Jupyter HUB

[![Build Status](https://travis-ci.org/elviejokike/ecsspawner.svg?branch=master)](https://travis-ci.org/elviejokike/ecsspawner)



### How to

```python
## Spawner Configuration

c.JupyterHub.spawner_class = 'ecsspawner.EcsTaskSpawner'
```

### Cluster Name Configuration

```python
c.Spawner.cluster_name = 'MyClusterName'
```
### ECS Task Definition

```python
c.Spawner.ecs_task_definition = 'MyTaskDefinition'
```

### Create Single EC2 instance for each task

```python
c.Spawner.ecs_task_on_ec2_instance = True
c.Spawner.ec2_instance_template = 'My EC2 Template'
```

