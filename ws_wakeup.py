#!/usr/bin/env python

import asyncio
import websockets
import sys

import RPi.GPIO as GPIO
import time
import json
import os
import signal
import subprocess

ROOMS_PINS = {'1':'2','2':'3','3':'14','4':'4','5':'15','6':'18','7':'17'}
ALARMS_LIST = {
    '1': 'muzyka%20dla%20dzieci/budzenie/mix.mp3',
    '2': 'muzyka%20dla%20dzieci/budzenie/mix2.mp4',
    '3': 'muzyka%20dla%20dzieci/budzenie/mix3.mp3',
    '4': 'muzyka%20dla%20dzieci/budzenie/mix4.mp3',
    '5': 'muzyka%20dla%20dzieci/budzenie/mix5.mp3'}

async def turnOnTurnOff(uri):
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        data = json.loads(message)
        pins = []
        if len(sys.argv) > 2:
            for index in range(len(sys.argv)-2):
                pins.append(ROOMS_PINS[sys.argv[index+2]])
        else:
            pins = ['2','14','4','18']
        print ('Pins:', pins)
        for k in data:
            if k != 'type':
                if (pins.count(k)>0 and data[k] == False) or (pins.count(k) == 0 and data[k] == True):
                    await websocket.send(json.dumps({'pin': int(k)}, indent='\t'))


async def startWakeup(uri):
    async with websockets.connect(uri) as websocket:

        global currentPlaylist
        previousPlaylistUri = ''
        alarm = ALARMS_LIST['5']
        if len(sys.argv) > 1:
            alarm = ALARMS_LIST[sys.argv[1]]
        print('Alarm', alarm)

        await websocket.send(json.dumps({"method":"core.mixer.set_volume","params":{"volume":100},"jsonrpc":"2.0","id":47}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.clear","jsonrpc":"2.0","id":73}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.add","params":{"uri":"local:track:" + alarm},"jsonrpc":"2.0","id":87}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))


asyncio.get_event_loop().run_until_complete(
    turnOnTurnOff('ws://192.168.1.12:8899'))

asyncio.get_event_loop().run_until_complete(
    startWakeup('ws://192.168.1.12:6680/mopidy/ws'))
