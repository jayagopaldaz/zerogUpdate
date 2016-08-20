#=============================================================================================================================================================#

mypi='control'
myname="loader.py"
version="v.a.1.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import time
from threading import Thread
from subprocess import call

def c():
    while True:
        call(['python3',abspath+'cooperate.py'])
        time.sleep(5)
def l():
    while True:
        call(['python3',abspath+'LED.py'])
        time.sleep(5)
def u():    
    while True:
        call(['idle3','-r',abspath+'unabstractor.py'])
        time.sleep(5)
        
Thread(target = c).start()
Thread(target = l).start()
Thread(target = u).start()
