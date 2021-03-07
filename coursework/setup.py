import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esecurity_cvicenti",
    version="0.0.1",
    author="Carlos Vicenti",
    author_email="40431915@live.napier.ac.uk",
    description="coursework esecurity module 2019",
    url="https://github.com/cvicenti/esecurity",
    packages=setuptools.find_packages(),
)
