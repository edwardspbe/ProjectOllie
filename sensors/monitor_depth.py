#!/usr/bin/python3
import datetime, threading, time
import statistics
import RPi.GPIO as GPIO
import sys, os
import signal
import requests
import json
import logging


###############################################################################
# function: test_threshold - will send a notification if a threshold is passed
#                          - this is limited to once an hour..
def test_threshold( inches, last_notification):
    confdata = []
    threshold = 0
    with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
        confdata = json.load(json_data_file)
    if  confdata['sensor_threshold_units'] == "cm":
        threshold = confdata['sensor_threshold']*toInches
    else :
        threshold = confdata['sensor_threshold']
    timenow = datetime.datetime.today()
    deltatime = timenow - datetime.timedelta(minutes=int(confdata['notif_delay']))
    print("deltatime: %s, last: %s" % (deltatime, last_notification))
    print("inches: %s, threshold: %s" % (inches, threshold))
    if (int(inches) < int(threshold)) and deltatime > last_notification :    #send notification (once per hour)
        print("service requested..  sending SMS to %s." % confdata['numbers'])
        ip = os.popen("ip -4 a show wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1").read()
        message = 'Ollie needs help... poo level high at upper pump.  See http://%s' % ip
        for name in confdata['numbers'] :
            answer = requests.post('https://textbelt.com/text', {
                                   'phone': confdata['numbers'][name],
                                   'message': message,
                                   'key': confdata['TextBelt']['key'],
            })
            print("SMS sent to %s" % name)
        last_notification = timenow
    return last_notification

###############################################################################
# function: measure - sends the pulse, measures the time lapsed and calulates 
#                     and returns the distance measured.
def measure():
  # This function measures a distance
  GPIO.output(GPIO_TRIGGER, True)
  # Delay 10us to stablize
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, False)
  start = time.time()
  while GPIO.input(GPIO_ECHO)==0:
      start = time.time()
  while GPIO.input(GPIO_ECHO)==1:
      stop = time.time()
  elapsed = stop-start
  distance = (elapsed * speedSoundCm)/2
  return distance

###############################################################################
# function: start_measuring - hanlder used to do the measuring once every
#                             period of time as controlled by our caller.
# measures distance 5 times then calculates the median in case our slow
# CPU has trouble keeping up... 
def start_measuring(output, last_notification):
    distance = []
    for i in range(0,5):
        mmnt = measure()
        distance.append(mmnt)
        #print("{0:5.1f}".format(mmnt), end=" ")
        time.sleep(1)
    median = statistics.median(distance)
    now = datetime.datetime.now()
    print("{0},{1:.1f},{2:.1f}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), median, median*toInches))
    output.write("{0},{1:.1f},{2:.1f}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), median, median*toInches))
    output.flush()
    return test_threshold( median*toInches, last_notification )

###############################################################################
# function: do_every - nifty routine that uses a generator to track time.  
#
#     Works well cause our measurements only happen once ever 15 seconds. 
#     more real-time apps will require a fast CPU to do processing fast enough.
#
def do_every( period, func ):
    def g_tick():
        t = time.time()
        while True:
            t += period
            yield max(t - time.time(),0)
    
    #initialized last notification to start time. this means we won't send one 
    #for at least an hour after starting. 
    last_notification = datetime.datetime.today()  

    g = g_tick()
    day = datetime.datetime.now().strftime('%Y-%m-%d')
    #open our log file... it will be checked for rotation later
    ofilename = "{}/monitorlog.{}".format(odir,day)
    if os.path.exists(ofilename) :
        output = open(ofilename, 'a')
    else:
        output = open(ofilename, 'w')
        output.write("Date,day,time,cm,inches\n")
    output.flush()
    while True:
        time.sleep(next(g))
        last_notification = func(output, last_notification)
        tmpday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tmpday != day :
            #rotate our log file... 
            outout.close()
            day = tmpday
            output = open("{}/monitorlog.{}".format(odir,day), 'w')
            output.write("Date,day,time,cm,inches\n")


######################################
#Main program starts here

# Speed of sound in cm/s at temperature (TODO: add temp sensor to project)
temperature = 10 
speedSoundCm = 34300 + (0.6*temperature)
toInches=0.3937
odir="/opt/ollie/monitor/log"

# - prior to starting, let's see if we are already running. 
#   if running, stop existing process and start fresh
curfile = os.path.basename(__file__).split('.')[0]
pidfile = "/var/run/{}".format(curfile)
if os.path.isfile(pidfile) :
    #read pid from runtime file, kill it, drop our own pid in the file, keep going...
    with open(pidfile, "r") as file:
        pid = file.readline()
        try :
            os.kill(int(pid), signal.SIGTERM)
        except OSError:
            pass
        file.__exit__()
    os.remove(pidfile)
pid = str(os.getpid())
with open(pidfile, 'a') as output:
    output.write(pid)

print("Ultrasonic Measurements: Upper tank")
print("Speed of sound is {:.1f} cm/s, assuming {} degrees C.".format(speedSoundCm, temperature))
print("    o NOTE: output can be found in {}".format(odir))

# Set pins as output and input
# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  
GPIO.setup(GPIO_ECHO,GPIO.IN)     

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

# Allow module to settle
time.sleep(0.5)

# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:  
    do_every( 30, start_measuring )
except KeyboardInterrupt:
    # User pressed CTRL-C
    # Reset GPIO settings
    GPIO.cleanup()
    
if os.path.isfile(pidfile) :
    os.remove(pidfile)
print("Measuring terminated!")


