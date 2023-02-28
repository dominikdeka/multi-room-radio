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
    '1': 'file:///media/pi/KINGSTON/muzyka%20dla%20dzieci/budzenie/mix.mp3',
    '2': 'file:///media/pi/KINGSTON/muzyka%20dla%20dzieci/budzenie/mix2c.mp3',
    '3': 'file:///media/pi/KINGSTON/muzyka%20dla%20dzieci/budzenie/mix3b.mp3',
    '4': 'file:///media/pi/KINGSTON/muzyka%20dla%20dzieci/budzenie/mix4.mp3',
    '5': 'file:///media/pi/KINGSTON/muzyka%20dla%20dzieci/budzenie/budzenie5.mp3',
    '6': 'https://stream.rcs.revma.com/ye5kghkgcm0uv',
    '7': 'https://stream.rcs.revma.com/ypqt40u0x1zuv'}
statesBefore = {}

async def changeStates(uri, state):
    async with websockets.connect(uri) as websocket:
        pins = []
        if len(sys.argv) > 2:
            for index in range(len(sys.argv)-2):
                pins.append(ROOMS_PINS[sys.argv[index+2]])
        else:
            pins = ['2','14','4','18']
        for k in statesBefore:
            if k != 'type':
                if (pins.count(k)>0 and statesBefore[k] == False) or (pins.count(k) == 0 and statesBefore[k] == True):
                    await websocket.send(json.dumps({'pin': int(k)}, indent='\t'))

async def turnOnTurnOff(uri):
    async with websockets.connect(uri) as websocket:
        global statesBefore
        message = await websocket.recv()
        statesBefore = json.loads(message)
        await changeStates(uri, statesBefore)


async def startWakeup(uri):
    async with websockets.connect(uri) as websocket:
        global index
        global currentPlaylist
        alarm = ALARMS_LIST['5']
        if len(sys.argv) > 1:
            alarm = ALARMS_LIST[sys.argv[1]]


        await websocket.send(json.dumps({"method": "core.playback.get_current_tl_track","jsonrpc": "2.0","id": 39}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)
        if data['result'] == None:
            index = 0
        else:
            await websocket.send(json.dumps({"method": "core.tracklist.index","jsonrpc": "2.0","id": 217}, indent='\t'))
            message = await websocket.recv()
            data = json.loads(message)
            index = data['result'] + 1

        await websocket.send(json.dumps({"method":"core.mixer.set_volume","params":{"volume":100},"jsonrpc":"2.0","id":47}, indent='\t'))
        # await websocket.send(json.dumps({"method":"core.tracklist.clear","jsonrpc":"2.0","id":73}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({
            "method": "core.tracklist.add",
            "params": {
                "uris": [alarm],
                "at_position": index
            },
            "jsonrpc": "2.0",
            "id": 245
        }, indent='\t'))

        while 'id' not in data or data['id'] != 245:
            message = await websocket.recv()
            data = json.loads(message)

        await websocket.send(json.dumps({"method":"core.playback.next","jsonrpc":"2.0","id":87}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))
        if 'length' in data['result'][0]['track']:
            lenght = data['result'][0]['track']['length']
            print('lenght', lenght)
            tlid = data['result'][0]['tlid']
            time.sleep(lenght/1000)
            await websocket.send(json.dumps({
                "method": "core.playback.next",
                "jsonrpc": "2.0",
                "id": 555
            }, indent='\t'))
            await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))
            await websocket.send(json.dumps({
                "method": "core.tracklist.remove",
                "params": {
                    "criteria": {
                        "tlid": [
                            tlid
                        ]
                    }
                },
                "jsonrpc": "2.0",
                "id": 465
            }, indent='\t'))

asyncio.get_event_loop().run_until_complete(
    turnOnTurnOff('ws://192.168.1.12:8899'))

asyncio.get_event_loop().run_until_complete(
    startWakeup('ws://192.168.1.12:6680/mopidy/ws'))

if sys.argv[1] != '6' and sys.argv[1] != '7':
    asyncio.get_event_loop().run_until_complete(
        changeStates('ws://192.168.1.12:8899', statesBefore))
