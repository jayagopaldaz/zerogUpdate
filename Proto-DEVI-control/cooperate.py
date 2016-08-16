#=============================================================================================================================================================#

myname="cooperate.py"
version="v3.21 "
version="v3.22 #NONONONONONO "

#=============================================================================================================================================================#
import sys
abspath='/home/pi/Desktop/'
sys.path.insert(0, abspath)
import printer
printer.hello(myname,version)

ip=printer.ip

try:
    printer.fileUpdate(ip,'IDcheck','IDcheck')
    #NONONONONONO printer.fileUpdate(ip,myname,myname)
    with open(abspath+'IDcheck', 'r') as id_file: IDcheck = id_file.readline().strip()
    with open(abspath+'myID',    'r') as id_file:    myID = id_file.readline().strip()
except:
    pass
    
#=============================================================================================================================================================#

#filesToGet=[]
filesToGet=[
#    "loader.py",
#    "update.py",                   #this file can become an interrupt while it transfers?!?!?!?
#    "unabstractor.py",
#    "printer.py",
#    "fcserver.json",
#
#    "guiassets/updating.png",
#    "guiassets/bg.png",
#    "guiassets/bglogo.png",
#
#    "guiassets/float/play.png",
#    "guiassets/float/stop.png",
#
#    "guiassets/settings/filter.png",
#    "guiassets/settings/settings.png",
#    "guiassets/settings/h2o2.png",
#    "guiassets/settings/volume.png",
#    "guiassets/settings/tester.jpg"]
#
#    "guiassets/main/60min.png", 
#    "guiassets/main/90min.png", 
#    "guiassets/main/custommin.png", 
#    "guiassets/main/nonemin.png"]
#
#    "splash.png", #?
#    "asplashscreen",
#
#    "unabstract/mdns_control.py",
#    "unabstract/client_control.py",
#    "unabstract/server_control.py",
#    "unabstract/unabstractor.py",
#    "mdns_hmi.py",
#    "client_hmi.py",
#    "server_hmi.py",
#    "zerog.py"
     ]

#=============================================================================================================================================================#

msg="                                  myID---from---"+myID+" || I || "+IDcheck+"---to---IDcheck"
printer.p(msg)

#----------------------------------------------------------------------I--------------------------------------------------------------------------------------#
import threading
import requests
import pyautogui
import time

from PIL import Image, ImageFile
#from subprocess import call
from threading import Thread

pyautogui.FAILSAFE=False
ImageFile.MAXBLOCK = 2**20
alive=True

start=time.time()
req=0

def checkOut():
    #NONONONONONO2 printer.fileUpdate(ip,myname,myname)
    printer.p(msg+"<br>"+msg+"<br>"+msg)

    #if printer.fin('floatInProgress')=='False':
    #printer.p(myname+"t-start:"+str(time.time()-start))
    #    printer.p(myname+" ... 10" second delay")
    #    time.sleep(10)
    #while time.time()-start<20: continue   
    printer.goodbye(myname,version)

def ioThread():
    OOO="       "
    printer.p(OOO+"ioThread === checking in...")
    global req
    global alive
    l=0
    r=0
    while alive:
        if myID==IDcheck:
            #if time.time()-start>20: alive=False #autorestart
            try:
                response=requests.post('http://'+ip+'/zerog/getgui.php', params={"mode":"r"})
                j=response.json()
          
                req=int(j['req'])
                if req==-1: alive=False
                if req!=1: continue
                o_l=l
                o_r=r
                x=int(j['x'])
                y=int(j['y'])
                l=int(j['l'])
                #k=int(j['k'])
                k=j['k']
                r=int(j['r'])
                
                printer.p(OOO+"ioThread === xyzlr:"+str(x)+","+str(y)+","+str(l)+","+str(r)+",  k:"+str(k)+",  req:"+str(req))
                
                pyautogui.moveTo(x,y,0)
                if l==1 and o_l!=1: pyautogui.mouseDown();
                elif l==0 and o_l!=0: pyautogui.mouseUp();
                
                if r==1 and o_r!=1: pyautogui.mouseDown(button='right');
                elif r==0 and o_r!=0: pyautogui.mouseUp(button='right');
                
                if k=='{{reboot}}': os.system('reboot')     #pyautogui.press('ctrl','x');
                elif k!='0':
                    pyautogui.typewrite(k);
                    pyautogui.press('enter');
                
                time.sleep(1)
            except:
                pass
        else: time.sleep(5)
        
    printer.p(OOO+"ioThread === ...checking out")
    
#----------------------------------------------------------------------I--------------------------------------------------------------------------------------#
def screenshotThread():
    OOO="                                           "
    global req
    global alive
    printer.p(OOO+"screenshotThread === checking in...")
    n=0
    while alive:
        #if time.time()-start>20: alive=False #autorestart
        if myID==IDcheck and req==1:
            #pyautogui.screenshot("screenshot.png")
            img=pyautogui.screenshot()
            try:
                img.save(abspath+"screenshot.jpg", "JPEG", quality=0, optimize=True, progressive=False)
                n+=1
            except:
                printer.p(OOO+"screenshotThread === couldn't save it?")
                pass
                
            try:
                files = {'media': open(abspath+'screenshot.jpg', 'rb')}
                r=requests.post('http://'+ip+'/zerog/upload.php', files=files)
                printer.p(OOO+"screenshotThread === screenshot#"+str(n))
            except:
                printer.p(OOO+"screenshotThread === couldn't upload it?")
                pass
        else: time.sleep(5)
        
    printer.p(OOO+"screenshotThread === ...checking out")
    
#----------------------------------------------------------------------I--------------------------------------------------------------------------------------#
def getfileThread():
    global filesToGet
    global alive
    OOO="                                                                                 "
    printer.p(OOO+"getfileThread === checking in...")
    if myID==IDcheck:
        printer.p(OOO+"getfileThread === ID Checks out")        
        for fn in filesToGet:
            printer.fileUpdate(ip,fn,fn)
            printer.p(OOO+"getfileThread === file receiver:"+fn)
            continue
    printer.p(OOO+"getfileThread === ...checking out")
    #while alive:
    #    if time.time()-start>20: alive=False #autorestart
    #    continue
    
#----------------------------------------------------------------------I--------------------------------------------------------------------------------------#
if __name__ == '__main__':
    Thread(target = getfileThread).start()
    Thread(target = ioThread).start()
    Thread(target = screenshotThread).start()
    
    #timeout=24*60*60
    while alive:
        printer.p("   "+myname+" > t:"+str(round(time.time()-start)))
        time.sleep(10)

        printer.fileUpdate(ip,'IDcheck','IDcheck')
        f=open(abspath+'IDcheck','r')
        IDcheck=f.readline().strip()
        f.close()

        #if myID!=IDcheck or time.time()-start>timeout: alive=False #autorestart
        if myID!=IDcheck: alive=False #autorestart
        continue
    checkOut()
#----------------------------------------------------------------------I--------------------------------------------------------------------------------------#

#=============================================================================================================================================================#
