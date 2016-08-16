#=============================================================================================================================================================#

myname="loader.py"
version="v5.01"

#=============================================================================================================================================================#
#exit(0)
import time
from threading import Thread
from subprocess import call
def c():
    while True:
        call(['python3','/home/pi/Desktop/cooperate.py'])
        time.sleep(5)
def z():    
    while True:
        call(['idle3',"-r",'/home/pi/Desktop/zerog.py'])
        time.sleep(5)
    
        
Thread(target = c).start()
Thread(target = z).start()
