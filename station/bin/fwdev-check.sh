#!/bin/bash

COMMAND="grep $1 /sys/bus/firewire/devices/fw*/*vendor"

$COMMAND > /dev/null
while [ $? -eq 0 ] ; do
        echo "Device with vendor id $1 exists"
        sleep 10
        $COMMAND > /dev/null
done
echo "Device $1 removed from bus, exiting"
exit 1
