# psycopg2 for AWS Lambda

All of the Lambda functions in this directory rely on
[psycopg2](http://initd.org/psycopg/), a package for interacting with
PostgreSQL databases. The AMI on which Lambda functions run doesn't have the
required `libpq` libraries available to dynamically link, so we need to use
[this](https://github.com/jkehler/awslambda-psycopg2) version which contains
statically linked libraries.

To prepare a deployment package, `cd` to the function's directory, and run:

```sh
pip3 install -r requirements.txt -t .
git clone https://github.com/jkehler/awslambda-psycopg2
mv awslambda-psycopg2/psycopg2-3.6 ./psycopg2
rm -rf awslambda-psycopg2
zip -r pkg.zip *
```
