#/bin/bash

RSS=0
for PROC in `ls /proc/|grep "^[0-9]"`
do
  if [ -f /proc/$PROC/statm ]; then
      TEP=`cat /proc/$PROC/statm | awk '{print ($2)}'`
      #echo $TEP
      RSS=`expr $RSS + $TEP`
  fi
done
RSS=`expr $RSS \* 4`
PageTable=`grep PageTables /proc/meminfo | awk '{print $2}'`
SlabInfo=`cat /proc/slabinfo | awk 'BEGIN{sum=0;}{sum=sum+$3*$4;}END{print sum/1024}'`
 
echo "RSS="$RSS"KB", "PageTable="$PageTable"KB", "SlabInfo="$SlabInfo"KB"
#printf "rss+pagetable+slabinfo=%sMB\n" `echo $RSS/1024 + $PageTable/1024 + $SlabInfo/1024 | bc`
total=`expr $RSS + $PageTable + $SlabInfo`
echo "rss + pagetable + slabinfo = $total KB"
free -k