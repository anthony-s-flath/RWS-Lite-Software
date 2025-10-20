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
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

# download python
wget https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tgz
tar zxvf Python-3.13.7.tgz

# build and install
cd Python-3.13.7
./configure --enable-optimizations
make altinstall

# replace python program with updated version
cd /usr/bin
rm python
ln -s /usr/local/bin/python3.13.7 python

# update pip
python -m pip install --upgrade pip

# go to home
cd ~

# this line will be different depending on RWS edition
git clone https://github.com/anthony-s-flath/RWS-Lite-Software

# setup virtual environment
python -m venv env
source env/bin/activate

pigpiod # this might need to be restarted every reboot
pip install -r requirements.txt
pip install -e .