#!/bin/bash

COMMAND="ping -c1 $1"

$COMMAND > /dev/null
while [ $? -eq 0 ] ; do
        echo "Remote station $1 alive"
        sleep 10
        $COMMAND > /dev/null
done
echo "Host not responding, exiting"
exit 1
