#=============================================================================================================================================================#

mypi='control'
myname="client_control.py"
version="v.a.2.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import socket
import time
import json

HOST = ''
PORT = 9876
BUFSIZE = 4096

send_buffer={}
def que(d):
    global send_buffer
    
    send_buffer={**send_buffer, **d}
    
def init():
    global send_buffer
    connected=False
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((HOST,PORT))
            connected=True
            print("connected")
        except: time.sleep(5)
            
        lastSend=time.time()-.5
        while connected:
            if send_buffer and time.time()>lastSend+.5:
                b=bytes(json.dumps(send_buffer),'utf-8')
                client.send(b)
                print('client sending: '+str(b))
                send_buffer={}
                lastSend=time.time()            
            
        client.close()
        time.sleep(5)
        
if __name__=='__main__': init()
