import subprocess
import os
import time
import datetime
import shutil
import socket
import logging
from logging.handlers import RotatingFileHandler

#logging.basicConfig(filename='simple-cam.log', level=logging.DEBUG)
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("simple-cam.log", maxBytes=1000000, backupCount=1)
logger.addHandler(handler)


RESOLUTION = "1920x1080"
SCALE_TOGGLE = False
SCALE = "960x540"
BRIGHTNESS = "brightness=50%"
CONTRAST = "contrast=50%"
SATURATION= "saturation=50%"
HUE = "hue=50%"

# warn the user if HDD space falls below this % (free/total)
HDD_SPACE_THRESHOLD = 5

# interval between photos in seconds
INTERVAL = 2*60

# path to the root of directory to store jpgs for timelapse processing.
# a subdirectory is created with the current date and images are moved there
# with sequential numbers for ffmpeg timelapse generation
img_root = "/home/pi/pictures"

# check for the existence of this file. When it's deleted stop
# the capture loop. This is how the movie generation process stops
# the image generation process
semaphore_fn = "/home/pi/simple-cam/running.txt"


def email_error_report(error_str):
    os.remove(semaphore_fn)
    logger.critical(error_str)
    logger.info("emailing report...")
    # wait to import because it takes a long time and is only needed for errors
    # import gmail
    # gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", "simple-cam.py Critical Error", error_str)
    exit()


if __name__ == "__main__":
    logger.info("starting simple-cam.py at " + str(datetime.datetime.now()))

    total, used, free = shutil.disk_usage("/")
    freep = free / total
    logger.debug("Total: %d GiB" % (total // (2**30)))
    logger.debug("Used: %d GiB" % (used // (2**30)))
    logger.debug("Free: %d GiB" % (free // (2**30)))

    if(freep < (HDD_SPACE_THRESHOLD / 100)):
        error_str = str(round((freep * 100), 2)) + "% remaining hard drive space too low on " + socket.gethostname()
        email_error_report(error_str)
    else:
        logger.info(str(round((freep * 100), 2)) + "% remaining hard drive space at acceptable levels")

    datestr = time.strftime("%Y%m%d-%H%M%S")  # 20120515-155045
    dest_path = os.path.join(img_root, datestr)
    if not os.path.exists(dest_path):
        logger.info("creating jpg dir " + dest_path)
        os.mkdir(dest_path)

    # make semaphore file
    open(semaphore_fn, 'a').close()
    time.sleep(1)
    logger.info("loop started at " + str(datetime.datetime.now()))

    imcount = 0
    # run forever and wait to be killed by cronjob.
    # a cleaner way is to trap a "kill -15" signal or semaphore...
    error_message = "No such file or directory"
    while os.path.exists(semaphore_fn):
        remote_path = os.path.join(dest_path, "img_{:05}.jpg".format(imcount))
        logger.info("sending remoteshoot at " + str(datetime.datetime.now()))
        if SCALE_TOGGLE == True:
            completed_process = subprocess.run(["fswebcam", "-r", RESOLUTION, "-S", "10", "--no-banner", "--set", BRIGHTNESS, "--set", CONTRAST, "--set", SATURATION, "--set", HUE, "--scale", SCALE, "--flip", "v", remote_path], capture_output=True)
        else:
            completed_process = subprocess.run(["fswebcam", "-r", RESOLUTION, "-S", "10", "--no-banner", "--set", BRIGHTNESS, "--set", CONTRAST, "--set", SATURATION, "--set", HUE, "--flip", "v", remote_path], capture_output=True)
        logger.debug(str(completed_process))
        if (completed_process.returncode != 0) or (error_message in str(completed_process.stderr)):
            email_error_report(str(completed_process))
        imcount += 1
        logger.info("remoteshoot success. sleeping " + str(INTERVAL) + " seconds starting at: " + str(datetime.datetime.now()))
        time.sleep(INTERVAL)

    # ok here we are done with the loop. Turn off the backlight.
    logger.info("loop ended at " + str(datetime.datetime.now()))

    # wait for last download to finish
    time.sleep(10)

    logger.info("job finished at " + str(datetime.datetime.now()))

    exit()
