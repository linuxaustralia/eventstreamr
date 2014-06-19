#!/bin/bash

COMMAND=`lspci | grep 1394`

$COMMAND > /dev/null
while [ $? -eq 0 ] ; do
        echo "A FireWire controller exists"
        sleep 10
        $COMMAND > /dev/null
done
echo "No FireWire controller found"
exit 1
