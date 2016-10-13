#=============================================================================================================================================================#

mypi='gui'
myname="loader.py"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import time
from threading import Thread
from subprocess import call

def c():
    while True:
        call(['python3',abspath+'cooperate.py'])
        time.sleep(5)
def z():    
    while True:
        #call(['python3',abspath+'zerog.py'])
        call(['idle3','-r',abspath+'zerog.py'])
        time.sleep(5)
        
Thread(target = c).start()
Thread(target = z).start()
