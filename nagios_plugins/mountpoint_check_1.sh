#!/bin/bash
# Author: Rudy
# Date : 20230523
# Ceph (astro_phys) mountpoint check for Nagios

ceph_mountpoints="astro_phys"
NODE_EXPORTER_FILE="/var/log/nagios_asgc/mountpoints_ceph_astro_phys"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

exit_ceph_mountpoints=0
for i in $ceph_mountpoints; do
    /usr/bin/mountpoint -q /ceph/$i
    if [ $? -ne 0 ]; then
        exit_ceph_mountpoints=2
    fi
done

EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_ceph_astro_phys_mountpoints gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_ceph_astro_phys_mountpoints $exit_ceph_mountpoints"

echo $exit_ceph_mountpoints
