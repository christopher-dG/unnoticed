from setuptools import setup

setup(
    name="unnoticed",
    version="0.0.1",
    packages=["unnoticed"],
    scripts=["bin/unnoticed"],
    install_requires=["boto3", "watchdog"],
    zip_safe=True,
)
