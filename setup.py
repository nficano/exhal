"""This module contains setup instructions for exhal."""
import codecs
import os
import sys
from shutil import rmtree

from setuptools import Command
from setuptools import setup

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(THIS_DIR, "README.md")

with codecs.open(README, encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


class UploadCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Print in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        """Initialize options."""
        pass

    def finalize_options(self):
        """Finialize options."""
        pass

    def run(self):
        """Upload release to Pypi."""
        try:
            self.status("Removing previous builds ...")
            rmtree(os.path.join(THIS_DIR, "dist"))
        except Exception:
            pass
        self.status("Building Source distribution ...")
        os.system(f"{sys.executable} setup.py sdist")
        self.status("Uploading the package to PyPI via Twine ...")
        os.system("twine upload dist/*")
        sys.exit()


setup(
    name="exhal",
    version="1.1.0",
    author="Nick Ficano",
    author_email="nficano@gmail.com",
    packages=["exhal"],
    url="https://github.com/nficano/exhal",
    license="MIT",
    package_data={"": ["LICENSE"]},
    scripts=["scripts/exhal"],
    install_requires=requirements,
    setup_requires=["wheel"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    description="Exhal for BlinkStick: Humanize your hardware",
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    cmdclass={"upload": UploadCommand},
)
