import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fossology-python",
    version="0.0.2",
    author="Marion Deveaud",
    author_email="marion.deveaud@siemens.com",
    description="A library to automate Fossology from Python scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.siemens.com/fossology/fossology-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Siemens Inner Source License",
        "Operating System :: OS Independent",
    ],
)
