from setuptools import setup, find_packages

setup(
    name='awsspawner',
    version = '0.0.1',
    author='Kike',
    url='https://github.com/elviejokike/awsspawner4jhub',
    keywords=[
          'Juputer',
          'Juputer HUB',
          'AWS',
          'ECS',
          'EC2',
          'Spawner'
    ],
    license="MIT",
    author_email = 'kike@world.com',
    description = 'ECS/EC2/AWS Spawner for Jupyter Hub',
    install_requires=['jupyterhub>=0.8.1','boto3==1.5.24','escapism==1.0.0','peewee==3.0.15'],
    packages=find_packages(exclude=['tests*','examples*']),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
