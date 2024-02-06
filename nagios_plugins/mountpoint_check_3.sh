#!/bin/bash
# Author: Rudy
# Date : 20230523
# dicos_ui_home mountpoint check for Nagios

mountpoints="/dicos_ui_home"
NODE_EXPORTER_FILE="/var/log/nagios_asgc/mountpoints_dicos_ui_home"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

exit_dicos_mountpoints=0
for i in $mountpoints; do
    /usr/bin/mountpoint -q $i
    if [ $? -ne 0 ]; then
        exit_dicos_mountpoints=2
        mount -a
    fi
done

EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_dicos_ui_home_mountpoints gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_dicos_ui_home_mountpoints $exit_dicos_mountpoints"

echo $exit_dicos_mountpoints
