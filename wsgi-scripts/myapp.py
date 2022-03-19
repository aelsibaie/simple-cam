
import os
import io
from PIL import Image, ImageDraw
from flask import Flask, send_file, request


app = Flask(__name__)


# path to the root of directory to store jpgs for timelapse processing.
# a subdirectory is created with the current date and images are moved there
# with sequential numbers for ffmpeg timelapse generation
img_root = "/home/pi/pictures"




def all_subdirs_of(b='.'):
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result


@app.route("/")
def get_gif():
    all_subdirs = all_subdirs_of(img_root)
    srcfolder = max((os.path.getmtime(f), f) for f in all_subdirs)[1]
    ## start daily report section
    my_list = sorted(os.listdir(srcfolder))
    SPLIT = 20
    indexes = []
    for i in range(SPLIT - 1):
        indexes.append(int((len(my_list) / 20) * (i + 1)))
    frames = []
    for index in indexes:
        #myImage = Image.open(os.path.join(srcfolder, my_list[index])).resize((320,180))
        myImage = Image.open(os.path.join(srcfolder, my_list[index]))
        myDrawing = ImageDraw.Draw(myImage)
        myDrawing.text((28, 36), my_list[index][4:-4], fill=(255, 0, 0))
        frames.append(myImage)
    gif_io = io.BytesIO()

    frames[0].save(gif_io, format="GIF", append_images=frames, save_all=True, duration=5000/(SPLIT-1), loop=0, )
    gif_io.seek(0)
    return send_file(gif_io, mimetype='image/gif')



