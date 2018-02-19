from setuptools import setup, find_packages

setup(
    name='ecsspawner',
    version = '0.0.1',
    author='Kike',
    url='https://github.com/elviejokike/ecsspawner',
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
    description = 'ECS/AWS Spawner for Jupyter Hub',
    keywords = 'ECS AWS Jupyter Hub',
    install_requires=['jupyterhub==0.7.2','boto3==1.5.24','escapism==1.0.0','peewee==3.0.15'],
    packages=find_packages(exclude=['tests*','examples*']),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
