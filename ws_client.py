#!/usr/bin/env python

import asyncio
import websockets

import RPi.GPIO as GPIO
import time
import json
import os

# Pin In Number
CHANGE_STATE_PINS = {15: {'lastStatus': 0}, 24: {'lastStatus': 0}, 25: {'lastStatus': 0}, 7: {'lastStatus': 0}, 6: {'lastStatus': 0}, 19: {'lastStatus': 0}, 14: {'lastStatus': 0, 'statusPin': 2}, 18: {'lastStatus': 0, 'statusPin': 3}, 10: {'lastStatus': 0, 'statusPin': 4}, 8: {'lastStatus': 0, 'statusPin': 17}, 5: {'lastStatus': 0, 'statusPin':27}, 13: {'lastStatus': 0, 'statusPin': 22}, 26: {'lastStatus': 0, 'statusPin': 9}}

GPIO.setmode(GPIO.BCM)

for k, v in CHANGE_STATE_PINS.items():
    GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

currentPlaylistUri = ''


async def changeStateReq(uri, pin):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'pin': pin}, indent='\t'))

async def playpause(uri):
    async with websockets.connect(uri) as websocket:

        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)

        if data['result'] == 'playing':
            await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.pause"}, indent='\t'))
        else:
            await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))

async def jumpplaylists(uri):
    async with websockets.connect(uri) as websocket:

        global currentPlaylistUri
        previousPlaylistUri = ''

        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playlists.as_list"}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)

        if currentPlaylistUri == '':
            currentPlaylistUri = data['result'][0]['uri']
        else:
            for v in data['result']:
                if previousPlaylistUri == currentPlaylistUri:
                    currentPlaylistUri = v['uri']
                    break
                else:
                    previousPlaylistUri = v['uri']

            if currentPlaylistUri == previousPlaylistUri:
                currentPlaylistUri = data['result'][0]['uri']
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playlists.get_items", "params": {"uri": currentPlaylistUri}}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)
        uris = []
        for v in data['result']:
            uris.append(v['uri'])
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.clear"}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.add", "params": {"uris": uris}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": True}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))


try:
    while True:
        for k, v in CHANGE_STATE_PINS.items():
            pin_status = GPIO.input(k)
            if v['lastStatus'] == 1 and pin_status == 0:
                if k == 15:
                    asyncio.get_event_loop().run_until_complete(
                        playpause('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 24:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 25:
                    print('25')
                elif k == 7:
                    print('7')
                elif k == 6:
                    print('6')
                    #microphone
                elif k == 19:
                    os.system('sudo reboot')
                else:
                    asyncio.get_event_loop().run_until_complete(
                        changeStateReq('ws://192.168.1.12:8765', v['statusPin']))
            CHANGE_STATE_PINS[k]['lastStatus'] = pin_status
        time.sleep(0.1)
finally:
    GPIO.cleanup()

