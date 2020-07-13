#!/bin/sh
yesterday=$(date -d "yesterday" "+%Y%m%d")
filename="./img/"$yesterday".png"
python3 ~/Dropbox/Server/TimeReport/main.py -r -l 0 -t $yesterday
coscmd upload $filename imgs/time/
