# File: simpleframe.py
# Description: Mirror puzzle 
#
#
# Resources:
#   https://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/
#   https://cdn-learn.adafruit.com/downloads/pdf/matrix-7-segment-led-backpack-with-the-raspberry-pi.pdf
#   https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#
# Prerequisites:
#   enable i2c and install i2c tools
#   install python dev tools
#
#
import RPi.GPIO as GPIO
import time
import datetime
import pygame

# ==========================================================
#  Defines
# ==========================================================
INPUT_SLIDING_DOOR = 24 
INPUT_BOX_LID      = 25
INPUT_RED_BUTTON   = 18
INPUT_RESET_BUTTON = 23
OUTPUT_SLIDING_DOOR = 17

OPEN = 0
CLOSED = 1

PODIUM_ROOM_AUDIOTRK = "OpenTheDoor.wav"
MIRROR_ROOM_AUDIOTRK = "RedButton.wav"

SlidingDoorLockState = 0
SlidingDoorOpenState = 0
BoxLidOpenState = 0
RedButtonState = 0

RedButtonPressed = False
ResetButtonPressed = False

# ==========================================================
#  Init
# ==========================================================
#setup the GPIO using BCM numbering.  As opposed to BOARD numbering.
GPIO.setmode(GPIO.BCM)
#setup all input switches for pull-up
GPIO.setup(INPUT_SLIDING_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_BOX_LID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_RESET_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OUTPUT_SLIDING_DOOR, GPIO.OUT)
MirrorRoom=""
PodiumRoom=""


def Initialize():
  global MirrorRoom
  global PodiumRoom
  global RedButtonPressed
  global ResetButtonPressed

  print("INIT: reset the audio")
  #Should turn on system mixer to 100% vol
  #amixer set PCM -- 100%
  pygame.mixer.quit()
  pygame.mixer.init()
  MirrorRoom = pygame.mixer.Sound(MIRROR_ROOM_AUDIOTRK)
  PodiumRoom = pygame.mixer.Sound(PODIUM_ROOM_AUDIOTRK)
  MirrorRoom.set_volume(1.0)
  PodiumRoom.set_volume(1.0)

  print("INIT: check for presence of files")

  print("INIT: DOOR is UNLOCKED")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH) 

  GPIO.remove_event_detect(INPUT_RESET_BUTTON) #re-initialized when program restarts/loops
  ResetButtonPressed = False
  GPIO.add_event_detect(INPUT_RESET_BUTTON, GPIO.FALLING, callback=ResetHandlerCallback, bouncetime=300)  

  GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized on when program is restarted/looped
  RedButtonPressed = False
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
    if ResetButtonPressed:
      return
    time.sleep(1)
  return

def ResetHandlerCallback(arg1):
   global ResetButtonPressed
   print("RESET DETECTED")
   ResetButtonPressed = True
   GPIO.remove_event_detect(INPUT_RESET_BUTTON) #re-initialized when program restarts/loops
   #exit()

def RedButtonCallback(arg1):
   global RedButtonPressed
   print("Interrupt: Detected button press!!!" + str(arg1))
   RedButtonPressed = True
   print("Door is UNLOCKED")
   GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
   GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized when program restarts/loops

def Start():
  global RedButtonPressed

  ## Arming!
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.LOW)
  print("Door is LOCKED")

  print("Let the fun begin!")
  ## Let the fun begin!
  while GPIO.input(INPUT_BOX_LID) == CLOSED:
    if ResetButtonPressed:

      return   # allow program to re-init
    # what if INPUT_SLIDING_DOOR was forced open??
    time.sleep(1)

  print("Detected Box open")
  print("Start 1 minute timer")
  countdown=60;
  print("Play audio in Mirror Room (L)")
  ch = MirrorRoom.play(-1)
  ch.set_volume(1.0,0) #Mirror Room on LEFT speaker
  print("Enable interrupt driven GPIO for RedButton")
  GPIO.add_event_detect(INPUT_RED_BUTTON, GPIO.FALLING, callback=RedButtonCallback, bouncetime=300)  
  while (not(RedButtonPressed) and (countdown > 0)):
     countdown = countdown - 1
     print("1mTimer: " + str(countdown))
     if ResetButtonPressed:
       return  #allow program to reset
     # what if INPUT_SLIDING_DOOR was forced open??
     time.sleep(1)

  if(RedButtonPressed):
    print("INPUT_RED_BUTTON was pressed")
  else:
    print("Timer elapsed")

  print("Door is UNLOCKED")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
  GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized on when program is restarted/looped

  #TODO: Make sure timer is forced to 00:00
  print("Stop audio in Mirror Room (L)")
  if ch.get_busy() == True:
    ch.fadeout(1000)  #in msec
    time.sleep(1)

  print("Play audio in Podium Room (R)")
  ch2 = PodiumRoom.play(-1)
  ch.set_volume(1.0, 1.0) #Podium Room plays on both LEFT and RIGHT speakers
  while GPIO.input(INPUT_SLIDING_DOOR) == CLOSED:
     if ResetButtonPressed:
       return
     time.sleep(1)

  print("Start a 15 minute timer, and continue to play audio in Podium Room (R)") 
  countdown = 60 * 1 # 60*15 
  while(countdown > 0):
    print("15mTimer: "+ str(countdown))
    countdown = countdown - 1
    if ResetButtonPressed:
       return  #allow program to reset
    time.sleep(1)
  print("Stopping all audio")
  if ch2.get_busy() == True:
     ch2.fadeout(2000)  #in msec    
  return

##########
# Main
###########
while True:
  Initialize()
  if not(ResetButtonPressed):
    WaitToBeReady()
  if not(ResetButtonPressed):
    Start()
  print("goto restart");

