from setuptools import setup, find_packages

# This file is kept for backward compatibility
# The actual configuration is in pyproject.toml

setup(
    name="agentspring",
    version="0.1.0",
    packages=find_packages(include=['agentspring*']),
    python_requires='>=3.8',
    install_requires=[
        'pydantic>=2.0.0,<3.0.0',
        'typing-extensions>=4.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.20.0',
            'black>=23.0.0',
            'isort>=5.0.0',
            'mypy>=1.0.0',
        ],
    },
    author="Navdeep Gill",
    author_email="mr.navdeepgill@gmail.com",
    description="A flexible and extensible framework for building agentic workflows",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/navdeep-G/agentspring",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
