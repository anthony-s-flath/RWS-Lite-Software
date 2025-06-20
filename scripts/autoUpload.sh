#! /bin/bash
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin

sudo echo -e "0 */1 * * * ./ftlabUpload.sh" | crontab
sudo /etc/init.d/cron restart 

