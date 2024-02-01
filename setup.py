"""This module provides setup for pip."""

from setuptools import setup, find_packages

setup(
    name="stewartfilmscreenclient",
    version="1.0.0",
    packages=find_packages(),
    url="https://github.com/dstanchfield/stewartfilmscreenclient",
    license="MIT",
    author="Darin Stanchfield",
    author_email="darin@stanchfield.com",
    description="Python client for controlling Stewart Filmscreen devices",
    install_requires=[
        "telnetlib3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
