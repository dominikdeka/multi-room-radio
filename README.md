**enable Network at Boot**
`sudo raspi-config`
System Options->Network at Boot (enabled)

**print temperature alias**
`alias temp='vcgencmd measure_temp'`

***install gpio listener***
`sudo pip3 install websockets`
add to /etc/rc.local
`/home/pi/salon-radio/start.sh &> /tmp/rc.local.log`

**install mopidy**
https://docs.mopidy.com/en/latest/installation/debian/#install-from-apt-mopidy-com
```
sudo adduser mopidy video
```

https://mopidy.com/ext/
```
sudo python3 -m pip install Mopidy-TuneIn
sudo python3 -m pip install Mopidy-YouTube
sudo python3 -m pip install youtube-dl
sudo python3 -m pip install Mopidy-Iris
sudo python3 -m pip install Mopidy-Mobile
sudo python3 -m pip install "git+https://github.com/mopidy/mopidy-soundcloud@master
sudo python3 -m pip install Mopidy-Tidal
sudo python3 -m pip install Mopidy-Local

sudo chmod 755 /media/pi
copy mopidy.conf to /etc/mopidy/
```
https://docs.mopidy.com/en/latest/running/service/

```
pi@raspberrypi:~ $ aplay -L
(...)
hdmi:CARD=vc4hdmi,DEV=0
    vc4-hdmi, MAI PCM i2s-hifi-0
    HDMI Audio Output
(...)
```
--->
```
pi@raspberrypi:~ $ sudo vi /etc/mopidy/mopidy.conf
[audio]
output = alsasink device=hdmi:vc4hdmi
```

***crontab***
use backuped crontab

***hdmi blink***
turn it off

***websockets***
add content of https://github.com/dominikdeka/multi-room-radio/blob/master/index.html to
/usr/local/lib/python2.7/dist-packages/mopidy_mobile/www/index.html

