# psycopg2 for AWS Lambda

All of the Lambda functions in this directory rely on
[psycopg2](http://initd.org/psycopg/), a package for interacting with
PostgreSQL databases. The AMI on which Lambda functions run doesn't have the
required `libpq` libraries available to dynamically link, so we need to use
[this](https://github.com/jkehler/awslambda-psycopg2) version which contains
statically linked libraries.

To prepare a deployment package, run: `./pkg.sh <dir>`.
