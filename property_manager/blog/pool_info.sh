#!/bin/bash
pool_name=`xe pool-list | grep name-label | awk -F ":" '{print $2}'`
host_name=`xe host-list | grep name-label | awk '{print $4}'`
ip_name=`ip a | grep inet | grep 172.30 | awk '{print $2}' | awk -F '/' '{print $1}'`
echo $pool_name > /tmp/$ip_name
for i in $host_name
  do
    b=`echo $i | awk -F "-" '{print $2}'`
    c=`echo $i | awk -F "-" '{print $3}'`
    d="172.30.$b.$c"
    echo "xe-$d" >> /tmp/$ip_name
    vm_host=`xe console-list | grep -B 4  $d  | grep "172.30" | grep vm-name-label | awk '{print $4}'`
    for i in $vm_host
      do
         vm_memory=`xe vm-list name-label=$i params=memory-actual | awk -F ":" '{print $2}'`
         vm_cpu=` xe vm-list name-label=$i params=VCPUs-number | awk -F ":" '{print $2}'`
         vm_disk=`xe vm-disk-list vm=$i | grep -A 1 sr-name-label  | grep virtual-size  | awk -F ":" '{print $2}'`
         echo $i"==="$vm_cpu"==="$vm_memory"==="$vm_disk >> /tmp/$ip_name
      done
done
