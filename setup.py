from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in wireapp/__init__.py
from wireapp import __version__ as version

setup(
	name="wireapp",
	version=version,
	description="Utility app for small businesses",
	author="Salim",
	author_email="dsmwaura@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
