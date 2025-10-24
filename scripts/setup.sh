#! /bin/bash

#########################################################
# FIRST TIME SETUP SCRIPT
# Use this the first time running on an Raspberry Pi.
# This may need to be ran more than once due to rebooting.
#########################################################

# Sync time forcefully
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

# update sources and gpg keyring
echo -e "Types: deb deb-src \n URIs: http://deb.debian.org/debian \nSuites: trixie trixie-updates \n Components: main non-free-firmware \n Signed-By: /etc/apt/trusted.gpg.d/debian-13.gpg" > /etc/apt/sources.list.d/rasp.sources
wget -O- https://ftp-master.debian.org/keys/archive-key-13.asc
gpg --dearmor archive-key-13.asc
mv archive-key-13.asc.gpg /etc/apt/trusted.gpg.d/debian-13.gpg
rm archive-key-13.asc archive-key-13.asc.gpg

# update system
apt update
apt full-upgrade
# rpi-update
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget dropbox

# enables dropbox on start
systemctl enable dropbox.service 
systemctl start dropbox.service

# download python
#wget https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tgz
#tar zxvf Python-3.13.7.tgz

# python build might not be necessary after sources + keyring change

# build and install
#cd Python-3.13.7
#./configure --enable-optimizations
#make altinstall
#cd ..
#rm -rf Python-3.13.7

# replace python program with updated version
#rm /usr/bin/python
#ln -s /usr/local/bin/python3.13 /usr/bin/python

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

# setup data directory
mkdir data
