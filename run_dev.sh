#!/bin/bash

#REDIS="redis-server"

#RESULT=`pgrep ${REDIS}`

#if [ "${RESULT:-null}" = null ]; then
#    redis-server etc/redis/redis-local.conf &
#fi

python web/manage.py runserver --settings=whim.settings_local