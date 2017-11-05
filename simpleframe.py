# File: simpleframe.py
# Description: Mirror puzzle 
#
#
# Resources:
#   https://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/
#   https://cdn-learn.adafruit.com/downloads/pdf/matrix-7-segment-led-backpack-with-the-raspberry-pi.pdf
#
# Prerequisites:
#   enable i2c and install i2c tools
#   install python dev tools
#
#
import RPi.GPIO as GPIO
import time
import datetime


# ==========================================================
#  Defines
# ==========================================================
INPUT_SLIDING_DOOR = 24 
INPUT_BOX_LID      = 25
INPUT_RED_BUTTON   = 18

OUTPUT_SLIDING_DOOR = 17

OPEN = 0
CLOSED = 1

SlidingDoorLockState = 0;
SlidingDoorOpenState = 0;
BoxLidOpenState = 0;
RedbuttonState = 0;


# ==========================================================
#  Init
# ==========================================================
#setup the GPIO using BCM numbering.  As opposed to BOARD numbering.
GPIO.setmode(GPIO.BCM)
#setup all input switches for pull-up
GPIO.setup(INPUT_SLIDING_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_BOX_LID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OUTPUT_SLIDING_DOOR, GPIO.OUT)


def Initialize():
  print("INIT: reset the audio")
  print("INIT: check for presence of files")
  print("INIT: DOOR is UNLOCKED")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
  return

def WaitToBeReady():
  ## Check for door and box to be closed
  ## before arming
  print("DEBUG RED BUTTON: " + str(GPIO.input(INPUT_RED_BUTTON)))
  print("DEBUG SLIDINGDOOR: " + str(GPIO.input(INPUT_SLIDING_DOOR)))
  print("DEBUG BOXLID: " + str(GPIO.input(INPUT_BOX_LID)))
  while GPIO.input(INPUT_BOX_LID) != CLOSED or \
        GPIO.input(INPUT_SLIDING_DOOR) != CLOSED:
    print("Waiting for door and box to be closed!");
    print("DEBUG RED BUTTON: " + str(GPIO.input(INPUT_RED_BUTTON)))
    print("DEBUG SLIDINGDOOR: " + str(GPIO.input(INPUT_SLIDING_DOOR)))
    print("DEBUG BOXLID: " + str(GPIO.input(INPUT_BOX_LID)))
    time.sleep(1)
  return

def Start():
  ## Arming!
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
  print("Door is LOCKED")


  print("Let the fun begin!")
  ## Let the fun begin!
  while GPIO.input(INPUT_BOX_LID) == CLOSED:
    # what if INPUT_SLIDING_DOOR was forced open??
    time.sleep(1)

  print("Detected Box open")
  print("Start 1 minute timer")
  countdown=60;
  print("Play audio in Mirror Room (L)")
  while ((GPIO.input(INPUT_RED_BUTTON) != 0) and (countdown > 0)):
     countdown = countdown - 1
     print("1mTimer: " + str(countdown))
     # what if INPUT_SLIDING_DOOR was forced open??
     time.sleep(1)

  if(GPIO.input(INPUT_RED_BUTTON) == 0):
    print("INPUT_RED_BUTTON was pressed")

  #TODO: Make sure timer is forced to 00:00
  print("Stop audio in Mirror Room (L)")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.LOW)
  print("LED/Door Solenoid IS OFF")
  print("Play audio in Podium Room (R)")
  while GPIO.input(INPUT_SLIDING_DOOR) == CLOSED:
      time.sleep(1)

  print("Start a 15 minute timer, and continue to play audio in Podium Room (R)") 
  countdown = 60 * 1 # 60*15 
  while(countdown > 0):
    print("15mTimer: "+ str(countdown))
    countdown = countdown - 1
    time.sleep(1)
  return

##########
# Main
###########
while True:
  Initialize()
  WaitToBeReady()
  Start()
  print("goto restart");

