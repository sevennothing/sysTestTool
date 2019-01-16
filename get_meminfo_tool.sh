#!/bin/sh

LOG_FILE=/var/log/mem.log
COMPRESS_LOGFILE=/var/log/mem_log.tar.gz
sum=0
MAND_PID=0
LRCP_PID=0
LRFP_PID=0
ZEBRA_PID=0
OSPFD_PID=0
FIBMGMT_PID=0
SNMPAPP_PID=0
MIPS_MAIN_PID=0
DROPBEAR_PID=0
CROND_PID=0

tmp_pid=0

tarfileCnt=0

USE_SYSLOG=0

### syslog 远程记录日志单条日志长度不能超过125 B
### vi中用:%s/\[#\]\n//  进行恢复
do_log(){                                                                                                                                                                                                     
        if [ $USE_SYSLOG == 1 ];then                                                                                                                                                                          
        strlen=${#1}                                                                                                                                                                                          
        if [ $strlen -lt 125 ];then                                                                                                                                                                           
                logger -p local5.info "$1"                                                                                                                                                                    
        else                                                                                                                                                                                                  
                let cnt=0                                                                                                                                                                                     
                while [ $cnt -le $strlen ]                                                                                                                                                                    
                do                                                                                                                                                                                            
                  msg=${1:$cnt:125}                                                                                                                                                                           
                  logger -p local5.info "$msg[#]"                                                                                                                                                                
                  let cnt+=125                                                                                                                                                                                
                done                                                                                                                                                                                          
                logger -p local5.info " "                                                                                                                                                                
        fi                                                                                                                                                                                                    
        else                                                                                                                                                                                               
                echo "$1" >> $LOG_FILE                                                                                                                                                                        
        fi                                                                                                                                                                                                    
}

compress_log_file(){
	if [ $USE_SYSLOG == 0 ];then
		compressLogFile="/var/log/mem"$tarfileCnt".tar.gz"
		echo " Compress MEM log file to $compressLogFile ..."
		tar czf $compressLogFile $LOG_FILE
		echo "" > $LOG_FILE
		let tarfileCnt+=1
	fi
}

first_log(){
	ts=$(date +%s)
	uptime=$(uptime)
	do_log "!!! Check $1 when $ts; $uptime ===================== "
}

log_error(){
	do_log "ERR!!! do $1 FAILED"
}
log_info(){
	do_log "INFO: $1"
}

log_msg(){
	do_log "$1"
}
get_sys_info(){
	info1=$(uname -a)
	info="INFO: SYSTEM-INFO $info1"
	log_msg "$info"
}
check_pid(){
	PROCESS=`ps -ef | grep $1 | grep -v grep | grep -v PPID | awk '{ print $1 }'`
	for i in $PROCESS
	do
		if [ -d /proc/$i ];then
			log_info "check $1 pid is $i"
			tmp_pid=$i
			return 0
		fi
	done
	log_error "check_pid $@"
	return 0
}


scan_dev_pid(){
	check_pid mand
	[ $? == 0 ] && MAND_PID=$tmp_pid

	check_pid lrcp
	[ $? == 0 ] && LRCP_PID=$tmp_pid

	check_pid lrfp.strip
	[ $? == 0 ] && LRFP_PID=$tmp_pid

	check_pid zebra
	[ $? == 0 ] && ZEBRA_PID=$tmp_pid

	check_pid ospfd
	[ $? == 0 ] && OSPFD_PID=$tmp_pid

	check_pid fibmgmt
	[ $? == 0 ] && FIBMGMT_PID=$tmp_pid

	check_pid snmpApp
	[ $? == 0 ] && SNMPAPP_PID=$tmp_pid

	check_pid mips_main
	[ $? == 0 ] && MIPS_MAIN_PID=$tmp_pid

	check_pid dropbear
	[ $? == 0 ] && DROPBEAR_PID=$tmp_pid

	check_pid crond
	[ $? == 0 ] && CROND_PID=$tmp_pid

}


free_cmd(){
	info=$(free -b)
	log_msg "$info"
}

meminfo_cmd(){
	info=$(cat /proc/meminfo | sed ':a;N;$!ba;s/\n/ /g')
	log_msg "$info"
}

show_slabinfo_result_key(){ 
	info1=$(cat /proc/slabinfo | awk '{print $1}' | sed ':a;N;$!ba;s/\n/ /g')
	info="slabinfo-key: $info1"
	log_msg "$info"
}
slabinfo_result_cmd(){
	info1=$(cat /proc/slabinfo | awk '{print $3*$4}' | sed ':a;N;$!ba;s/\n/ /g')
	info2=$(cat /proc/slabinfo | awk 'BEGIN{sum=0;}{sum=sum+$3*$4;}END{print sum}')
	info="slabinfo: $info1"
	log_msg "$info"
	info="slabinfo_total: $info2 B"
	log_msg "$info"
}

log_pid_status(){
	#cat /proc/$1/status >> $LOG_FILE
	#cat /proc/$1/status | grep -E "Vm*|Name" >> $LOG_FILE
	info=$(cat /proc/$1/status | grep -E "Vm*|Name" | sed ':a;N;$!ba;s/\n/ /g')
	#echo "Name:	$2 END" >> $LOG_FILE
	log_msg "$info"
}

iostat_cmd(){
	info=$(iostat)
	log_msg "$info"
}

##### This is Test start  ###
[ -f $LOG_FILE ] || `touch $LOG_FILE`

scan_dev_pid

get_sys_info
show_slabinfo_result_key

while [ 1 ]
do
  let sum=sum+1
  first_log $sum
  free_cmd
  meminfo_cmd
  iostat_cmd
  slabinfo_result_cmd

  log_pid_status $MAND_PID mand
	log_pid_status $LRCP_PID lrcp 
	log_pid_status $LRFP_PID lrfp.strip
	log_pid_status $FIBMGMT_PID fibmgmt
	log_pid_status $ZEBRA_PID zebra
	log_pid_status $OSPFD_PID ospfd
	log_pid_status $SNMPAPP_PID snmpApp
	log_pid_status $MIPS_MAIN_PID mips_main
	log_pid_status $DROPBEAR_PID dropbear
	log_pid_status $CROND_PID crond

<<EOF
  for pid in $CHECK_PID_LIST
  do
	log_pid_status $pid
  done
EOF

  logfileSize=$(ls -l $LOG_FILE  | awk '{print $5}')
  if [ $logfileSize -gt 10485760 ];then
  	compress_log_file
  fi
  sleep 10
  
done
