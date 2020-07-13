#!/bin/sh
lastweek=$(date -d "-7 days" "+%YW%V")
filename="./img/"$lastweek".png"
echo $lastweek
echo $filename
python3 ~/Dropbox/Server/TimeReport/main.py -r -l 1 -t $lastweek
coscmd upload $filename imgs/time/
