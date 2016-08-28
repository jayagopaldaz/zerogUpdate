#=============================================================================================================================================================#

mypi='shared'
myname="printer.py"
version="v.a.1.40"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import requests
import datetime
import time
from threading import Thread

ip="72.182.78.244"
#ip="canopy-os.com"

myID="_"

try:
    with open(abspath+'IDcheck', 'r') as id_file: IDcheck = id_file.readline().strip()
    with open(abspath+'myID',    'r') as id_file:    myID = id_file.readline().strip()
except: pass

def helloThread(fn,v):
    st = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    m=""
    m+="<br>"+""
    m+="<br>"+"======================================================================================================================================================"
    m+="<br>"+st
    m+="<br>"+"This is "+fn+"<br>Her version is "+v
    m+="<br>"+"------------------------------------------------------------------------------------------------------------------------------------------------------"
    p(m)

def pThread(s):
    if myID!=IDcheck: return
    try: r=requests.post('http://'+ip+'/zerog/getgui.php', params={"mode":"print","s":myID+"> "+s})
    except: pass

def goodbyeThread(fn,v):
    st = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    m="------------------------------------------------------------------------------------------------------------------------------------------------------"
    m+="<br>"+""
    m+="<br>"+st
    m+="<br>"+"                                                                                                                        Her version was "+v
    m+="<br>"+"                                                                                                                        This was "+fn
    m+="<br>"+"======================================================================================================================================================"
    m+="<br>"+""
    m+="<br>"+""
    p(m)
    
def fileUpdateThread(ip_from,fn_from,to_fn):
    try:
        r = requests.get('http://'+ip+'/zerog/'+myID+'/'+fn_from)
        f=open(abspath+to_fn,'wb')
        f.write(r.content)
        f.close()
        p("updated "+to_fn)
    except:
        pass

def foutThread(fn,dat):
    try:
        f=open(abspath+'var/'+fn,'w')
        f.write(dat)
        f.close()
        p("wrote "+fn+" to /var: "+dat)
    except:
        pass

def fin(fn):
    try:
        f=open(abspath+'var/'+fn,'r')
        dat=f.read()
        f.close()
        #p("read "+fn+" from /var: "+dat)
        return dat
    except:
        return False
        pass

##############################################
def hello(fn,v):                       Thread(target = helloThread,      args=[fn,v]).start()
def p(s):                              Thread(target = pThread,          args=[s]).start()
def goodbye(fn,v):                     Thread(target = goodbyeThread,    args=[fn,v]).start()
def fileUpdate(ip_from,fn_from,to_fn): Thread(target = fileUpdateThread, args=[ip_from,fn_from,to_fn]).start()
def fout(fn,dat):                      Thread(target = foutThread,       args=[fn,dat]).start()
#def fin(fn):                           Thread(target = finThread).start() #RETURN!!!!!!!!!!!!