#!/bin/bash
set -eu

if [ $# != 3 ]; then
   echo "usage: $0 <host> <access token> </path/to/file>"
   exit 1
fi

HOST=$1
TOKEN=$2
FNAME=$3
MIMETYPE=`file -b --mime-type $FNAME`

f="$FNAME"
f=${f//\\/\\\\}
f=${f//\"/\\\"}
f=${f//;/\\;}

URL="https://${HOST}:8448/_matrix/media/r0/upload?access_token=$TOKEN"


curl -i -k -X POST -H "Content-Type: $MIMETYPE" --data-binary "@$f"  $URL
