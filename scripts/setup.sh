#! /bin/bash

#########################################################
# FIRST TIME SETUP SCRIPT
# use this the first time running on an raspberry pi
#########################################################

# Sync time forcefully
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

# update system
apt update
apt full-upgrade
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget dropbox

# enables dropbox on start
systemctl enable dropbox.service 
systemctl start dropbox.service

# download python
wget https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tgz
tar zxvf Python-3.13.7.tgz

# build and install
cd Python-3.13.7
./configure --enable-optimizations
make altinstall
cd ..
rm -rf Python-3.13.7

# replace python program with updated version
rm /usr/bin/python
ln -s /usr/local/bin/python3.13 /usr/bin/python

# update pip
python -m pip install --upgrade pip

# setup virtual environment
python -m venv env
source env/bin/activate

pigpiod # this might need to be restarted every reboot
pip install -r requirements.txt
pip install -e .