'''
Ollies Snack Shack notification system

Simple push button implemented on a raspberry pi (zero).
When the button is pushed an SMS notification is sent to the
"on-call" list of phone numbers indicating service required 
at the snack-shack.  

'''

import sys
import RPi.GPIO as GPIO
from time import sleep
import requests
import json

sleep(0.5)
red   = 19
blue  = 20
green = 21
yellow = (red,green)
cyan  = (blue,green)
magenta = (red,blue)
white = (red,blue,green)

large=1
medium=0.5
small=0.25
tiny=0.1

#led blink cycles
wait = (blue)
errorstate = (
    (red,small,25), 
)
working = (
    (red,small,5), 
    (yellow,small,5), 
    (white,small,5), 
    (green,small,5), 
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

def main():
  try:
    raw_input("Ready?")
    print "waiting for button push"
    while( True ):
        GPIO.setmode(GPIO.BCM)
        blinkon(wait)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pin = GPIO.wait_for_edge(4, GPIO.FALLING)
        blinkoff(wait)
        if pin == 4 :
            answer = requests.post('https://textbelt.com/text', {
                  'phone': '6132408250',
                    'message': 'Hello from Ollie',
                      'key': 'textbelt',
                      })
            obj = json.loads(answer.content)
            if obj['success'] == True :
                print "Yeah!"
                for colour,time,repeat in working:
                    for i in range(repeat) :
                        blinkon(colour)
                        sleep(time)
                        blinkoff(colour)
                        sleep(time)
            else :
                print "Uh OH!  ERROR: [%s]" % obj['error']
                for colour,time,repeat in errorstate:
                    for i in range(repeat) :
                        blinkon(colour)
                        sleep(time)
                        blinkoff(colour)
                        sleep(time)
        GPIO.cleanup()

  except KeyboardInterrupt :
    print "\Quitting"
    return

  finally:
    GPIO.cleanup()


main()

