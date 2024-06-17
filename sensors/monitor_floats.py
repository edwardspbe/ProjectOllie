#!/usr/bin/python3
import datetime, threading, time
import statistics
import RPi.GPIO as GPIO
import sys, os
import signal
import requests
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

################################################################################
# function: move_to_GDrive  - copyies a file to google drive location
#
def move_to_GDrive( f1 ):
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  
  #Google drive subdirectory where files are stored
  #ddir="MyPiDrive"

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  token = "%s/token.json" % rdir
  if os.path.exists(token):
    creds = Credentials.from_authorized_user_file(token, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "%s/credentials.json" % rdir, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token, "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    #cfile = "%s/%s" % (ddir, f1)
    file_metadata = {"name": f1 }
    media = MediaFileUpload(f1, mimetype="text/plain")
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return 

################################################################################
# function: send_notification - will send a notification 
DEBUG = False
if DEBUG :
  def send_notification( confdata, state ):
    print("Notification: last: %s, Alarm state: %d" % (monitor.next_notification, state))
    return
else :
  def send_notification( confdata, state ):
    print("service requested..  sending SMS to %s." % confdata['numbers'])
    ip = os.popen("ip -4 a show wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1").read()
    if state == monitor.ON :
        message = 'Ollie needs help... %s.  See http://%s' % (confdata['float_warning'],ip)
    else :
        message = 'Ollie\'s HI alarm now off... See http://%s' % (ip)
    for name in confdata['numbers'] :
        answer = requests.post('https://textbelt.com/text', {
                               'phone': confdata['numbers'][name],
                               'message': message,
                               'key': confdata['TextBelt']['key'],
        })
        print("SMS sent to %s" % name)
    return 

###############################################################################
# function: checkstate - returns the state of our 3 inputs... 
def checkstate():
  one = GPIO.input(GPIO_IN_1)
  two = GPIO.input(GPIO_IN_2)
  three = GPIO.input(GPIO_IN_3)
  return one, two, three

###############################################################################
# function: start_monitor - hanlder used to do the check state of each line
#                  once every period of time as controlled by our caller.
# outputs are for float state changes(time) and pump on/off times
#
def start_monitor(f_output, p_output, confdata, monitor):
    now = datetime.datetime.now()
    f_hi, f_low, pump = checkstate()
    if DEBUG :
        print("STATES:  f_hi(%s), f_low(%s), pump(%s)" % (f_hi, f_low, pump))

    #set visual indicators
    if f_hi == monitor.ON:
        GPIO.output(GPIO_OUT_HI,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_HI,GPIO.LOW)
    if f_low == monitor.ON:
        GPIO.output(GPIO_OUT_LOW,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_LOW,GPIO.LOW)
    if pump == monitor.ON:
        GPIO.output(GPIO_OUT_PUMP,GPIO.HIGH)
    else:
        GPIO.output(GPIO_OUT_PUMP,GPIO.LOW)
    
    #if any state change, log it... 
    if (f_hi != monitor.f_hi_state) or (f_low != monitor.f_low_state) \
                                    or (pump != monitor.pump_state):
        print("State change: {0}, {1}, {2}, {3}, {4}, {5}, {6}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), \
                f_hi, f_low, pump, monitor.f_hi_state, monitor.f_low_state, monitor.pump_state))
        f_output.write("{0}, {1}, {2}, {3}\n".format(now.strftime('%Y-%m-%d, %a, %H:%M:%S'), f_hi, f_low, pump))

    #send notification if high float alarm or change in high float alarm
    if f_hi == monitor.ON :
        if monitor.next_notification == 0 :
            monitor.next_notification = now + datetime.timedelta(minutes=int(confdata['notif_delay']))
        if now > monitor.next_notification :
            send_notification(confdata, monitor.ON)
            monitor.pump_notification_sent = 1
            monitor.next_notification = 0
    if f_hi == monitor.OFF and f_hi != monitor.f_hi_state : #transition from hi float alarm off...
        if monitor.pump_notification_sent == 1 :
            send_notification(confdata, monitor.OFF)
            monitor.pump_notification_sent = 0
            monitor.next_notification = 0
    
    #track and log time pump is on
    if (pump == monitor.ON) and (monitor.pump_state == monitor.OFF) :
        #log pump just started
        print("{} State: ON\n".format(now.strftime('%Y-%m-%d %a %H:%M:%S')))
        p_output.write("{} State: ON\n".format(now.strftime('%Y-%m-%d %a %H:%M:%S')))
    if (pump == monitor.OFF) and (monitor.pump_state == monitor.ON) :
        #log pump stopped
        p_output.write("{} State: OFF\n".format(now.strftime('%Y-%m-%d %a %H:%M:%S')))
        print("{} State: OFF\n".format(now.strftime('%Y-%m-%d %a %H:%M:%S')))
        monitor.pump_started = 0
        

    #set the current state so we can monitor for change going forward.
    monitor.f_hi_state = f_hi
    monitor.f_low_state = f_low
    monitor.pump_state = pump
    f_output.flush()
    p_output.flush()
    return 

###############################################################################
# function: do_every - nifty routine that uses a generator to track time.  
#
def do_every( func, monitor ):
    def g_tick(period):
        t = time.time()
        while True:
            t += period
            yield max(t - time.time(),0)
    
    #get configuration data
    confdata = []
    with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
        confdata = json.load(json_data_file)

    g = g_tick(confdata['float_measurement_frequency'])
    day = datetime.datetime.now().strftime('%Y-%m-%d')

    #open our log file... it will be checked for rotation later
    ffilename = "{}/floatlog.{}".format(odir,day)
    pfilename = "{}/pumplog.{}".format(odir,day)
    if os.path.exists(ffilename) :
        f_output = open(ffilename, 'a')
    else:
        f_output = open(ffilename, 'w')
        f_output.write("Date, day, time, line, state(hi,lo,pump)\n----------------------------------------\n")
    f_output.flush()
    if os.path.exists(pfilename) :
        p_output = open(pfilename, 'a')
    else:
        p_output = open(pfilename, 'w')
        p_output.write("Pump state changes\n----------------------------\n")
    p_output.flush()
    
    #endlessly retry and log our measurements... 
    while True:
        time.sleep(next(g))
        func(f_output, p_output, confdata, monitor)
        tmpday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tmpday != day :
            #rotate our log file
            #... but first re-read configuration just in case things have changed... 
            with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
                confdata = json.load(json_data_file)
            f_output.close()
            p_output.close()

            #make backup of current files...
            os.system("cp {} {}/backup/floatlog.{}".format(ffilename, odir, day) )
            os.system("cp {} {}/backup/pumplog.{}".format(pfilename, odir, day) )

            #move output files to google drive
            move_to_GDrive( ffilename )
            move_to_GDrive( pfilename )

            #progress with 
            day = tmpday
            f_output = open(ffilename, 'w')
            f_output.write("Date, day, time, line, state(hi,lo,pump)\n----------------------------------------\n")
            f_output.flush()
            p_output = open(pfilename, 'w')
            p_output.write("Pump state changes\n----------------------------\n")
            p_output.flush()


###############################################################################
class MonitorData :
    #optoisolator is NC (normally closed) returning (1) for off and (0) for on
    #...a little backwards but if we use the definition and not the value, it works.
    ON = 0
    OFF = 1
    #our static variables for state...
    f_hi_state = OFF
    f_low_state = OFF
    pump_state = OFF
    next_notification = 0
    pump_notification_sent = 0

######################################
#Main program starts here
#Read all configuration data used by project
with open('/opt/ollie/monitor/ollie_at_your_service.conf') as json_data_file:
    confdata = json.load(json_data_file)
odir = confdata['logdir']
rdir = confdata['rundir']

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
GPIO_IN_2 = 22  #f_low
GPIO_IN_3 = 23  #pump

#declare the object that will track our state
monitor = MonitorData()

GPIO_OUT_HI = 21   #f_hi indicator
GPIO_OUT_LOW = 20  #f_low indicator
GPIO_OUT_PUMP = 16 #pump indicator

# Use BCM (Broadcom) GPIO references instead of physical pin numbers 
GPIO.setmode(GPIO.BCM)  #vs.  GPIO.setmode(GPIO.BOARD)

# initialize input pins
GPIO.setup(GPIO_IN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_IN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_IN_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#initialize output pins (controlling LED indicators)
GPIO.setup(GPIO_OUT_HI, GPIO.OUT) 
GPIO.setup(GPIO_OUT_LOW, GPIO.OUT) 
GPIO.setup(GPIO_OUT_PUMP, GPIO.OUT) 
GPIO.output(GPIO_OUT_HI, GPIO.LOW)
GPIO.output(GPIO_OUT_LOW, GPIO.LOW)
GPIO.output(GPIO_OUT_PUMP, GPIO.LOW)

# Allow module to settle
time.sleep(0.5)

# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:  
    do_every( start_monitor, monitor )
except KeyboardInterrupt:
    # User pressed CTRL-C
    # Reset GPIO settings
    GPIO.cleanup()
    
if os.path.isfile(pidfile) :
    os.remove(pidfile)
print("Monitoring Terminated!")
