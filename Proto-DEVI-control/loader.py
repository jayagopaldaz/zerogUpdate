#=============================================================================================================================================================#

mypi='control'
myname="loader.py"
version="v.a.2.00"
abspath='/home/pi/Desktop/'
TESTMODE=not True

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
        #call(['python3',abspath+'LED.py'])
        call(['idle3','-r',abspath+'LED.py'])
        time.sleep(5)
def u():    
    while True:
        call(['idle3','-r',abspath+'unabstractor.py'])
        time.sleep(5)

def t():    
    while True:
        call(['idle3','-r',abspath+'test.py'])
        time.sleep(5)

if TESTMODE:        
    Thread(target = t).start()
    time.sleep(5)
    Thread(target = l).start()

else:
    Thread(target = c).start()
    Thread(target = u).start()
    time.sleep(20)
    Thread(target = l).start()
