
EcoFlow BioFilter Monitoring Solution
-------------------------------------
This folder contains files associated with the (ProjectOllie/sensor) Raspberry Pi project that is used to monitor our septic pump feeding the EcoFlow BioFilter. The intent of this project is to try to understand/monitor the fluids being passed through the BioFilter over the course of the year while the park is open.

This project involves using a Raspberry Pi Zero and a 3 channel Optocoupler Isolation Module used to sense 120V (AC) on a line.  By tapping into the EcoFlow BioFilter Control panel and monitoring when pump voltage is (high/on/120V) along with the low float and high float lines are (high/on/120V) we can better estimate the volume of affluent waste water entering the BioFilter chamber.

The Optocoupler used was [Donker 3 Channel Photoelectric Isolated Module](https://www.amazon.ca/Channel-Optocoupler-Isolation-Isolated-Detection/dp/B081D1N443). Other components include LEDs and resisters used to indicate when low float, high float and pump are on.

![](https://github.com/edwardspbe/ProjectOllie/blob/master/sensors/DeploymentBigPicture.jpg)
![](https://github.com/edwardspbe/ProjectOllie/blob/master/sensors/PiZeroAndOptoCouplerBoard.jpg)
![](https://github.com/edwardspbe/ProjectOllie/blob/master/sensors/PumpCtrlWiring.jpg)

Deployed Solution
-----------------
Script: monitor_floats.py
Description: Tool used to track the flow of fluids into the EcoFlow BioFilter System for ECA related responsibilities.
             This project leverages the use of a tri-input optocoupler circuit to monitor the state of the pump 
             controller. Data is used in conjunction with the pump specifications to calculate flow volume into the 
             EcoFlow BioFilter chamber.
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

Notes on pump monitor program
-----------------------------
Script: monitor_depth.py
Description: 1st attempt at monitoring fluid flow of septic chamber.  Retired as could not sufficiently seal 
            the ultrasonic sensor from moisture in the chamber.  Sensor would only last a few days before dying. :(
Output: /opt/ollie/monitor/log/monitorlog.<date>
Original implementation using ultrasonic sensor.  This solution measures the 
current depth of the holding tank and sends notifications via txt message
when things are alarmingly high and need investigation. Works great for a day
or two and then humidity destroys sensor.
-   The first sensor monitors the depth of our pump tank feeding the peat moss pit.  Spiratic use means spikes in tank levels which can lead to some pretty smelly results so this tool is intended to help us understand when those spikes in activity are and how dramatic they can be so that we can improve the programming of our pumping system.  This is intended to run on a simple [Raspberri PI (zero) with ultrasonic sensor](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/) over the wifi in our park.
- config file should be placed in /lib/systemd/system/... .service
-   The monitor_depth code and associated manager is intended to be run as a [systemd service](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units). 


Notes on pump monitoring data log compilation for import to spreadsheet
-----------------------------------------------------------------------
Logs generally go to the cloud, but if you grab them from the sensor itself, there will be two directories...
log/backup and log.  Some files under some (power failure, etc) conditions do not get copied properly and 
end up as orphaned files. Grab both the orphaned and log/backup files and use the following tools to process
them.

1. catallpumplogs.sh  - script to concatenate all pumplog.<date> files into a single log and them
                        execute the python script (2.)

2. crunch_pump_times.py - script to parse all concatenated pumplogs and dump daily output criteria
                          to be imported into the spreadsheet used to graph daily effluent volumes
