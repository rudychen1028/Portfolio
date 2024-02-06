#!/bin/bash 
calculate_disk_uses(){
used_space=`df -h ${MOUNT_POINT} | grep -v Filesystem | awk '{print $5}' | sed 's/%//g'`
case $used_space in 
[1-80]*) 
echo "OK - $used_space% of disk space used." 
exit 0 
;; 
[81-85]*) 
echo "WARNING - $used_space% of disk space used." 
exit 1 
;; 
[86-100]*) 
echo "CRITICAL - $used_space% of disk space used." 
exit 2 
;; 
*) 
echo "UNKNOWN - $used_space% of disk space used." 
exit 3 
;; 
esac
}

if [[ -z "$1" ]] 
then
        echo "Missing parameters! Syntax: ./`basename $0` mount_point/disk"
        exit 3
else
        MOUNT_POINT=$1
fi
 
calculate_disk_uses 
