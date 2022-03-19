import subprocess
import os
import time
import datetime
import shutil
import socket
import logging

logging.basicConfig(filename='simple-cam.log', level=logging.DEBUG)

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
    logging.critical(error_str)
    logging.info("emailing report...")
    # wait to import because it takes a long time and is only needed for errors
    import gmail
    gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", "simple-cam.py Critical Error", error_str)
    exit()


if __name__ == "__main__":
    logging.info("starting simple-cam.py at " + str(datetime.datetime.now()))

    total, used, free = shutil.disk_usage("/")
    freep = free / total
    logging.debug("Total: %d GiB" % (total // (2**30)))
    logging.debug("Used: %d GiB" % (used // (2**30)))
    logging.debug("Free: %d GiB" % (free // (2**30)))

    if(freep < (HDD_SPACE_THRESHOLD / 100)):
        error_str = str(round((freep * 100), 2)) + "% remaining hard drive space too low on " + socket.gethostname()
        email_error_report(error_str)
    else:
        logging.info(str(round((freep * 100), 2)) + "% remaining hard drive space at acceptable levels")

    datestr = time.strftime("%Y%m%d-%H%M%S")  # 20120515-155045
    dest_path = os.path.join(img_root, datestr)
    if not os.path.exists(dest_path):
        logging.info("creating jpg dir " + dest_path)
        os.mkdir(dest_path)

    # make semaphore file
    open(semaphore_fn, 'a').close()
    time.sleep(1)
    logging.info("loop started at " + str(datetime.datetime.now()))

    imcount = 0
    # run forever and wait to be killed by cronjob.
    # a cleaner way is to trap a "kill -15" signal or semaphore...
    error_message = "No such file or directory"
    while os.path.exists(semaphore_fn):
        remote_path = os.path.join(dest_path, "img_{:05}.jpg".format(imcount))
        logging.info("sending remoteshoot at " + str(datetime.datetime.now()))
        if SCALE_TOGGLE == True:
            completed_process = subprocess.run(["fswebcam", "-r", RESOLUTION, "--no-banner", "--set", BRIGHTNESS, "--set", CONTRAST, "--set", SATURATION, "--set", HUE, "--scale", SCALE, remote_path], capture_output=True)
        else:
            completed_process = subprocess.run(["fswebcam", "-r", RESOLUTION, "--no-banner", "--set", BRIGHTNESS, "--set", CONTRAST, "--set", SATURATION, "--set", HUE, remote_path], capture_output=True)
        logging.debug(str(completed_process))
        if (completed_process.returncode != 0) or (error_message in str(completed_process.stderr)):
            email_error_report(str(completed_process))
        imcount += 1
        logging.info("remoteshoot success. sleeping " + str(INTERVAL) + " seconds starting at: " + str(datetime.datetime.now()))
        time.sleep(INTERVAL)

    # ok here we are done with the loop. Turn off the backlight.
    logging.info("loop ended at " + str(datetime.datetime.now()))

    # wait for last download to finish
    time.sleep(10)
    
    
    logging.info("starting daily report at " + str(datetime.datetime.now()))
    ## start daily report section
    my_list = sorted(os.listdir(dest_path))
    SPLIT = 20
    indexes = []
    for i in range(SPLIT - 1):
        indexes.append(int((len(my_list) / 20) * (i + 1)))

    logging.info("making gif at " + str(datetime.datetime.now()))    
    from PIL import Image, ImageDraw
    frames = []
    for index in indexes:
        myImage = Image.open(os.path.join(dest_path, my_list[index])).resize((320,180))
        myDrawing = ImageDraw.Draw(myImage)
        myDrawing.text((28, 36), my_list[index][4:-4], fill=(255, 0, 0))

        frames.append(myImage)

    frames[0].save("daily_summary.gif", format="GIF", append_images=frames, save_all=True, duration=5000/(SPLIT-1), loop=0, )
    
    logging.info("emailing summary at " + str(datetime.datetime.now()))    
    import gmail
    today = datetime.date.today()
    subj = "simple-cam.py Daily Report - {:%d, %b %Y}".format(today)

    body = ""
    body += "Remaining hard drive space: " + str(round(freep*100, 2)) + "%\n"
    body += "Minimum required hard drive space: " + str(HDD_SPACE_THRESHOLD) + "%\n\n"
    body = body + ("Total: %d GiB\n" % (total // (2**30)))
    body = body + ("Used: %d GiB\n" % (used // (2**30)))
    body = body + ("Free: %d GiB" % (free // (2**30)))
    
    gmail.send_message(gmail.service, "amir.elsibaie@gmail.com", subj, body, attachments=["/home/pi/simple-cam/daily_summary.gif"])


    logging.info("job finished at " + str(datetime.datetime.now()))

    exit()
