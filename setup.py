from setuptools import setup, find_packages


try:
    from ecsspawner import __about__
    about = __about__.__dict__
except ImportError:
    # installing - dependencies are not there yet
    # Manually extract the __about__
    about = dict()
    exec(open("about/__about__.py").read(), about)

setup(
    name='ecsspawner',
    version = about['__version__'],
    author = about['__author__'],
    url=about['__url__'],
    license="Apache License 2.0",
    author_email = 'kike@world.com',
    description = 'ECS/AWS Spawner for Jupyter Hub',
    keywords = 'ECS AWS Jupyter Hub',
    packages=find_packages(exclude=['tests*','examples*']),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
