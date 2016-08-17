# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='gui'
myname="server_hmi.py"
version="v.a.1.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import socket

HOST = ''
PORT = 9876
ADDR = (HOST,PORT)
BUFSIZE = 4096

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try: serv.bind(ADDR)
except: pass
serv.listen(5)

data=''
def init():
    global data
    print('listening ...')
    while True:
        conn, addr = serv.accept()
        print('client connected ... '+str(addr))
        while True:
            dataB = conn.recv(BUFSIZE)
            if not dataB: break
            data=dataB.decode('utf-8')
            #print(data)
        conn.close()
        print('client disconnected')

if __name__=='__main__': init()
