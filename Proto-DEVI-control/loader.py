#=============================================================================================================================================================#

myname="loader.py"
version="v5.01-control"

#=============================================================================================================================================================#
#exit(0)
import time
from threading import Thread
from subprocess import call
def c():
    while True:
        call(['python3','/home/pi/Desktop/cooperate.py'])
        time.sleep(5)
def l():
    while True:
        call(['python3','/home/pi/Desktop/LED.py'])
        #call(['idle3','-r','/home/pi/Desktop/LED.py'])
        time.sleep(5)
def u():    
    while True:
        call(['idle3','-r','/home/pi/Desktop/unabstractor.py'])
        time.sleep(5)
    
        
Thread(target = c).start()
Thread(target = l).start()
Thread(target = u).start()
