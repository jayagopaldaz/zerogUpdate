# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='gui'
myname="client_hmi.py"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import socket
import time

HOST = ''
PORT = 9877
BUFSIZE = 4096

pending=False

def send(d):
    global dat,pending
    if 'reinit' not in d: print('client sending: '+d)
    dat=bytes(d,'UTF-8')
    pending=True
    
def init():
    global pending

    connected=False
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((HOST,PORT))
            connected=True
        except: time.sleep(5)
            
        while connected:
            if pending:
                try: client.send(dat)
                except: connected=False
                pending=False
        
        client.close()
        time.sleep(5)
        
if __name__=='__main__': init()
