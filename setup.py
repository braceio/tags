import os
from distutils.core import setup

root = os.path.dirname(os.path.realpath(__file__))

setup(
    name='brace-tags',
    version='1.0.9',
    author='Cole Krumbholz, Lauri Hynynen',
    author_email='team@brace.io',
    description='The simplest static site generator',
    packages=['tags'],
    install_requires=open(root+"/requirements.txt").read().splitlines(),
    long_description=open(root+"/README.md").read(),
    license='LICENSE',
    scripts=['scripts/tags'],
)