#!/bin/bash 

logdir="/opt/ollie/monitor/log/"
DATE=`date`

if [ $# -ne 1 ] 
then
    echo "[${DATE}: syntax error in state.bash" >> $logdir\state.log
else
    if [ "$1" == "on" ]
	then 
		systemctl start monitor_depth
    else 
		systemctl stop monitor_depth
	fi
fi
