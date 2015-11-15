from distutils.core import setup

setup(
    # Application name:
    name="DockerWatcher",

    # Version number (initial):
    version="0.0.0",

    # Application author details:
    author="Ruslan Gustomyasov",
    author_email="rusik@4ege.ru",

    # Packages
    packages=["client", "common", "master", "slave", "watcher", "web"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/DockerWatcher_v001/",

    #
    # license="LICENSE.txt",
    description="Docker Watcher",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "flask", "tornado", "python-etcd", "psutil", "requests", "docker-py"
    ],
)