import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fossology",
    version="0.0.3",
    description="A library to automate Fossology from Python scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.siemens.com/fossology/fossology-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT",
        "Operating System :: OS Independent",
    ],
)
