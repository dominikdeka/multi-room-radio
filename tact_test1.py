#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import os
import time
import shlex
import subprocess

# Pin In Number
PIN = 14
# Pin Out Number
PIN_OUT = 18 
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_OUT, GPIO.OUT)
last_pin_status = 0


state = False
GPIO.output(PIN_OUT, state)
try: 
    while True:
    	pin_status = GPIO.input(PIN)
    	if last_pin_status == 1 and pin_status == 0:
    	    state = not state
	    GPIO.output(PIN_OUT, state)

    	last_pin_status = pin_status
    	time.sleep(0.1)
finally:  
    GPIO.cleanup()

