#=============================================================================================================================================================#

mypi='control'
myname="server_control.py"
version="v.a.1.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import socket
import time

HOST = ''
PORT = 9877
BUFSIZE = 4096
ADDR = (HOST,PORT)

ready=False
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while not ready:
    try: 
        serv.bind(ADDR)
        serv.listen(5)
        ready=True
    except: 
        print('no server bind')
        time.sleep(1)

data=''
def init():
    global data
    print('control listening ...')
    while True:
        conn, addr = serv.accept()
        print('hmi client connected ... '+str(ADDR))
        while True:
            dataB = conn.recv(BUFSIZE)
            if not dataB: break
            data=dataB.decode('utf-8')
            print("control server recvd: " +data)
        conn.close()
        print('hmi client disconnected')

if __name__=='__main__': init()
