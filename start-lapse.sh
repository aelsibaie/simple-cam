#!/bin/bash

# kill it if we are running, ignoring errors if not
pkill -f cam3.py

# start it up for sure
cd /home/pi
nohup python3 simple_cam.py  > cam-log.txt 2>&1 &
