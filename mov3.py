#!/usr/bin/python


# Python 3
#

# Given a top-level directory as argument, finds the most recent subdirectory.
# Finds all the img_nnnnn.jpg files in that directory, sorts them by filename,
# and creates a mp4 movie from them using ffmpeg. 
#
#
import sys
import os
import time
import subprocess


# local vars
output_dir = "/home/pi/timelapse"
input_dir = "/home/pi/pictures"

def all_subdirs_of(b='.'):
  result = []
  for d in os.listdir(b):
    bd = os.path.join(b, d)
    if os.path.isdir(bd): result.append(bd)
  return result
  


all_subdirs = all_subdirs_of(input_dir)
srcfolder = max((os.path.getmtime(f),f) for f in all_subdirs)[1]


froot =  os.path.basename(srcfolder)

print("working on directory " + srcfolder)
print("froot " + froot)



ffcall = ['ffmpeg']
ffcall.append('-r')
ffcall.append('18')
# doc: http://ffmpeg.org/ffmpeg.html#crop




#input files, of type 20160903200831.jpg
ffcall.append('-pattern_type')
ffcall.append('glob')
ffcall.append('-i')
#ffcall.append("'" + os.path.join(srcfolder, "img_?????.jpg") + "'")
ffcall.append(os.path.join(srcfolder, "img_?????.jpg"))
#ffcall.append(os.path.join(srcfolder, 'temp-%5d.jpg'))

# this crops out bright building lights at bottom of screen
#ffcall.append('-vf')
#ffcall.append('crop=4608:3456:309:185')
##ffcall.append('crop=1280:720:309:128')


# this deshakes
#x:y:w:h:rx:ry:edge:blocksize:contrast:search:filename

#ffcall.append('-vf')
#ffcall.append('deshake=-1:-1:-1:-1:16:16:0:8:100:1:shake.log,crop=1280:720:309:185')



# output quality
#ffcall.append('-q:v')
#ffcall.append('2')

# overwrite output
ffcall.append('-y')

#disable audio output
ffcall.append('-an')

#output file
vidfile = os.path.join(output_dir, froot+'.mp4')
ffcall.append(vidfile)
#ffcall.append('-s')
#ffcall.append('800x600')

print("starting movie script")
sys.stdout.flush()
#mencoder -mc 0 -noskip -skiplimit 0 -ovc lavc -lavcopts \
#  vcodec=mpeg4:vhq:trell:mbd=2:vmax_b_frames=1:v4mv:vb_strategy=0:vlelim=0:vcelim=0:cmp=6:subcmp=6:precmp=6:predia=3:dia=3:vme=4:vqscale=1 \
#  "mf://$tmpdir/*.jpg" -mf type=jpg:fps=$fps -o $output


# make the movie from the temp files
print(' '.join(ffcall))
sys.stdout.flush()
subprocess.call(ffcall,stdout=sys.stdout,stderr=sys.stderr)


# and upload it
#ftpcall = ['/home/jtf/cam/ftpscript.py',vidfile]
#print(' '.join(ftpcall))
#subprocess.call(ftpcall,stdout=sys.stdout,stderr=subprocess.STDOUT)

    

    
