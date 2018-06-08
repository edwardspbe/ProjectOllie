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
import logging
from time import sleep
from datetime import datetime

#Raspberry Pi GPIO pins used to set/change colours on 
sbutt = 21   #service button
abutt = 26   #admin button
red   = 17
blue  = 27
green = 22
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
    (red,small,5), 
    (yellow,small,5), 
    (blue,small,5), 
    (green,tiny,300), 
)
alreadywaiting= (
    (green,tiny,50), 
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
            blinkoff(colour)
            sleep(time)


#called when admin button is tripped
def a_callbk():
    pass

#called when service button is tripped
def s_callbk(pin):
    with open('/opt/ollie/ollie_at_your_service.conf') as json_data_file:
        confdata = json.load(json_data_file)
    
    #this is important in case someone is pushing the button non-stop
    if s_callbk.service_ts != None :
        delta = datetime.now() - s_callbk.service_ts
        if delta.seconds > SmsQuietPeriod :
            s_callbk.service_ts = None
        else :
            logging.info("service request while in WAIT-PERIOD.")
            do_blink_loop(alreadywaiting)
            GPIO.cleanup()
            return
            
    logging.info("service requested..  sending SMS to %s." % confdata['numbers'])
    answer=[]
    for name in confdata['numbers'] :
        answer = requests.post('https://textbelt.com/text', {
                               'phone': confdata['numbers'][name],
                               'message': 'Ollie needs help at the Snack Shack',
                               'key': confdata['TextBelt']['key'],
        })
        print "SMS sent to %s" % name
        obj = json.loads(answer.content)
        if obj['success'] == True :
            logging.info("SMS Send Successful!")
            do_blink_loop(working)
            s_callbk.service_ts = datetime.now()
            blinkon(green)
            s_callbk.led_state = green
        else :
            logging.info("SMS SEND ERROR: [%s]" % obj['error'])
            do_blink_loop(errorstate)
            do_blinkon(red)
            s_callbk.led_state = red
            break

#make sure we are operating properly and LEDs are indicating ready... 
def check_state():
    if s_callbk.service_ts != None :
        delta = datetime.now() - s_callbk.service_ts
        if delta.seconds > SmsQuietPeriod :
            s_callbk.service_ts = None
            do_blinkoff(white)
            
    pass


def main():
  try:
    logging.basicConfig(format='%(asctime)s %(message)s', filename='ss_not.log', level=logging.INFO)
    #initialize the global timestamps
    s_callbk.service_ts = None    #service timestamp

    #initialize buttons for input...
    print "waiting for button push"
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sbutt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(abutt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(sbutt, GPIO.RISING, callback=s_callbk, bouncetime=200)
    GPIO.add_event_detect(abutt, GPIO.RISING, callback=a_callbk, bouncetime=200)
    do_blinkon(blue)
    while True:
        sleep(30)
        #check state of buttons and led
        check_state()
    
  except KeyboardInterrupt :
    print "Aborting!"

  finally :
    GPIO.cleanup()
 
if __name__ == '__main__':
    main()

