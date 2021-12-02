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

statesBefore = {}
async def changeStates(uri, state):
    async with websockets.connect(uri) as websocket:
        for k in state:
            if k != 'type':
                if ((k == '2' or k == '3' or k == '4' or k == '14' or k == '18' or k == '15' or k == '17') and state[k] == False) or (k != '2' and k != '3' and k != '4' and k != '14' and k != '18' and k != '15' and k != '17' and state[k] == True):
                    await websocket.send(json.dumps({'pin': int(k)}, indent='\t'))

async def turnOnTurnOff(uri):
    async with websockets.connect(uri) as websocket:
        global statesBefore
        message = await websocket.recv()
        statesBefore = json.loads(message)
        await changeStates(uri, statesBefore)


async def startAlarm(uri, prefix):
    async with websockets.connect(uri) as websocket:

        global alarmTone
        global index
        alarms = ['spotify:track:642phU4GOkBtnFkPnPS3O8', 'spotify:track:4oiEefH8ARkVTiB9GGrRqq', 'spotify:track:23Jjn06Bc0hhXd7J3bJlws', 'spotify:track:5bqEngtIzgQJU8cI4AVUKV', 'spotify:track:3h768eRbPl89qLMahvA3G3', 'spotify:track:3KliIkBn8SLZoe5E2tmtbP']
        alarmTone = random.choice(alarms)
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
        await websocket.recv()
        # await websocket.send(json.dumps({"method":"core.tracklist.clear","jsonrpc":"2.0","id":73}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({
            "method": "core.tracklist.add",
            "params": {
                "uri": alarmTone,
                "at_position": index
            },
            "jsonrpc": "2.0",
            "id": 245
        }, indent='\t'))

        while 'id' not in data or data['id'] != 245:
            message = await websocket.recv()
            data = json.loads(message)

        lenght = data['result'][0]['track']['length']
        tlid = data['result'][0]['tlid']



        await websocket.send(json.dumps({"method":"core.playback.next","jsonrpc":"2.0","id":87}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))

        time.sleep(lenght/1000)
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
        await websocket.send(json.dumps({
            "method": "core.playback.next",
            "jsonrpc": "2.0",
            "id": 555
        }, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))

asyncio.get_event_loop().run_until_complete(
    turnOnTurnOff('ws://192.168.1.12:8899'))

asyncio.get_event_loop().run_until_complete(
    startAlarm('ws://192.168.1.12:6680/mopidy/ws', '1_'))

asyncio.get_event_loop().run_until_complete(
    changeStates('ws://192.168.1.12:8899', statesBefore))
