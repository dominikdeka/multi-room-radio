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
CHANGE_STATE_PINS = {
            21: {'lastStatus': 0, 'statusPin': 2},
            20: {'lastStatus': 0, 'statusPin': 3},
            16: {'lastStatus': 0, 'statusPin': 14},
            12: {'lastStatus': 0, 'statusPin': 4},
            5: {'lastStatus': 0, 'statusPin': 15},
            27: {'lastStatus': 0, 'statusPin': 18},
            23: {'lastStatus': 0, 'statusPin': 17},
            26: {'lastStatus': 0},
            19: {'lastStatus': 0},
            13: {'lastStatus': 0},
            6: {'lastStatus': 0},
            7: {'lastStatus': 0},
            22: {'lastStatus': 0},
            24: {'lastStatus': 0},
            10: {'lastStatus': 0},
            25: {'lastStatus': 0},
            9: {'lastStatus': 0},
            8: {'lastStatus': 0},
            11: {'lastStatus': 0}
            }

GPIO.setmode(GPIO.BCM)

for k, v in CHANGE_STATE_PINS.items():
    GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

currentPlaylist = {}
stateBeforeMic = ''

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

async def playnext(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.next"}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))

async def playprevious(uri):
    async with websockets.connect(uri) as websocket:
#        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.previous"}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))

async def repeat(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": True}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))

async def pause(uri):
    async with websockets.connect(uri) as websocket:
        global stateBeforeMic
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"}, indent='\t'))
        message = await websocket.recv()
        data = json.loads(message)

        stateBeforeMic = data['result']

        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.pause"}, indent='\t'))


async def play(uri):
    global stateBeforeMic
    if stateBeforeMic == 'playing':
        async with websockets.connect(uri) as websocket:
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
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_random", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_single", "params": {"value": False}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.set_repeat", "params": {"value": True}}, indent='\t'))
        await websocket.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "core.playback.play"}, indent='\t'))



try:
    while True:
        for k, v in CHANGE_STATE_PINS.items():
            pin_status = GPIO.input(k)
            global microphone
            if v['lastStatus'] == 0 and pin_status == 1 and k == 7:
                    asyncio.get_event_loop().run_until_complete(
                                            pause('ws://192.168.1.12:6680/mopidy/ws'))
                    microphone = subprocess.Popen('arecord -D plughw:1,0 |  aplay', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            if v['lastStatus'] == 1 and pin_status == 0:
                if k == 26:
                    asyncio.get_event_loop().run_until_complete(
                        playpause('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 24:
                    asyncio.get_event_loop().run_until_complete(
                        playnext('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 10:
                    asyncio.get_event_loop().run_until_complete(
                        repeat('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 25:
                    asyncio.get_event_loop().run_until_complete(
                        playprevious('ws://192.168.1.12:6680/mopidy/ws'))
                elif k == 19:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '1_'))
                elif k == 13:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '2_'))
                elif k == 6:
                    asyncio.get_event_loop().run_until_complete(
                        jumpplaylists('ws://192.168.1.12:6680/mopidy/ws', '3_'))
                elif k == 7:
                    #microphone
                    if microphone.poll() == None:
                        asyncio.get_event_loop().run_until_complete(
                                                play('ws://192.168.1.12:6680/mopidy/ws'))
                        os.killpg(os.getpgid(microphone.pid), signal.SIGTERM)
#                    microphone.kill()
                elif k == 22:
                    os.system('sudo reboot')
                else:
                    asyncio.get_event_loop().run_until_complete(
                        changestate('ws://192.168.1.12:8899', v['statusPin']))
            CHANGE_STATE_PINS[k]['lastStatus'] = pin_status
        time.sleep(0.1)
finally:
    GPIO.cleanup()

