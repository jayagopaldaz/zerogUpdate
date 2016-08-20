#=============================================================================================================================================================#

mypi='shared'
myname="update.py',"
version="v.a.1.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import os

ALL=-1

f=open(abspath+'myID','r')
myID=f.readline().strip()
f.close()        

baseURL=' https://raw.githubusercontent.com/jayagopaldaz/zerogUpdate/master/'

def get(pi,ar,i1,i2):
    if i2==ALL: i2=len(ar)
    for i in range(i1,i2): os.system('wget -O '+abspath+ar[i]+baseURL+pi+ar[i])

shared_urls = [
    'cooperate.py',
    'printer.py'
    ]

control_urls = [
    'default.mp3',
    'client_control.py',
    'globalvars.py',
    'LED.py',
    'loader.py',
    'mdns_control.py',
    'server_control.py',
    'unabstractor.py'
    ]

gui_urls = [
    'client_hmi.py',
    'loader.py',
    'mdns_hmi.py',
    'server_hmi.py',
    'zerog.py'
    ]
    
guiassets_urls = [
    'guiassets/bg.png',
    'guiassets/bglogo.png',
    'guiassets/updating.png'
    ]
guiassets_float_urls = [
    'guiassets/float/base.png',
    'guiassets/float/play.png',
    'guiassets/float/stop.png'
    ]
guiassets_main_urls = [
    'guiassets/main/kozgoxl.otf',
    'guiassets/main/60min.png',
    'guiassets/main/90min.png',
    'guiassets/main/custommin.png',
    'guiassets/main/lightoff.png',
    'guiassets/main/nonemin.png'
    ]
guiassets_settings_urls = [
    'guiassets/settings/custom.png',
    'guiassets/settings/filter.png',
    'guiassets/settings/h2o2.png',
    'guiassets/settings/levels.png',
    'guiassets/settings/rt_edit.png',
    'guiassets/settings/runtime.png',
    'guiassets/settings/settings.png',
    'guiassets/settings/trends.png',
    'guiassets/settings/volume.png'
    ]
    
get('',shared_urls,0,ALL)
if myID[-7:]=='control': get('Proto-DEVI-control/',control_urls,0,ALL)
if myID[-3:]=='gui':     get('Proto-DEVI-gui/',control_urls,0,ALL)
