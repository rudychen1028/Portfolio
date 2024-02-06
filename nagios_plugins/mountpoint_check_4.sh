#!/bin/bash
# Author: Rudy
# Date : 20230523
# dlstor2:/data mountpoint check for Nagios

mountpoints="/data"
NODE_EXPORTER_FILE="/var/log/nagios_asgc/mountpoints_dlstor2_data"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

exit_dlstor2_mountpoints=0
for i in $mountpoints; do
    /usr/bin/mountpoint -q $i
    if [ $? -ne 0 ]; then
        exit_dlstor2_mountpoints=2
        mount -a
        # MSG="OTHER Mountpoint: [$i] is problematic! "$MSG
    fi
done
#for i in $mountpoints; do
#    c=`ls /cvmfs/$i  | wc -l`
#    if [ $? -ne 0 ] || [ $c -eq 0 ]; then
#        exit_dlstor2_mountpoints=2
#    fi
#done

EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_dlstor2_data_mountpoints gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_dlstor2_data_mountpoints $exit_dlstor2_mountpoints"

echo $exit_dlstor2_mountpoints
