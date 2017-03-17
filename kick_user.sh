#!/bin/bash
set -eu

if [ $# != 4 ]; then
   echo "usage: $0 <host> <access token> <user id> <#room:server.domain>"
   exit 1
fi

HOST=$1
TOKEN=$2
USER=$3
RALIAS=$4

QALIAS=`echo $RALIAS | sed 's/#/%23/' | sed 's/:/%3A/' | sed 's/!/%21/'`


URL="https://${HOST}:8448/_matrix/client/r0/rooms/${QALIAS}/kick?access_token=$TOKEN"


curl -i -k -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "{ \
   \"reason\": \"dont ask im the boss\", \
   \"user_id\": \"$USER\" \
 }" $URL