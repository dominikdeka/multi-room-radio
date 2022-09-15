#!/bin/sh
cd /home/pi/python_scripts/multi-room-radio/
while ! ifconfig | grep -F "192.168.1." > /dev/null; do sleep 1; done
date >> state.txt
cat /sys/class/net/eth0/operstate >> state.txt
python3.9 ws_serwer.py &
python3.9 ws_client.py &
