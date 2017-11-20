#!/usr/bin/env bash

set -e

[ -z $STAGE ] && echo '$STAGE is not set' && exit 1

case $STAGE in

    'TEST' )
        pip install awscli --user
        aws configure set region us-east-1
        aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
        aws configure set aws_secret_accses_key $AWS_SECRET_ACCESS_KEY
        aws s3 sync s3://unnoticed-test ./testdata
        go test
        ;;

    'CLIENT' )
        export DIR=bin-$(date '+%FT%T')-${TRAVIS_BRANCH=local}
        mkdir -vp $DIR

        echo -e '\n========================= Linux 64-bit =========================\n'
        export GOOS=linux GOARCH=amd64
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch ./cmd/osu-watch
        echo -e '\n========================= Linux 32-bit =========================\n'
        export GOOS=linux GOARCH=386
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch ./cmd/osu-watch
        echo -e '\n======================== Windows 64-bit ========================\n'
        export GOOS=windows GOARCH=amd64
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan.exe ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch.exe ./cmd/osu-watch
        echo -e '\n======================== Windows 32-bit ========================\n'
        export GOOS=windows GOARCH=386
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan.exe ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch.exe ./cmd/osu-watch
        echo -e '\n========================= MacOS 64-bit =========================\n'
        export GOOS=darwin GOARCH=amd64
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch ./cmd/osu-watch
        echo -e '\n========================= MacOS 32-bit =========================\n'
        export GOOS=darwin GOARCH=386
        go build -v -o $DIR/$GOOS-$GOARCH-osu-scan ./cmd/osu-scan
        go build -v -o $DIR/$GOOS-$GOARCH-osu-watch ./cmd/osu-watch

        echo $DIR > .bin-dir
        ;;

    'API' )
        cd api
        git clone https://github.com/jkehler/awslambda-psycopg2
        cp -r awslambda-psycopg2/psycopg2-3.6 ./getscores/psycopg2
        cp -r awslambda-psycopg2/psycopg2-3.6 ./putscores/psycopg2
        rm -rf awslambda-psycopg2
        cd getscores
        pip3 install -r requirements.txt -t .
        zip -r pkg.zip *
        cd ../putscores
        pip3 install -r requirements.txt -t .
        zip -r pkg.zip *
        ;;

    'DISCORD' )
        echo "export DISCORD_CLIENT_ID=\"$DISCORD_CLIENT_ID\"" >> discord/.env
        echo "export DISCORD_TOKEN=\"$DISCORD_TOKEN\"" >> discord/.env
        echo "export DB_HOST=\"$DB_HOST\"" >> discord/.env
        echo "export DB_NAME=\"$DB_NAME\"" >> discord/.env
        echo "export DB_USER=\"$DB_USER\"" >> discord/.env
        echo "export DB_PASSWORD=\"$DB_PASSWORD\"" >> discord/.env
        echo "export OSU_API_KEY=\"$OSU_API_KEY\"" >> discord/.env
        docker build -t $DOCKER_USERNAME/images:unnoticed-discord discord
        ;;

esac
