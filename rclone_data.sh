#!/bin/bash
# Script to transfer data to dropbox
# Warning: Do not run on your personal machine!
# The file is moved using either a server move, or via copying, then deleting

# Sync time forcefully
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

# Move to dropbox
# parameter is for a folder
rclone move /home/pi/RWS/Data/ dropbox:/$1/Data --include=*.csv
