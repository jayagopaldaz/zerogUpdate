#=============================================================================================================================================================#

mypi='gui'
myname="server_hmi.py"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import socket
import time

HOST = ''
PORT = 9876
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
        time.sleep(5)

data=''
def init():
    global data
    print('hmi listening ...')
    while True:
        conn, addr = serv.accept()
        print('control client connected ... '+str(addr))
        while True:
            dataB = conn.recv(BUFSIZE)
            if not dataB: break
            data=dataB.decode('utf-8')
            if "fthermo" not in data: print("hmi server recvd: " +data)
            #print("hmi server recvd: " +data)
        conn.close()
        print('control client disconnected')

if __name__=='__main__': init()
