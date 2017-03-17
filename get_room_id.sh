#!/bin/bash
set -eu

if [ $# != 3 ]; then
   echo "usage: $0 <host> <access token> <#room:server.domain>"
   exit 1
fi

HOST=$1
TOKEN=$2
RALIAS=$3

QALIAS=`echo $RALIAS | sed 's/#/%23/' | sed 's/:/%3A/'`

URL="https://${HOST}:8448/_matrix/client/r0/directory/room/${QALIAS}?access_token=$TOKEN"


curl -i -k -X GET --header 'Accept: application/json'  $URL
