import sys
import os
import subprocess

# local vars
LIMIT = 30 * 1e+9 # 30gb
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


    ffcall.append('-c:v')
    ffcall.append('libx264')

    ffcall.append('-crf')
    ffcall.append('17')


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
    completed_process = subprocess.run(ffcall, stdout=sys.stdout, stderr=sys.stderr)

    if (completed_process.returncode != 0):
        print("ffmpeg failed, keeping pictures")
    else:
        print("ffmpeg worked, deleting old pictures")
        subprocess.run(['rm', '-rf', srcfolder])

    size = 0
    for ele in os.scandir(output_dir):
        size += os.path.getsize(ele)

    while size > LIMIT:
        oldest_file = sorted([ "/home/pi/timelapse/"+f for f in os.listdir("/home/pi/timelapse/")], key=os.path.getctime)[0]
        print("removing oldest file", oldest_file)
        os.remove(oldest_file)
        size = 0
        for ele in os.scandir(output_dir):
            size += os.path.getsize(ele)


    print(size)

    print("finished processing timelapse")
