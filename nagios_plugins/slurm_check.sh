#!/bin/bash
# Author: Rudy
# Date: 2023-06-06
# Purpose: Check first to get the worker node online to slurm.
# FDR5 worker node

log_file="/var/log/slurm_check/log.txt"

scripts=(
    "/root/t3_worker_nagios/ldap_check.sh"
    "/root/t3_worker_nagios/mount_point_check_ceph_astro_phys.sh"
    "/root/t3_worker_nagios/mount_point_check_ceph_sharedfs.sh"
    "/root/t3_worker_nagios/mount_point_check_dicos_ui_home.sh"
    "/root/t3_worker_nagios/mount_point_check_dlstor2_data.sh"
    "/root/t3_worker_nagios/mount_point_check_t3_cvmfs.sh"
)

echo $(date) > "$log_file"

allgood=1
for script in "${scripts[@]}"; do
    result=$(bash $script)
    if [ $result -ne 0 ]; then
        echo "$script returned a non-zero exit code: $result" >> "$log_file"
        allgood=0
    fi
done

if [ $allgood -eq 1 ]; then
    echo "There are all good. $(date)"
    echo "There are all good." >> "$log_file"
    h=$(hostname | cut -f 1 -d ".")
    slurm_status=$(sinfo -h -o "%t" -n $h)
    if [ "$slurm_status" == "down" ] || [ "$slurm_status" == "drain" ]; then
        echo "Host $h is down."
        /usr/bin/pbsnodes -r "$h"
    fi
    exit 2
else
    echo "There are some problems. See $log_file for details. $(date)"
    h=$(hostname | cut -f 1 -d ".")
    /usr/bin/pbsnodes -o "$h"
    exit 0
fi
