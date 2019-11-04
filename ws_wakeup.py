#!/usr/bin/env python

import asyncio
import websockets

import RPi.GPIO as GPIO
import time
import json
import os
import signal
import subprocess


async def turnOnTurnOff(uri):
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        data = json.loads(message)
        print(data)
        for k in data:
            if k != 'type':
                if ((k == '2' or k == '4' or k == '17') and data[k] == False) or (k != '2' and k != '4' and k != '17' and data[k] == True):
                    await websocket.send(json.dumps({'pin': int(k)}, indent='\t'))


async def startWakeup(uri, prefix):
    async with websockets.connect(uri) as websocket:

        global currentPlaylist
        previousPlaylistUri = ''

        await websocket.send(json.dumps({"method":"core.mixer.set_volume","params":{"volume":100},"jsonrpc":"2.0","id":47}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.clear","jsonrpc":"2.0","id":73}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.add","params":{"uri":"local:track:muzyka%20dla%20dzieci/budzenie/mix2.mp4"},"jsonrpc":"2.0","id":87}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))


asyncio.get_event_loop().run_until_complete(
    turnOnTurnOff('ws://192.168.1.12:8899'))

asyncio.get_event_loop().run_until_complete(
    startWakeup('ws://192.168.1.12:6680/mopidy/ws', '1_'))
