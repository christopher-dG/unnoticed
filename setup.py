import sys
from setuptools import setup


requires = ["boto3", "watchdog"]

if sys.platform in ["win32", "cygwin"]:
    requires.append("win10toast")
elif sys.platform == "darwin":
    requires.append("pync")
else:
    requires.extend(["notify2", "dbus-python"])

setup(
    name="unnoticed",
    version="0.0.1",
    packages=["unnoticed"],
    scripts=["bin/unnoticed"],
    install_requires=requires,
    zip_safe=True,
)
