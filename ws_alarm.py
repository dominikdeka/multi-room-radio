#!/usr/bin/env python

import asyncio
import websockets
import random
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
                if ((k == '2' or k == '3' or k == '4' or k == '14' or k == '18' or k == '15' or k == '17') and data[k] == False) or (k != '2' and k != '3' and k != '4' and k != '14' and k != '18' and k != '15' and k != '17' and data[k] == True):
                    await websocket.send(json.dumps({'pin': int(k)}, indent='\t'))


async def startWakeup(uri, prefix):
    async with websockets.connect(uri) as websocket:

        global currentPlaylist
        previousPlaylistUri = ''
        alarms = ['spotify:track:642phU4GOkBtnFkPnPS3O8', 'spotify:track:4oiEefH8ARkVTiB9GGrRqq', 'spotify:track:23Jjn06Bc0hhXd7J3bJlws', 'spotify:track:5bqEngtIzgQJU8cI4AVUKV', 'spotify:track:3h768eRbPl89qLMahvA3G3', 'spotify:track:3KliIkBn8SLZoe5E2tmtbP']
        await websocket.send(json.dumps({"method":"core.mixer.set_volume","params":{"volume":100},"jsonrpc":"2.0","id":47}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.clear","jsonrpc":"2.0","id":73}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"method":"core.tracklist.add","params":{"uri":random.choice(alarms)},"jsonrpc":"2.0","id":87}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))


asyncio.get_event_loop().run_until_complete(
    turnOnTurnOff('ws://192.168.1.12:8899'))

asyncio.get_event_loop().run_until_complete(
    startWakeup('ws://192.168.1.12:6680/mopidy/ws', '1_'))
