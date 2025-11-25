"""Setup script for Ranex Framework development installation."""
from setuptools import setup, find_packages
import os

# Read the directory to find packages
packages = find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*', 'app', 'app.*'])

setup(
    name="ranex",
    version="0.0.1",
    description="Ranex Framework - Hybrid AI-Governance Framework",
    packages=packages,
    python_requires=">=3.12",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    # Don't use pyproject.toml for build (it's configured for maturin)
    setup_requires=[],
)

