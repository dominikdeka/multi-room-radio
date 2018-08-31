#!/bin/sh
sleep 10
cd /home/pi/python_scripts/multi-room-radio/
sudo python3.6 ws_serwer.py &
sudo python3.6 ws_client.py &