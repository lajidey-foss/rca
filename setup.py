from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rca/__init__.py
from rca import __version__ as version

setup(
	name="rca",
	version=version,
	description="App to help simplified returnable case workflow for liquid product with containers",
	author="Jide Olayinka by Gross Innovates",
	author_email="appdev@grossin.co",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
