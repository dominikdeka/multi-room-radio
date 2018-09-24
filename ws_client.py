#!/usr/bin/env python

import asyncio
import websockets

import RPi.GPIO as GPIO
import time
import json
import os
import signal
import subprocess

# Pin In Number
CHANGE_STATE_PINS = {15: {'lastStatus': 0}, 24: {'lastStatus': 0}, 25: {'lastStatus': 0}, 7: {'lastStatus': 0}, 6: {'lastStatus': 0}, 19: {'lastStatus': 0}, 14: {'lastStatus': 0, 'statusPin': 2}, 18: {'lastStatus': 0, 'statusPin': 3}, 10: {'lastStatus': 0, 'statusPin': 4}, 8: {'lastStatus': 0, 'statusPin': 17}, 5: {'lastStatus': 0, 'statusPin':27}, 13: {'lastStatus': 0, 'statusPin': 22}, 26: {'lastStatus': 0, 'statusPin': 9}}

GPIO.setmode(GPIO.BCM)

for k, v in CHANGE_STATE_PINS.items():
    GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

currentPlaylist = {}


async def changestate(uri, pin):
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


async def jumpplaylists(uri, prefix):
    async with websockets.connect(uri) as websocket:

        global currentPlaylist
        previousPlaylistUri = ''

        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playlists.as_list"}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)
        result = [k for k in data['result'] if k['name'].startswith(prefix)]
        if currentPlaylist == {} or prefix not in currentPlaylist['name']:
            currentPlaylist = result[0]
        else:
            for v in result:
                if previousPlaylistUri == currentPlaylist['uri']:
                    currentPlaylist = v
                    break
                else:
                    previousPlaylistUri = v['uri']

            if currentPlaylist['uri'] == previousPlaylistUri:
                currentPlaylist = result[0]
        print(currentPlaylist)
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playlists.get_items", "params": {"uri": currentPlaylist['uri']}}, indent='\t'))
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
            global microphone
            if v['lastStatus'] == 0 and pin_status == 1 and k == 6:
                    microphone = subprocess.Popen('arecord -D plughw:1,0 |  aplay', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            if v['lastStatus'] == 1 and pin_status == 0:
                if k == 15:
                    asyncio.get_event_loop().run_until_complete(
                        playpause('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 24:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '1_'))
                elif k == 25:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '2_'))
                elif k == 7:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '3_'))
                elif k == 6:
                    #microphone
                    print('kill him')
                    if microphone.poll() == None:
                        os.killpg(os.getpgid(microphone.pid), signal.SIGTERM)
#                    microphone.kill()
                elif k == 19:
                    os.system('sudo reboot')
                else:
                    asyncio.get_event_loop().run_until_complete(
                        changestate('ws://192.168.1.12  :8899', v['statusPin']))
            CHANGE_STATE_PINS[k]['lastStatus'] = pin_status
        time.sleep(0.1)
finally:
    GPIO.cleanup()

