"""Setup configuration for the Slot Game Analyzer."""

from setuptools import setup, find_packages

setup(
    name="slot_analyzer",
    version="0.1.0",
    description="A tool for analyzing slot game patterns and behaviors",
    author="Slot Analyzer Team",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "structlog>=23.1.0",
        "loguru>=0.7.0",
        "pydantic>=2.4.2",
        "kombu>=5.3.1",
        "redis>=5.0.0",
        "aioredis>=2.0.1",
        "click>=8.1.3",
    ],
    entry_points={
        "console_scripts": [
            "slot-analyzer=slot_analyzer.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)