import setuptools
from mlops_nba import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    install_requires = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="data-pipeline",
    version=__version__,
    author="Data Science Team @Fullsoon",
    author_email="contact@fullsoon.co",
    description="data-pipeline contains all the bricks you need to create a functionnal data science project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests.*", "tests"]),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
