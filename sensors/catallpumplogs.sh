#command to concatinate all log files, sort by date, remove duplicates
#and comment lines
cat pumplog.2025-[01]* orphin/pumplog.2025-[01]* | grep '^202' | sort -u > allpumplogs.txt
#command to remove duplicate day data; defaults to leaving day with longest 
#seconds column in data
python ../crunch_pump_times.py allpumplogs.txt >final_pump_times.txt
