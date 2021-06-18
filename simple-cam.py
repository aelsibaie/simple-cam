import subprocess
import os
import time
import datetime
import sys
import gmail

# 0=L, 1=M1, 2=M2, 3=M3, 4=S, 5=RAW
RESOLUTION = 4

# interval between photos in seconds
INTERVAL = 5

# path to the root of directory to store jpgs for timelapse processing.
# a subdirectory is created with the current date and images are moved there
# with sequential numbers for ffmpeg timelapse generation
img_root = "/home/pi/pictures"

# check for the existence of this file. When it's deleted stop
# the capture loop. This is how the movie generation process stops
# the image generation process
semaphore_fn = "/home/pi/running.txt"





datestr = time.strftime("%Y%m%d-%H%M%S") #20120515-155045
dest_path = os.path.join(img_root, datestr)
if not os.path.exists(dest_path):
    print("creating jpg dir " + dest_path)
    os.mkdir(dest_path)

# make semaphore file
open(semaphore_fn, 'a').close()
time.sleep(1)
print("loop started at" + str(datetime.datetime.now()))


imcount = 0
# run forever and wait to be killed by cronjob.
# a cleaner way is to trap a "kill -15" signal or semaphore...
while os.path.exists(semaphore_fn): 
    sys.stdout.flush()
    remote_path = os.path.join(dest_path, "img_{:05}.jpg".format(imcount))
    print("sending remoteshoot at " + str(datetime.datetime.now()))
    subprocess.run(["fswebcam", "-r", "1280x960", "--no-banner", remote_path])
    imcount +=1
    time.sleep(INTERVAL)


# ok here we are done with the loop. Turn off the backlight.
print("loop ended at " + str(datetime.datetime.now()))

# wait for last download to finish
time.sleep(10)

print("job finished at " + str(datetime.datetime.now()))
sys.stdout.flush()

exit()
