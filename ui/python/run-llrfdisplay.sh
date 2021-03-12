#!/bin/bash

export DISPLAY=0.0

now=$(date +%c)

printf "$now -- "

process="$(pgrep -f llrfdisplay.py)"

# change into scripts directory
## ONLY ON BASH!
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [ -z "$process" ]; then
        printf "restarting .....................\n\n\n"
#       ./mailrestart.sh "$now"
        echo "------" >> /var/log/llrfdisplay.log
        python3 -u llrfdisplay.py >> /var/log/llrfdisplay.log 2>&1 &
else
        printf "still running\n"
fi

