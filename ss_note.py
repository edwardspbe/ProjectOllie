#-------------------------------------------------------------------------------
# Name:        ss_note.py
# Purpose      Snack Shack notifications python module for automating snack shack.
#
# Author:      paul.e@rogers.com
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
red   = 19
blue  = 20
green = 21
yellow = (red,green)
cyan  = (blue,green)
magenta = (red,blue)
white = (red,blue,green)
#blink times
large=1
medium=0.5
small=0.25
tiny=0.1

RESENDSMSPERIOD = 300    #no of seconds before sending another SMS mesg...

#led blink cycles
wait = (blue)
errorstate = (
    (red,small,25), 
)
working = (
    (yellow,small,5), 
    (cyan,small,5), 
    (white,small,5), 
    (green,tiny,30), 
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

     
def main():
  try:
    timestamp = None
    logging.basicConfig(format='%(asctime)s %(message)s', filename='ss_not.log', level=logging.INFO)

    while True :
        #wait for input from button...
        print "waiting for button push"
        while( True ):
            GPIO.setmode(GPIO.BCM)
            blinkon(wait)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            pin = GPIO.wait_for_edge(4, GPIO.FALLING)
            blinkoff(wait)
            blinkon(red)
            if pin == 4 :
                if timestamp != None :
                    delta = datetime.now() - timestamp
                    if delta.seconds > RESENDSMSPERIOD :
                        timestamp = None
                    else :
                        logging.info("service request while in WAIT-PERIOD.")
                        do_blink_loop(alreadywaiting)
                        GPIO.cleanup()
                        continue
                        
                logging.info("service requested..  sending SMS.")
                answer = requests.post('https://textbelt.com/text', {
                                       'phone': '6132408250',
                                       'message': 'Hello from Ollie',
                                       'key': 'textbelt',
                })
                obj = json.loads(answer.content)
                if obj['success'] == True :
                    logging.info("SMS Send Successful!")
                    do_blink_loop(working)
                    timestamp = datetime.now()
                else :
                    logging.info("SMS SEND ERROR: [%s]" % obj['error'])
                    do_blink_loop(errorstate)
            #this is important in case someone is pushing the button non-stop
            GPIO.cleanup()

  except KeyboardInterrupt :
    print "Aborting!"

  finally :
    GPIO.cleanup()
 
if __name__ == '__main__':
    main()

