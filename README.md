# General
```
# updating system
sudo apt-get update && sudo apt-get upgrade

# install virtualenv
sudo apt-get install python3-virtualenv

# reboot
sudo reboot

# Enabling I2C
sudo raspi-config nonint do_i2c 0
    
# Enabling SPI
sudo raspi-config nonint do_spi 0

# Enabling Serial
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial 0

# Enabling SSH
sudo raspi-config nonint do_ssh 0

# Enabling Camera
sudo raspi-config nonint do_camera 0

# Disable raspi-config at Boot
sudo raspi-config nonint disable_raspi_config_at_boot 0

```

# OpenCV
## install with PIP
```
#in a virtualenv env
pip install opencv-contrib-python
```

## install with APT
```
# in a virtualenv env
sudo apt install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev \
libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev \
libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev \
libhdf5-serial-dev libhdf5-103 libqt5gui5 libqt5webkit5 libqt5test5 python3-pyqt5 python3-dev

pip3 install opencv-python
```

# Picamera2
## install
picamera 2 is already pre-installed.
For picamera2 to work in a virtualenv:
- the virtualenv needs to enable usage of global packages
- and numpy needs to be downgraded via ```pip install numpy==1.26.4```

## issue with QTGL preview
A bug appears when using QTGL preview.
Since the following works ```libcamera-hello --qt-preview```, we assume there's a pb of QT5 lib being used by picamera2. We thus need to add the below after cv2 import:
```
import os
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
```

## lib explained
- MappedArray gives access to image buffer (the in memory image)


# Face recognition
## install with PIP
```
# package requires to build dlib library whioch can be very long
# edit swap size to 1024 and restart process
sudo nano /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

# to verify change was made
free -m

# after reboot, install and wait
pip install face_recognition
```


# MQTT
## install

```
# install MQTT broker
brew install mosquitto

# install python libs
pip3 install paho-mqtt

# start broker service
brew services start mosquitto

# start a topic (in a window)
mosquitto_sub -t topic/state 

# send to topic (in another window)
mosquitto_pub -t topic/state -m "Hello World"
```


# I2C
## scan CLI

```
# scan i2c with
sudo i2cdetect -y 1

# --> it gives the address of the connected devices
```

## scan via python
```
from machine import I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time



def do_scan(which):
    i2c=I2C(which)
    print("I2C Configuration: "+str(i2c))
    devices = i2c.scan()
```


# Bluetooth
```
# get Bluetooth up and running 
sudo service bluetooth start

# enter bluetooth shell
sudo bluetoothctl

# configure
power on
pairable on
discoverable on
agent on
default-agent
quit

# scan
bluetoothctl scan on

# pairing
bluetoothctl pair 40:HR:32:46:GH:00
bluetoothctl trust 40:HR:32:46:GH:00
```

# OLED
connect OLED display directly on GPIO pins below:
- Vcc 3.3V
- GND
- SDA
- SCL

```
# pip3 install --upgrade adafruit-python-shell

# install OLED ssd1306 driver
pip3 install --upgrade adafruit-circuitpython-ssd1306

# Installing latest version of Blinka locally
sudo apt-get install -y i2c-tools libgpiod-dev python3-libgpiod
pip3 install --upgrade RPi.GPIO
pip3 install --upgrade adafruit-blinka

```


# ROS
## install

```
wget https://s3.ap-northeast-1.wasabisys.com/download-raw/dpkg/ros2-desktop/debian/bookworm/ros-jazzy-desktop-0.3.2_20240525_arm64.deb
sudo apt install ./ros-jazzy-desktop-0.3.2_20240525_arm64.deb
sudo pip install --break-system-packages vcstool colcon-common-extensions
source /opt/ros/${DISTRO}/setup.bash
```

## uninstall
```
sudo apt remove ros-${DISTRO}-desktop
```


