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
# Useful to run: python simpleframe.py > >(logger -p user.info) 2>&1
# Causes logging in /var/log/user
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
OUTPUT_BUTTON_LIGHT = 6

OPEN = 1
CLOSED = 0

PODIUM_ROOM_AUDIOTRK = "MirrorPush.wav"
MIRROR_ROOM_AUDIOTRK = "Button.wav"

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
GPIO.setup(OUTPUT_BUTTON_LIGHT, GPIO.OUT)

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

  print("INIT: turn off red button illumination")
  GPIO.output(OUTPUT_BUTTON_LIGHT, GPIO.LOW)

  GPIO.remove_event_detect(INPUT_RESET_BUTTON) #re-initialized when program restarts/loops
  ResetButtonPressed = False

  GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized on when program is restarted/looped
  RedButtonPressed = False
  return

def WaitToBeReady():
  ## Check for door and box to be closed
  ## before arming
  print("DEBUG RED BUTTON: " + str(GPIO.input(INPUT_RED_BUTTON)))
  print("DEBUG BOXLID: " + str(GPIO.input(INPUT_BOX_LID)))

  while GPIO.input(INPUT_BOX_LID) != CLOSED:
    lcdPrint("door", False)
    #print("Waiting for box lid to be closed!");
    #print("DEBUG RED BUTTON: " + str(GPIO.input(INPUT_RED_BUTTON)))
    #print("DEBUG BOXLID: " + str(GPIO.input(INPUT_BOX_LID)))
    if GPIO.input(INPUT_RESET_BUTTON) == False:
      return
    time.sleep(1)
  return

def ResetHandlerCallback(arg1):
   global ResetButtonPressed
   GPIO.remove_event_detect(INPUT_RESET_BUTTON) #re-initialized when program restarts/loops
   print("RESET DETECTED" + str(arg1))
#   if (GPIO.input(INPUT_RESET_BUTTON) == True):
#       print("RESET CONFIRMED")
#      ResetButtonPressed = True
#   else:
#      print("RESET NOT CONFIRMED. No op")
#      GPIO.add_event_detect(INPUT_RESET_BUTTON, GPIO.FALLING, callback=RedButtonCallback, bouncetime=600)
   ResetButtonPressed = True
   #exit()

def RedButtonCallback(arg1):
   global RedButtonPressed
   print("Interrupt: Detected button press!!!" + str(arg1))
   print("Door is UNLOCKED")
   print("resetstate = " + str(ResetButtonPressed))
   #GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
   GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized when program restarts/loops
   RedButtonPressed = True

def lcdPrintHex(hex):
  global colon
  colon = False
  display.clear()
  display.print_hex(hex)
  display.set_colon(colon)
  display.write_display()
  return

def lcdPrintTime(secs):
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


# Digit value to bitmask mapping:
MY_DIGIT_VALUES = {
    ' ': 0b00000000,
    '-': 0b10000000,
    'd': 0b01011110,
    'o': 0b01011100,
    'r': 0b01010000,
    'P': 0b01110011,
    'U': 0b00111110,
    'S': 0b01101101,
    'H': 0b01110110,


    '-': 0x40,
    '0': 0x3F,
    '1': 0x06,
    '2': 0x5B,
    '3': 0x4F,
    '4': 0x66,
    '5': 0x6D,
    '6': 0x7D,
    '7': 0x07,
    '8': 0x7F,
    '9': 0x6F,
    'A': 0x77,
    'B': 0x7C,
    'C': 0x39,
    'D': 0x5E,
    'E': 0x79,
    'F': 0x71
}

def lcdPrint(word, colon):
  #print(word)
  display.set_digit_raw(0, MY_DIGIT_VALUES.get(word[0]))
  display.set_digit_raw(1, MY_DIGIT_VALUES.get(word[1]))
  display.set_digit_raw(2, MY_DIGIT_VALUES.get(word[2]))
  display.set_digit_raw(3, MY_DIGIT_VALUES.get(word[3]))
  display.set_colon(colon)
  display.write_display()
  return


def lcdBlinkZero():
  global colon
 
  display.clear()

  if colon:
     display.set_digit(0, 0)
     display.set_digit(1, 0)
     display.set_digit(2, 0)
     display.set_digit(3, 0)

  display.set_colon(colon)
  display.write_display()
  colon = not colon
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
    if GPIO.input(INPUT_RESET_BUTTON) == False:
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
  GPIO.add_event_detect(INPUT_RED_BUTTON, GPIO.FALLING, callback=RedButtonCallback, bouncetime=700)
  while (not(RedButtonPressed) and (countdown > 0)):
     GPIO.output(OUTPUT_BUTTON_LIGHT, GPIO.HIGH)

     lcdPrintTime(countdown)
     time.sleep(.5)
     lcdPrintTime(countdown)
     time.sleep(.5)
     #print("1mTimer: " + str(countdown))
     if GPIO.input(INPUT_RESET_BUTTON) == False:
        return  #allow program to reset
     # what if INPUT_SLIDING_DOOR was forced open??
#     time.sleep(1)
     countdown = countdown - 1

  if(RedButtonPressed):
    print("INPUT_RED_BUTTON was pressed")
  else:
    print("Timer elapsed")

  print("Unlocking the Door")
  GPIO.output(OUTPUT_SLIDING_DOOR, GPIO.HIGH)
  #GPIO.remove_event_detect(INPUT_RED_BUTTON) #re-initialized on when program is restarted/looped

  #TODO: Make sure timer is forced to 00:00
  lcdBlinkZero()

  print("Stop audio in Mirror Room (L)")
  if ch.get_busy() == True:
    ch.fadeout(1000)  #in msec
    time.sleep(1)

  print("Play audio in Podium Room (R)")
  ch2 = PodiumRoom.play(-1)
  ch2.set_volume(1.0, 1.0) #Podium Room plays on both LEFT and RIGHT speakers

  print("Loop forever and ccontinue to play audio in Podium Room (R)") 
  while True:
    #print("Looping forever, until reset switch")
    if GPIO.input(INPUT_RESET_BUTTON) == False:
       return  #allow program to reset
    #lcdBlinkZero()
    lcdPrint("PUSH", False)
    time.sleep(0.5)

##########
# Main
###########
try:
  while True:
    Initialize()
    if not(GPIO.input(INPUT_RESET_BUTTON) == False):
      time.sleep(1)
      WaitToBeReady()
    if not(GPIO.input(INPUT_RESET_BUTTON) == False):
      Start()
except KeyboardInterrupt:
    # do something for ctrl-c events
    print("") 
finally:
   GPIO.cleanup()

