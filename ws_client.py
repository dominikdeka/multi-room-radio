#!/usr/bin/env python

import asyncio
import websockets

import RPi.GPIO as GPIO
import time
import json

# Pin In Number
CHANGE_STATE_PINS = {14: {'lastStatus': 0, 'statusPin': 2}, 18: {'lastStatus': 0, 'statusPin': 3}, 10: {'lastStatus': 0, 'statusPin': 4}, 8: {'lastStatus': 0, 'statusPin': 17}, 5: {'lastStatus': 0, 'statusPin':27}, 13: {'lastStatus': 0, 'statusPin': 22}, 26: {'lastStatus': 0, 'statusPin': 9}}

GPIO.setmode(GPIO.BCM)

for k, v in CHANGE_STATE_PINS.items():
    GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


async def changeStateReq(uri, pin):
    async with websockets.connect(uri) as websocket:
        print(json.dumps({'pin': pin}, indent='\t'))
        await websocket.send(json.dumps({'pin': pin}, indent='\t'))

try:
    while True:
        for k, v in CHANGE_STATE_PINS.items():
            pin_status = GPIO.input(k)
            if v['lastStatus'] == 1 and pin_status == 0:
                asyncio.get_event_loop().run_until_complete(
                    changeStateReq('ws://192.168.1.12:8765', v['statusPin']))
            CHANGE_STATE_PINS[k]['lastStatus'] = pin_status
        time.sleep(0.1)
finally:
    GPIO.cleanup()

