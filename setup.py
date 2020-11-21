from setuptools import setup, find_packages

setup(
    name="conda-forge-artifact-validation",
    version="0.0.1",
    description="",
    author="conda-forge/core",
    author_email="",
    scripts=["bin/conda-forge-artifact-validation"],
    url="https://github.com/conda-forge/artifact-validation",
    packages=find_packages(),
)
