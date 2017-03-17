#!/bin/bash
set -eu

if [ $# != 4 ]; then
   echo "usage: $0 <host> <access token>  <room id> <mxc:/.../..>"
   exit 1
fi

HOST=$1
TOKEN=$2
ROOM=$3
AVATAR=$4

QROOM=`echo $ROOM | sed 's/#/%23/' | sed 's/:/%3A/' | sed 's/!/%21/'`


URL="https://${HOST}:8448/_matrix/client/r0/rooms/${QROOM}/state/m.room.avatar?access_token=$TOKEN"
echo $URL

curl -i -k -X PUT --header 'Accept: application/json' -d "{ \
        \"url\": \"$AVATAR\"  \
   }" $URL
