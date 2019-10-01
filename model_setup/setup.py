from setuptools import setup, find_packages

setup(
    name='model_setup',
    version='1.0',
    description='Machine Learning Model',
    author='Ahiwe Onyebuchi Valentine',
    author_email='vahiwe@gmail.com',
    packages=find_packages(
        include=['model_setup', 'model_setup.*'])  # same as name
)
