#!/usr/bin/env bash

source /root/app/.env
if [[ $1 = 'bash' ]]; then
    exec bash
else
    exec /root/app/bot.rb "$@"
fi
