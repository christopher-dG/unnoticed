#!/usr/bin/env bash

if [[ $TRAVIS_PULL_REQUEST = 'false' ]] && [[ $TRAVIS_BRANCH = 'master' ]]; then
    cd $(dirname $(dirname $0))
    [ -f .bin-dir ] || (echo './.bin-dir does not exist' && exit 1)
    DIR=$(cat .bin-dir)
    pip install awscli --user
    aws configure set region us-east-1
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    aws configure set aws_secret_accses_key $AWS_SECRET_ACCESS_KEY
    md5sum $DIR/*
    aws s3 mv --recursive $DIR s3://unnoticed-deploy/$DIR
    cd - > /dev/null
else
    echo 'Skipping deployment'
    echo "TRAVIS_PULL_REQUEST=${TRAVIS_PULL_REQUEST=unset}"
    echo "TRAVIS_BRANCH=${TRAVIS_BRANCH=unset}"
fi
