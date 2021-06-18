#!/usr/bin/python3

# this is Python 3!

import os
import time
import datetime
import pexpect
import sys
import gmail

# 0=L, 1=M1, 2=M2, 3=M3, 4=S, 5=RAW
RESOLUTION = 4

# interval between photos in seconds
INTERVAL = 60*2

# path to your chdkptp installation, including lua stuff
chdkptp_path = "/home/pi/chdkptp-r964/"

# path to the root of directory to store jpgs for timelapse processing.
# a subdirectory is created with the current date and images are moved there
# with sequential numbers for ffmpeg timelapse generation
img_root = "/home/pi/pictures"

# check for the existence of this file. When it's deleted stop
# the capture loop. This is how the movie generation process stops
# the image generation process
semaphore_fn = "/home/pi/running.txt"


# tell chdkptp where to find its lua stuff
# should use os.path.join() but this works
os.putenv("LUA_PATH",  chdkptp_path + "lua/?.lua;;")
os.putenv("LUA_CPATH", chdkptp_path + "?.so;;")


child = pexpect.spawn(chdkptp_path + "chdkptp")
child.logfile = sys.stdout.buffer


child.expect('___> ')
child.sendline('c')
try:
    i = child.expect(['connected:','ERROR: no matching device'])
except:
    print("Exception was thrown: " + str(child))

print(i)

if i == 1:
    print("Connection error, bye!")
    child.sendline('quit')
    time.sleep(1)
    exit()
    
child.expect('con')


# set to record mode. Will error if already in rec mode but shruggie.
child.sendline("rec")
child.expect('con')

# set RESOLUTION 
child.sendline("=set_prop(require(\"propcase\").RESOLUTION, " + str(RESOLUTION) + ")") 
child.expect('con')


# attempt to turn OFF ALL LIGHT
child.sendline("=set_lcd_display(0)") 
child.expect('con')


datestr = time.strftime("%Y%m%d-%H%M%S") #20120515-155045
dest_path = os.path.join(img_root, datestr)
if not os.path.exists(dest_path):
    print("creating jpg dir " + dest_path)
    os.mkdir(dest_path)

# make semaphore file
open(semaphore_fn, 'a').close()
time.sleep(1)
print("loop started at" + str(datetime.datetime.now()))


# child.sendline("=return get_focus()") 
# child.expect('con')


imcount = 0
# run forever and wait to be killed by cronjob.
# a cleaner way is to trap a "kill -15" signal or semaphore...
while os.path.exists(semaphore_fn): 
    sys.stdout.flush()
    remote_path = os.path.join(dest_path, "img_{:05}".format(imcount))
    print("sending remoteshoot at " + str(datetime.datetime.now()))
    child.sendline("remoteshoot " + remote_path)
    try:
        child.expect('con')
    except Exception as exc:
        print("Exception was thrown: " + str(child))
        gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", "Server Error", "Exception: " + exc + "--- " + str(child))
        child.sendline('quit')
        time.sleep(1)
        exit()
    
    #TODO: check errors here
    imcount +=1
    time.sleep(INTERVAL)


# ok here we are done with the loop. Turn off the backlight.
print("loop ended at " + str(datetime.datetime.now()))


# wait for last download to finish
time.sleep(10)


# turn OFF ALL LIGHT
child.sendline("play")
child.expect('con')

child.sendline("=set_backlight(0)") 
child.expect('con')
child.sendline("=set_lcd_display(0)") 
child.expect('con')
child.sendline("=set_led(4,0)") 
child.expect('con')


child.sendline("quit")
time.sleep(1)
child.terminate()
child.wait()

print("job finished at " + str(datetime.datetime.now()))
sys.stdout.flush()

exit()
