#! /bin/bash

#########################################################
# POST REBOOT SCRIPT
# use this in between cold reboots
#########################################################

# start io daemon
pigpiod

# Sync time forcefully
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

# this will be different depending on RWS directory
cd ~/RWS-Lite-Software

# activate virtual environment
source env/bin/activate
