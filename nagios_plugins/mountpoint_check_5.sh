#!/bin/bash
# Author: Rudy
# Date : 20230523
# nsrrc_ui_home mountpoint check for Nagios

mountpoints="/nsrrc_ui_home"
NODE_EXPORTER_FILE="/var/log/nagios_asgc/mountpoints_nsrrc_ui_home"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

exit_nsrrc_mountpoints=0
for i in $mountpoints; do
    /usr/bin/mountpoint -q $i
    if [ $? -ne 0 ]; then
        exit_nsrrc_mountpoints=2
        mount -a
    fi
done

EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_nsrrc_ui_home_mountpoints gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_nsrrc_ui_home_mountpoints $exit_nsrrc_mountpoints"

echo $exit_nsrrc_mountpoints
