#!/usr/bin/env bash

set -e

if [[ ! $TRAVIS_PULL_REQUEST = 'false' ]] || [[ ! $TRAVIS_BRANCH = 'master' ]]; then
    echo 'Skipping deployment'
    echo "TRAVIS_PULL_REQUEST=${TRAVIS_PULL_REQUEST=unset}"
    echo "TRAVIS_BRANCH=${TRAVIS_BRANCH=unset}"
    exit 0
fi

pip install awscli --user
aws configure set region us-east-1
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_accses_key $AWS_SECRET_ACCESS_KEY

case $STAGE in

    'CLIENT' )
        [ -f .bin-dir ] || (echo '.bin-dir does not exist' && exit 1)
        DIR=$(cat .bin-dir)
        [ -d $DIR ] || (echo "$DIR does not exist" && exit 1)
        echo -e '\n================== Client binary MD5s ==================\n'
        md5sum $DIR/*
        echo -e '\n========================================================\n'
        aws s3 mv --recursive $DIR s3://unnoticed-deploy/$DIR
        ;;

    'LAMBDA' )
        [ -f lambda/pkg.zip ] || (echo 'lambda/pkg.zip does not exist' && exit 1)
        # aws lambda update-function-code --function-name unnoticedPutScores --zip-file fileb://lambda/pkg.zip
        # Leave this disabled for now, it seems that psycopg2 being installed as an egg
        # may be causing problems.
        ;;

    'DISCORD' )
        docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
        docker push $DOCKER_USERNAME/images:unnoticed-discord

esac
