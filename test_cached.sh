#!/bin/sh

DATA_8KB=""

a=$(echo `< /dev/urandom tr -dc A-Za-z0-9 | head -c8192`)
DATA_8KB=$a

echo $DATA_8KB

#echo "" > /var/log/aa.log

while [ 1 ]
do
  #echo $DATA_8KB >> /var/log/aa.log
  #logger -p INFO $DATA_8KB
  #logger -p local.INFO $DATA_8KB
  #logger -p local2.INFO $DATA_8KB
  #logger -p local3.INFO $DATA_8KB
  #logger -p local4.INFO $DATA_8KB
  #logger -p local5.INFO $DATA_8KB
  #logger -p local6.INFO $DATA_8KB
  logger -p local7.INFO $DATA_8KB
  usleep 1500
done