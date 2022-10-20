import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "not_a_blockchain",
    version = "0.0.4",
    author = "Matthew Ruge",
    author_email = "matthew.ruge@shrgroupllc.com",
    description = ("Toy to help me understand blockchain"),
    license = "BSD",
    keywords = "blockchain graph",
    url = "http://packages.python.org/not_a_blockchain",
    packages=['chain'],
    long_description="Toy to help me understand blockchain",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)