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
from Adafruit_LED_Backpack import SevenSegment

# ==========================================================
#  Defines
# ==========================================================
INPUT_SLIDING_DOOR = 24 
INPUT_BOX_LID      = 25
INPUT_RED_BUTTON   = 18
INPUT_RESET_BUTTON = 23
OUTPUT_SLIDING_DOOR = 17

OPEN = 1
CLOSED = 0

PODIUM_ROOM_AUDIOTRK = "OpenTheDoor.wav"
MIRROR_ROOM_AUDIOTRK = "RedButton.wav"

SlidingDoorLockState = 0
SlidingDoorOpenState = 0
BoxLidOpenState = 0
RedButtonState = 0

RedButtonPressed = False
ResetButtonPressed = False

colon = False

# ==========================================================
#  Init
# ==========================================================
#setup the GPIO using BCM numbering.  As opposed to BOARD numbering.
GPIO.setmode(GPIO.BCM)
#setup all input switches for pull-up
#not used GPIO.setup(INPUT_SLIDING_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_BOX_LID, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INPUT_RESET_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OUTPUT_SLIDING_DOOR, GPIO.OUT)
MirrorRoom=""
PodiumRoom=""
# Create display instance on default I2C address (0x70) and bus number.
display = SevenSegment.SevenSegment()

def initDisplay():
  display.begin()
  display.clear()
  display.set_invert(False)
  colon = False
#  display.print_float(0, decimal_digits=0, justify_right=True)
  display.set_colon(colon)
  display.write_display()
  return

def Initialize():
  global MirrorRoom
  global PodiumRoom
  global RedButtonPressed
  global ResetButtonPressed
  global colon

  print("INIT: display init")
  initDisplay()

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

  print("INIT: Unlocking door")
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
  print("DEBUG BOXLID: " + str(GPIO.input(INPUT_BOX_LID)))
  while GPIO.input(INPUT_BOX_LID) != CLOSED:
    lcdPrintHex(0x071d)
    print("Waiting for box lid to be closed!");
    print("DEBUG RED BUTTON: " + str(GPIO.input(INPUT_RED_BUTTON)))
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

def lcdPrintHex(hex):
  global colon
  colon = False
  display.clear()
  display.print_hex(hex)
  display.set_colon(colon)
  display.write_display()
  return

def lcdPrint(secs):
  global colon
  display.clear()
  #display.print_float(secs, decimal_digits=0, justify_right=True)
  display.set_digit(0, int(secs/60/10))
  display.set_digit(1, (secs/60) % 10)
  display.set_digit(2, int(secs%60)/10)
  display.set_digit(3, (secs%60) % 10)
  display.set_colon(colon)
  display.write_display()
  colon = not colon
  return

def lcdBlinkZero():
  global colon
 
  colon = True
  display.clear()
  display.set_digit(0, 0)
  display.set_digit(1, 0)
  display.set_digit(2, 0)
  display.set_digit(3, 0)
  display.set_colon(colon)
  display.write_display()  
 # display.setBlinkRate(3)
  return

def Start():
  global RedButtonPressed
  global colon

  ## clear the display
  initDisplay()

  ## Arming!
  print("Locking the Door!")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.LOW)

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
     lcdPrint(countdown)
     print("1mTimer: " + str(countdown))
     if ResetButtonPressed:
       return  #allow program to reset
     # what if INPUT_SLIDING_DOOR was forced open??
     time.sleep(1)
     countdown = countdown - 1

  if(RedButtonPressed):
    print("INPUT_RED_BUTTON was pressed")
  else:
    print("Timer elapsed")

  print("Unlocking the Door")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
  GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized on when program is restarted/looped

  #TODO: Make sure timer is forced to 00:00
  lcdBlinkZero()
  
  print("Stop audio in Mirror Room (L)")
  if ch.get_busy() == True:
    ch.fadeout(1000)  #in msec
    time.sleep(1)

  print("Play audio in Podium Room (R)")
  ch2 = PodiumRoom.play(-1)
  ch.set_volume(1.0, 1.0) #Podium Room plays on both LEFT and RIGHT speakers

  print("Loop forever and ccontinue to play audio in Podium Room (R)") 
  while True:
    #print("Looping forever, until reset switch")
    if ResetButtonPressed:
       return  #allow program to reset
    time.sleep(1)

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

