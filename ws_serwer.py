#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
import RPi.GPIO as GPIO

logging.basicConfig()

STATE_PINS = {2: False, 3: False, 4: False, 17: False, 27: False, 22: False, 9: False}

USERS = set()


GPIO.setmode(GPIO.BCM)
for k, v in STATE_PINS.items():
    GPIO.setup(k, GPIO.OUT)
    GPIO.output(k, v)

def state_event():
    return json.dumps({'type': 'state', **STATE_PINS})

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)

async def unregister(websocket):
    USERS.remove(websocket)

async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data['pin'] in list(STATE_PINS.keys()):
                STATE_PINS[data['pin']] = not STATE_PINS[data['pin']]
                GPIO.output(data['pin'], STATE_PINS[data['pin']])

                await notify_state()
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)

try:
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(counter, '192.168.1.12', 8765))
    asyncio.get_event_loop().run_forever()
finally:
    GPIO.cleanup()
