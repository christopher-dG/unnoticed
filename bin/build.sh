#!/usr/bin/env bash

cd $(dirname $(dirname $0))
export DIR=bin-$(date '+%FT%T')-${TRAVIS_BRANCH=local}
mkdir -p $DIR

echo -e '\n========================= Linux 64-bit =========================\n'
export GOOS=linux GOARCH=amd64
go build -v -o $DIR/$GOOS-$GOARCH-scan ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch ./cmd/unnoticed-watch
echo -e '\n========================= Linux 32-bit =========================\n'
export GOOS=linux GOARCH=386
go build -v -o $DIR/$GOOS-$GOARCH-scan ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch ./cmd/unnoticed-watch

echo -e '\n======================== Windows 64-bit ========================\n'
export GOOS=windows GOARCH=amd64
go build -v -o $DIR/$GOOS-$GOARCH-scan.exe ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch.exe ./cmd/unnoticed-watch
echo -e '\n======================== Windows 32-bit ========================\n'
export GOOS=windows GOARCH=386
go build -v -o $DIR/$GOOS-$GOARCH-scan.exe ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch.exe ./cmd/unnoticed-watch

echo -e '\n========================= MacOS 64-bit =========================\n'
export GOOS=darwin GOARCH=amd64
go build -v -o $DIR/$GOOS-$GOARCH-scan ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch ./cmd/unnoticed-watch
echo -e '\n========================= MacOS 32-bit =========================\n'
export GOOS=darwin GOARCH=386
go build -v -o $DIR/$GOOS-$GOARCH-scan ./cmd/unnoticed-scan
go build -v -o $DIR/$GOOS-$GOARCH-watch ./cmd/unnoticed-watch

echo $DIR > .bin-dir
cd - > /dev/null
