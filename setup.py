from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="agentspring",
    version="0.1.0",
    description="A modular, extensible agentic API framework inspired by the spirit of Spring—growth, flexibility, and rapid development.",
    long_description=(here / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_GITHUB_USERNAME/agentspring",  # Update this before publishing
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0",
        "pydantic>=1.10.0",
        "celery>=5.2.0",
        "redis>=4.0.0",
        "uvicorn>=0.18.0",
        "requests>=2.25.0",
    ],
    include_package_data=True,
    package_data={"agentspring": ["README.md"]},
    entry_points={
        "console_scripts": [
            "agentspring=agentspring.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/YOUR_GITHUB_USERNAME/agentspring",
        "Source": "https://github.com/YOUR_GITHUB_USERNAME/agentspring",
    },
) 