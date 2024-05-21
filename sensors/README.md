Notes on pump monitor program

Script: monitor_depth.py
Output: /opt/ollie/monitor/log/monitorlog.<date>
Original implementation using ultrasonic sensor.  This solution measures the 
current depth of the holding tank and sends notifications via txt message
when things are alarmingly high and need investigation. Works great for a day
or two and then humidity destroys sensor.
-   The first sensor monitors the depth of our pump tank feeding the peat moss pit.  Spiratic use means spikes in tank levels which can lead to some pretty smelly results so this tool is intended to help us understand when those spikes in activity are and how dramatic they can be so that we can improve the programming of our pumping system.  This is intended to run on a simple [Raspberri PI (zero) with ultrasonic sensor](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/) over the wifi in our park.
- config file should be placed in /lib/systemd/system/... .service
-   The monitor_depth code and associated manager is intended to be run as a [systemd service](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units). 

Script: monitor_floats.py
Output Filename: pumpstatus.csv.<date>
Data collected by sensor to be moved to our Google Drive

Content: periodic state of; pump (ON|OFF), LowFloat (ON|OFF), HIGHFLOAT (ON|OFF)
example:  date, time, <pstate>, <lfstate>, <hfstate>

Content2: state change notifications
example: date, time, <object> <oldstate> <newstate> 

Why are we collecting two types of data? 
... what if our monitor fails?
... what if our system isn't being used?
... we need to get notifications should things stop working or at the 
....... very least, if states stop changing.

TODO: Another option would be to input and track the programmable timed 
... dosage state changes.  When our sensor doesn't see the timing changes
... expected, then a notification could be triggered.  We would still need
... to track the state changes though so we understand how much we are 
... pumping.


