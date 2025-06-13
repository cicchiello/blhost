#!/usr/bin/env python

import time
import atexit

import pigpio 

def cleanup():
   pi.stop()

atexit.register(cleanup)

pi = pigpio.pi()

#Broadcom pin 25 is physical pin 22
pi.write(25, 1)
pi.write(25, 0)
time.sleep(0.01)
pi.write(25, 1)


