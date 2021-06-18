import subprocess
import os
import time
import datetime
import sys
import shutil
import socket

#import gmail
#gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", "ErrorSubj", "ErrorBody")

RESOLUTION = "1280x960"

# warn the user if HDD space falls below this % (free/total)
HDD_SPACE_THRESHOLD = 95

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


def email_error_report(error_str):
    print("CRITICAL ERROR, EXITING...")
    print(error_str)
    print("emailing report...")
    import gmail
    gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", "simple-cam.py Critical Error", error_str)
    exit()

if __name__ == "__main__":
    total, used, free = shutil.disk_usage("/")

    print("Total: %d GiB" % (total // (2**30)))
    print("Used: %d GiB" % (used // (2**30)))
    print("Free: %d GiB" % (free // (2**30)))
    freep = free/total

    if(freep < (HDD_SPACE_THRESHOLD / 100)):
        error_str = str(round((freep*100), 2)) + "% remaining hard drive space too low on " + socket.gethostname()
        email_error_report(error_str)
    else:
        print(str(round((freep*100), 2)) + "% remaining hard drive space at acceptable levels")


    datestr = time.strftime("%Y%m%d-%H%M%S") #20120515-155045
    dest_path = os.path.join(img_root, datestr)
    if not os.path.exists(dest_path):
        print("creating jpg dir " + dest_path)
        os.mkdir(dest_path)

    # make semaphore file
    open(semaphore_fn, 'a').close()
    time.sleep(1)
    print("loop started at " + str(datetime.datetime.now()))

    imcount = 0
    # run forever and wait to be killed by cronjob.
    # a cleaner way is to trap a "kill -15" signal or semaphore...
    while os.path.exists(semaphore_fn): 
        sys.stdout.flush()
        remote_path = os.path.join(dest_path, "img_{:05}.jpg".format(imcount))
        print("sending remoteshoot at " + str(datetime.datetime.now()))
        completed_process = subprocess.run(["fswebcam", "-r", RESOLUTION, "--no-banner", remote_path], capture_output=True)
        print(completed_process)
        if completed_process.returncode != 0:
            print("bad news bears")
            exit()
        imcount +=1
        print("sleeping " + str(INTERVAL) + " seconds starting at: " + str(datetime.datetime.now()))
        time.sleep(INTERVAL)

    # ok here we are done with the loop. Turn off the backlight.
    print("loop ended at " + str(datetime.datetime.now()))

    # wait for last download to finish
    time.sleep(10)

    print("job finished at " + str(datetime.datetime.now()))
    sys.stdout.flush()

    exit()
