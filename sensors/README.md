# ProjectOllie - Sensors 
![ProjectOllie](https://github.com/edwardspbe/ProjectOllie/blob/master/banner.jpg)

This area is focused on work to impliment rudimentary sensors and their associated monitoring and reporting tools.  

## monitor_depth

The first sensor monitors the depth of our pump tank feeding the peat moss pit.  Spiratic use means spikes in tank levels which can lead to some pretty smelly results so this tool is intended to help us understand when those spikes in activity are and how dramatic they can be so that we can improve the programming of our pumping system.  This is intended to run on a simple ![Raspberri PI (zero) with ultrasonic sensor](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/) over the wifi in our park.

The monitor_depth code and associated manager is intended to be run as a ![systemd service](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units). 
