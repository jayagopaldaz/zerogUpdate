#=========================#
# SERVER FOR CONTROL SIDE #
#=========================#
import socket

HOST = ''
PORT = 9877
BUFSIZE = 4096
ADDR = (HOST,PORT)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try: serv.bind(ADDR)
except: pass
serv.listen(5)

data=''
def init():
    global data
    print('control listening ...')
    while True:
        conn, addr = serv.accept()
        print('contol client connected ... '+str(ADDR))
        while True:
            dataB = conn.recv(BUFSIZE)
            if not dataB: break
            data=dataB.decode('utf-8')
            if len(data)<50: print("server recvd: " +data)
        conn.close()
        print('client disconnected')

if __name__=='__main__': init()
