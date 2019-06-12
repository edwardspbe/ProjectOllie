#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        ollie_at_your_service.py
# Purpose      Snack Shack notifications python module for automating snack shack.
#
# Author:      paul.e@rogers.com
#
# References:  
# GPIO docs - https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
# PI B+ pinout - http://www.keytosmart.com/raspberry-pi-b-gpio-details-pinout/
#
# Created:     13/03/2018
#              03/01/2019 - updated to include test mode printing actions instead
#                           of sending SMSs to allow for easier testing.
# Copyright:   (c) paul.e@rogers.com 2018
# Licence:     MIT
#-------------------------------------------------------------------------------
 
'''
Ollies Snack Shack notification system

Simple push button implemented on a raspberry pi (zero).
When the button is pushed an SMS notification is sent to the
"on-call" list of phone numbers indicating service required 
at the snack-shack.  

'''

import sys
import RPi.GPIO as GPIO
import multiprocessing
import requests
import json
import os
import logging
from time import sleep
from datetime import datetime

#Raspberry Pi GPIO pins used to set/change colours on 
sbutt = 21   #service button
abutt = 26   #admin button
red   = 17
blue  = 22
green = 27
yellow = (red,green)
cyan  = (blue,green)
magenta = (red,blue)
white = (red,blue,green)

#blink times
large=1
medium=0.5
small=0.25
tiny=0.1

SmsQuietPeriod = 300    #no of seconds before sending another SMS mesg...

#led blink cycles
wait = (blue)
errorstate = (
    (red,small,25), 
)
working = (
    (magenta,medium,10), 
    (green,medium,10), 
)
alreadywaiting= (
    (green,small,10), 
)

def blinkon(pins):
    if isinstance(pins, list):
        for pin in pins :
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
    else :  #assume single pin
        GPIO.setup(pins, GPIO.OUT)
        GPIO.output(pins, GPIO.HIGH)

def blinkoff(pins):
    if isinstance(pins, list):
        for pin in pins :
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    else :  #assume single pin
        GPIO.setup(pins, GPIO.OUT)
        GPIO.output(pins, GPIO.LOW)

def do_blink_loop(cycle):
    for colour,time,repeat in cycle :
        for i in range(repeat) :
            blinkon(colour)
            sleep(time)
            blinkoff(white)
            sleep(time)


def sendSMSNotification():
    logging.info("service requested..  sending SMS to %s." % confdata['numbers'])
    answer=[]
    success=True
    ip = os.popen("ip -4 a show wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1").read()
    #message may not include URLs unless we are "whitelisted" by the TextBelt.com guys... 
    #Whitelisted (Jun. 11, 2019) 
    #message = 'Ollie needs help at the Snack Shack.  If you no longer want to be on-call, please reconfigure Ollie at: %s' % ip
    message = 'Ollie needs help at the Snack Shack.  If you no longer want to be on-call, please reconfigure Ollie at: http://%s' % ip
    for name in confdata['numbers'] :
        answer = requests.post('https://textbelt.com/text', {
                               'phone': confdata['numbers'][name],
                               'message': message,
                               'key': confdata['TextBelt']['key'],
        })
        print "SMS sent to %s" % name
        obj = json.loads(answer.content)
        if obj['success'] != True :
            logging.info("SMS SEND ERROR: [%s]" % obj['error'])
            s_callbk.service_ts = None
            blinkon(red)
            s_callbk.led_state = red
            return
    blinkoff(white)
    do_blink_loop(working)
    blinkon(green)
    s_callbk.led_state = green


def logNotification():
    logging.info("service requested..  logging notification to %s." % confdata['numbers'])
    answer=[]
    for name in confdata['numbers'] :
        logging.info("logging notification for %s" % name)
        logging.info('please reconfigure at: <a href="http://%s/>http://%s</a>' % (ip,ip))
    blinkoff(white)
    do_blink_loop(working)
    blinkon(green)
    s_callbk.led_state = green


#called when admin button is tripped
def a_callbk():
    pass

#called when service button is tripped
def s_callbk(pin):
    #this is important in case someone is pushing the button non-stop
    if s_callbk.service_ts != None :
        delta = datetime.now() - s_callbk.service_ts
        if SmsQuietPeriod > delta.seconds :
            logging.info("service request while in WAIT-PERIOD.")
            return

    s_callbk.service_ts = datetime.now()
    #logNotification()
    sendSMSNotification()

#make sure we are operating properly and LEDs are indicating ready... 
def check_state():
    if s_callbk.service_ts != None :
        logging.info("in check_state with service_ts=%s" % s_callbk.service_ts )
        delta = datetime.now() - s_callbk.service_ts
        if delta.seconds > SmsQuietPeriod :
            logging.info("in check_state: resetting timer..." )
            s_callbk.service_ts = None
            blinkoff(white)
            blinkon(blue)
        else :
            blinkoff(white)
            blinkon(green)
    else :
        logging.info("in check_state, not in a wait state" )
        blinkoff(white)
        blinkon(blue)

def main():
  try:
    logging.basicConfig(format='%(asctime)s %(message)s', filename='ss_not.log', level=logging.INFO)
    #initialize the global timestamps
    s_callbk.service_ts = None    #service timestamp

    #initialize buttons for input...
    print "waiting for button push"
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sbutt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(abutt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(sbutt, GPIO.RISING, callback=s_callbk, bouncetime=200)
    GPIO.add_event_detect(abutt, GPIO.RISING, callback=a_callbk, bouncetime=200)
    blinkoff(white)
    blinkon(blue)
    while True:
        sleep(30)
        #check state of buttons and led
        check_state()
    
  except KeyboardInterrupt :
    print "Aborting!"

  finally :
    GPIO.cleanup()
 
if __name__ == '__main__':
    with open('/opt/ollie/ollie_at_your_service.conf') as json_data_file:
        confdata = json.load(json_data_file)
    main()

