#!/usr/bin/python3

# this is Python 3!

import os
import time
import datetime
import pexpect


# path to your chdkptp installation, including lua stuff
chdkptp_path = "/home/pi/chdkptp-r964/"


# tell chdkptp where to find its lua stuff
# should use os.path.join() but this works
os.putenv("LUA_PATH",  chdkptp_path + "lua/?.lua;;")
os.putenv("LUA_CPATH", chdkptp_path + "?.so;;")


child = pexpect.spawn(chdkptp_path + "chdkptp")
child.expect('___> ')

child.sendline('c')
try:
    i = child.expect(['connected:','ERROR: no matching device'])
except:
    print("Exception was thrown:")
    print("Exception was thrown: " + str(child))

print(i)
if i == 1:
    print("Connection error, bye!")
    child.sendline('quit')
    time.sleep(1)
    exit()
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

print("keepalive finished at " + str(datetime.datetime.now()))

exit()
