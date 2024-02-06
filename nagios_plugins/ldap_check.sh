#!/bin/bash
# Purpose: prometheus check on ldap access for worker nodes

NODE_EXPORTER_FILE="/var/log/nagios_asgc/ldap.check"

if [ ! -d /var/log/nagios_asgc ];then
        mkdir /var/log/nagios_asgc
fi

nlimit=3
n=0
max_sec=10
res=`id harvesteruser`
if [ $? -eq 0 ]; then
    ldap_status=0
else
    ldap_status=2
    while [ $n -lt $nlimit ] && [ $ldap_status -ne 0 ]; do
        s_time=`echo "scale=1; $RANDOM/32767*$max_sec" | bc | cut -d "." -f 1`
        echo "$s_time"
        sleep $s_time
        res=`id harvesteruser`
        ldap_status=$?
        n=$(($n+1))
        #echo $n
    done
    if [ $ldap_status -ne 0 ]; then
        ldap_status=2
    fi
fi

EXPORT_METRICS=$EXPORT_METRICS"# TYPE check_ldap_status gauge\n"
EXPORT_METRICS=$EXPORT_METRICS"check_ldap_status $ldap_status\n"

echo $ldap_status
#echo -e $EXPORT_METRICS > $NODE_EXPORTER_FILE
