# kill it if we are running, ignoring errors if not
pkill -f simple-cam.py

# start it up for sure
cd /home/pi
nohup python3 simple-cam.py  >/dev/null 2>&1 &
