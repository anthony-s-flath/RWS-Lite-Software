#! /bin/bash

#########################################################
# FIRST TIME SETUP SCRIPT ON UPDATED RASPBERRY PI.
# Version >= 13
# Use this the first time running rws on an Raspberry Pi.
#########################################################

# Sync time forcefully
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"


# update system
apt update
apt full-upgrade
# rpi-update
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget dropbox

# enables dropbox on start
systemctl enable dropbox.service 
systemctl start dropbox.service


# update pip
python -m pip install --upgrade pip

# setup virtual environment
python -m venv env
source env/bin/activate

pigpiod # this might need to be restarted every reboot

pip install -r requirements.txt
pip install -e .

# add w1thermsesnor to config
echo "dtoverlay=w1-gpio" >> /boot/config.txt
# add i2c (this might not be needed)
echo "dtparam=i2c1=on" >> /boot/config.txt"

# setup data directory
mkdir data
