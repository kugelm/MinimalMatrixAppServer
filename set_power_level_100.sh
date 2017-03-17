#!/bin/bash
set -eu

if [ $# != 5 ]; then
   echo "usage: $0 <host> <access token> <user id> <room id> <as user>"
   exit 1
fi

HOST=$1
TOKEN=$2
USER=$3
ROOM=$4
ASUSER=$5

QUSER=`echo $USER | sed 's/@/%40/' | sed 's/:/%3A/'`
QROOM=`echo $ROOM | sed 's/#/%23/' | sed 's/:/%3A/' | sed 's/!/%21/'`


URL="https://${HOST}:8448/_matrix/client/r0/rooms/${QROOM}/state/m.room.power_levels?access_token=$TOKEN"
echo $URL

curl -i -k -X PUT --header 'Accept: application/json' -d "{ \
        \"ban\": 50,  \
        \"events\": { \
            \"m.room.name\": 100,        \
            \"m.room.power_levels\": 100 \
        },  \
        \"events_default\": 0,   \
        \"invite\": 50,  \
        \"kick\": 50,    \
        \"redact\": 50,  \
        \"state_default\": 50,  \
        \"users\": {  \
            \"${USER}\": 100,  \
            \"${ASUSER}\": 100  \
        },  \
        \"users_default\": 0  \
   }" $URL
