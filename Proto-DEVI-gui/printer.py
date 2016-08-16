#=============================================================================================================================================================#

myname="printer.py"
version="v4.04"

#=============================================================================================================================================================#
import requests
import datetime
import time
from threading import Thread

abspath='/home/pi/Desktop/'
silent=False

ip="72.182.78.244"
#ip="canopy-os.com"

#try: logf=open(abspath+'log.txt','w')
#except: pass

myID="_"

try:
    f=open(abspath+'myID','r')
    myID=f.readline().strip()
    f.close()        
except:
    pass

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
    #print(s)
    
    if silent: return 0
    #t=str(time.time())
    #fs=t[-6]+"   :("+s+"):\r\n"
    #try: logf.write(fs)
    #except: pass
    
    #if len(s)>2048: s=s[0:2048]
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
        p("read "+fn+" from /var: "+dat)
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