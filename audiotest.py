import pygame
import time

#pygame.mixer.quit()
pygame.mixer.init()
#pygame.mixer.init(44100, -16, 8, 4096)

#pygame.mixer.set_num_channels(2)
MirrorRoom = pygame.mixer.Sound("RedButton.wav")
PodiumRoom = pygame.mixer.Sound("OpenTheDoor.wav")

MirrorRoom.set_volume(1.0)
ch = MirrorRoom.play()
ch.set_volume(1.0,0)
count=0;
while pygame.mixer.get_busy() == True:
    time.sleep(1)
    count = count + 1 ;
    if count == 2:
      MirrorRoom.fadeout(1000)  #in msec
    continue

PodiumRoom.set_volume(1.0)
PodiumRoom.play()
while pygame.mixer.get_busy() == True:
    continue



#pygame.mixer.set_reserved(2)




#pygame.mixer.music.set_volume(1.0)  #values from 0.0 to 1.0
#pygame.mixer.music.load("RedButton.wav")
#pygame.mixer.music.play()   #-1 = play infinitely
#while pygame.mixer.music.get_busy() == True:
#while pygame.mixer.music.get_num_channels() == 5:
#    continue
#effect = pygame.mixer.Sound("RedButton.wav")
#effect.play()



