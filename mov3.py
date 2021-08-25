import sys
import os
import subprocess

# local vars
output_dir = "/home/pi/timelapse"
input_dir = "/home/pi/pictures"


def all_subdirs_of(b='.'):
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        srcfolder = str(sys.argv[1]).rstrip("/")
    else:
        all_subdirs = all_subdirs_of(input_dir)
        srcfolder = max((os.path.getmtime(f), f) for f in all_subdirs)[1]

    froot = os.path.basename(srcfolder)

    print("working on directory " + srcfolder)
    print("froot " + froot)

    # doc: http://ffmpeg.org/ffmpeg.html
    ffcall = ['ffmpeg']

    ffcall.append('-r')
    ffcall.append('18')

    ffcall.append('-pattern_type')
    ffcall.append('glob')

    ffcall.append('-i')
    ffcall.append(os.path.join(srcfolder, "img_?????.jpg"))

    # overwrite output
    ffcall.append('-y')

    # disable audio output
    ffcall.append('-an')
    
    ffcall.append('-vf')
    ffcall.append('format=yuv420p')

    # output file
    vidfile = os.path.join(output_dir, froot + '.mp4')
    ffcall.append(vidfile)

    print("starting movie script")
    sys.stdout.flush()

    print(' '.join(ffcall))
    sys.stdout.flush()
    subprocess.call(ffcall, stdout=sys.stdout, stderr=sys.stderr)
