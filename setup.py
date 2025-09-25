from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="agentspring",
    version="0.1.0",
    packages=find_packages(include=['agentspring*']),
    install_requires=requirements,
    python_requires='>=3.8',
    author="Your Name",
    author_email="your.email@example.com",
    description="AgentSpring - Infrastructure for building agentic applications",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentspring",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'agentspring=agentspring.cli:main',
        ],
    },
)