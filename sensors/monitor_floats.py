#!/usr/bin/python3
import datetime, threading, time
import statistics
import RPi.GPIO as GPIO
import sys, os
import signal
import requests
import json
import logging


################################################################################
# function: send_notification - will send a notification if last notification 
#                               time has exceeded threshold.
def dbg_send_notification( confdata, last_notification, force):
    timenow = datetime.datetime.today()
    deltatime = timenow - datetime.timedelta(minutes=int(confdata['notif_delay']))
    print("deltatime: %s, last: %s, forced notification: %d" % (deltatime, last_notification, force))
    if deltatime > last_notification or force:    #send notification (once per hour)
        print("service requested..  sending SMS to %s." % confdata['numbers'])
        last_notification = timenow
    return last_notification


def send_notification( confdata, last_notification, force):
    timenow = datetime.datetime.today()
    deltatime = timenow - datetime.timedelta(minutes=int(confdata['notif_delay']))
    print("deltatime: %s, last: %s, forced notification: %d" % (deltatime, last_notification, force))
    if deltatime > last_notification or force:    #send notification (once per hour)
        print("service requested..  sending SMS to %s." % confdata['numbers'])
        ip = os.popen("ip -4 a show wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1").read()
        message = 'Ollie needs help... %s.  See http://%s' % (confdata['float_warning'],ip)
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
# function: checkstate - returns the state of our 3 inputs... 
def checkstate():
  one = GPIO.input(GPIO_IN_1)
  two = GPIO.input(GPIO_IN_2)
  three = GPIO.input(GPIO_IN_3)
  return one, two, three

###############################################################################
# function: start_monitoring - hanlder used to do the check state of each line
#                  once every period of time as controlled by our caller.
def start_monitoring(output, confdata, last_notification):
    start_monitoring.f_hi_state
    start_monitoring.f_low_state 
    start_monitoring.pump_state
    now = datetime.datetime.now()
    f_hi, f_low, pump = checkstate()
        
    if f_hi == ON:
        GPIO.output(GPIO_OUT_3,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_3,GPIO.LOW)
    if f_low == ON:
        GPIO.output(GPIO_OUT_2,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_2,GPIO.LOW)
    if pump == ON:
        GPIO.output(GPIO_OUT_1,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_1,GPIO.LOW)
    if (f_hi != start_monitoring.f_hi_state) or (f_low != start_monitoring.f_low_state) or \
                                                (pump != start_monitoring.pump_state):
        print("State change: {0},{1},{2},{3}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), f_hi, f_low, pump))
        output.write("{0},{1},{2},{3}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), f_hi, f_low, pump))
        output.flush()

    #send notification if high float alarm or change in high float alarm
    if f_hi == ON:
        last_notification = dbg_send_notification(confdata, last_notification, False)
    if f_hi == OFF and f_hi != start_monitoring.f_hi_state :
        last_notification = dbg_send_notification(confdata, last_notification, True)

    #set the current state so we can monitor for change going forward.
    f_hi_state = f_hi
    f_low_state = f_low
    pump_state = pump
    return last_notification

###############################################################################
# function: do_every - nifty routine that uses a generator to track time.  
#
def do_every( func ):
    def g_tick(period):
        t = time.time()
        while True:
            t += period
            yield max(t - time.time(),0)
    
    #get configuration data
    confdata = []
    with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
        confdata = json.load(json_data_file)

    #initialized last notification to start time. this means we won't send one 
    #for at least an hour after starting. 
    last_notification = datetime.datetime.today()  

    g = g_tick(confdata['float_measurement_frequency'])
    day = datetime.datetime.now().strftime('%Y-%m-%d')

    #open our log file... it will be checked for rotation later
    ofilename = "{}/floatlog.{}".format(odir,day)
    if os.path.exists(ofilename) :
        output = open(ofilename, 'a')
    else:
        output = open(ofilename, 'w')
        output.write("Date, day, time, line, state\n----------------------------\n")
    output.flush()
    
    #endlessly retry and log our measurements... 
    while True:
        time.sleep(next(g))
        last_notification = func(output, confdata, last_notification)
        tmpday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tmpday != day :
            #rotate our log file
            #... but first re-read configuration just in case things have changed... 
            with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
                confdata = json.load(json_data_file)
            output.close()
            day = tmpday
            output = open("{}/floatlog.{}".format(odir,day), 'w')
            output.write("Date, day, time, line, state\n----------------------------\n")



######################################
#Main program starts here
#Read all configuration data used by project
with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
    confdata = json.load(json_data_file)
odir = confdata['logdir']

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

#starting... 
print("Pump Float Monitor: Upper tank")
print("  o NOTE: output can be found in {}".format(odir))

# Define GPIO to use for input
# aligning as:  f_hi, f_low, pump = checkstate(return one,two,three)
GPIO_IN_1 = 17  #f_hi
GPIO_IN_2 = 23  #f_low
GPIO_IN_3 = 22  #pump
#optoisolator is NC (normally closed) returning (1) for off and (0) for on
ON = 0
OFF = 1
#our static variables for state...
start_monitoring.f_hi_state = OFF
start_monitoring.f_low_state = OFF
start_monitoring.pump_state = OFF

GPIO_OUT_1 = 16
GPIO_OUT_2 = 20
GPIO_OUT_3 = 21

# Use BCM (Broadcom) GPIO references instead of physical pin numbers 
GPIO.setmode(GPIO.BCM)  #vs.  GPIO.setmode(GPIO.BOARD)

# initialize input pins
GPIO.setup(GPIO_IN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_IN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_IN_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#initialize output pins (controlling LED indicators)
GPIO.setup(GPIO_OUT_1, GPIO.OUT) 
GPIO.setup(GPIO_OUT_2, GPIO.OUT) 
GPIO.setup(GPIO_OUT_3, GPIO.OUT) 
GPIO.output(GPIO_OUT_1, GPIO.LOW)
GPIO.output(GPIO_OUT_2, GPIO.LOW)
GPIO.output(GPIO_OUT_3, GPIO.LOW)

# Allow module to settle
time.sleep(0.5)

# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:  
    do_every( start_monitoring )
except KeyboardInterrupt:
    # User pressed CTRL-C
    # Reset GPIO settings
    GPIO.cleanup()
    
if os.path.isfile(pidfile) :
    os.remove(pidfile)
print("Monitoring Terminated!")


