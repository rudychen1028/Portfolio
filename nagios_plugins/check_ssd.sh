#!/bin/bash

ALERT=80
disk=$( df -h | grep ssd | awk '{ print $5 }' | cut -d'%' -f1 )
check=($( sudo docker ps -a| awk -F' ' '{print $10}' | grep cryosparc | awk -F'-' '{print $2}' | awk -F'_' '{print "\\|"$1}' | sort | uniq))
IFS="" eval 'lst="${check[*]}"'
cmd=$(echo "ls /ssd | grep -v '$(echo ${lst:2})'")
if [ $disk -gt "$ALERT" ]; then
  echo 'Warning- Clean the data right away!'
  #echo $check
  #echo $cmd
  eval $cmd | while read t
  do
    cd /ssd
    sudo rm -rf $t
  done
  exit 2
else
  echo "Everything is ok!"
  exit 0
fi
