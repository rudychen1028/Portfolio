#!/bin/bash
# Author: Rudy
# Date : 20230523
# T3 cvmfs mountpoint check for Nagios

cvmfs_mountpoints="cvmfs.grid.sinica.edu.tw sft.cern.ch "
NODE_EXPORTER_FILE="/var/log/nagios_asgc/mountpoints_t3_cvmfs"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

exit_cvmfs_mountpoints=0
for i in $cvmfs_mountpoints; do
    c=`ls /cvmfs/$i  | wc -l`
    if [ $? -ne 0 ] || [ $c -eq 0 ]; then
        exit_cvmfs_mountpoints=2
    fi
done

EXPORT_METRICS=""
EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_cvmfs_mountpoints gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_cvmfs_mountpoints $exit_cvmfs_mountpoints"

echo $exit_cvmfs_mountpoints
