# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os

import pkg_resources
from setuptools import setup, find_packages

setup(
    name="DataScienceProblems",
    py_modules=["DataScienceProblems"],
    version="1.0",
    description="",
    author="Microsoft",
    packages=find_packages(),
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    entry_points={
        "console_scripts": [
            "evaluate_dsp = data_science_problems.evaluate_dsp",
        ]
    }
)
