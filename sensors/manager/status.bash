#!/bin/bash 

logdir="/opt/ollie/monitor/log/"
status=`systemctl status monitor_depth | grep "Active:"`
echo "$status <br>"

running=`echo $status | grep "running" > /dev/null 2>&1`
if [ $? -eq 0 ] 
then
    file=`ls -t $logdir  | head -1`
    while read -r line
	do
		echo "$line <br>"
	done < <(tail -50 $logdir/$file)
fi
