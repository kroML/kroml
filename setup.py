import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kroml",
    version="0.0.1",
    author="kroML FW",
    author_email="kroml.framework@gmail.com",
    description="A framework for deploying ML projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kroML/kroml",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)