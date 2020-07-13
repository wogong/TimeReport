#!/bin/sh
lastmonth=$(date -d "-30 days" "+%YM%m")
filename="./img/"$lastmonth".png"
echo $lastmonth
echo $filename
python3 ~/Dropbox/Server/TimeReport/main.py -r -l 2 -t $lastmonth
coscmd upload $filename imgs/time/
