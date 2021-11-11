#! /bin/bash
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin

cd /home/pi/
STR1=`cat DEVICE_NAME`


cd /home/pi/RD200P2_UART_DATA
git init
git add $STR1

git commit -m "ftlab upload"

git push -u origin master:ftlabTest31


