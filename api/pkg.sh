#!/usr/bin/env bash

if [ -z $1 ]; then
    echo "No directory specified"
    exit 1
fi
cd $1
python3 -m pip install -r requirements.txt -t .
git clone https://github.com/jkehler/awslambda-psycopg2
mv awslambda-psycopg2/psycopg2-3.6 ./psycopg2
rm -rf awslambda-psycopg2/psycopg2-3.6
zip -r pkg.zip *
