from setuptools import setup
import sys

if sys.platform in ["win32", "cygwin"]:
    notifier = "win10toast"
elif sys.platform == "darwin":
    notifier = "pync"
else:
    notifier = "notify2"

setup(
    name="unnoticed",
    version="0.0.1",
    packages=["unnoticed"],
    scripts=["bin/unnoticed"],
    install_requires=["boto3", "watchdog", notifier],
    zip_safe=True,
)
