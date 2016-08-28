#=============================================================================================================================================================#

mypi='shared'
myname="update.py',"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import os
import sys

END=-1

def man():
    print('usage: update.py <src> <kind> [start:[stop]] -ls')
    print('')
    print('    src      s0|s1|s2 (git|72.182.78.244|192.168.0.111)')
    print('    kind     shared|control|gui|guiassets')
    print('             float|main|settings (guiassets)')
    print('             music')
    print('    start:   first url index')
    print('    stop     last url index')
    print('    -ls      list selected urls')
    print('')
    exit(0)

if len(sys.argv)<3 and '-ls' not in sys.argv: man()
    
try:
    f=open(abspath+'myID','r')
    myID=f.readline().strip()
    f.close()        
except: myID='Spoof-DEVI-gui'

baseURL0=' https://raw.githubusercontent.com/jayagopaldaz/zerogUpdate/master/'
baseURL1=' 72.182.78.244/zerog/zerogUpdate/'
baseURL2=' 192.168.0.111/zerog/zerogUpdate/'

def get(pi,ar,i1,i2):
    if i2==END: i2=len(ar)
    for i in range(i1,i2): 
        if myID=='Spoof-DEVI-gui':
            try: print('spoofing: wget -O '+abspath+ar[i]+baseURL+pi+ar[i])
            except: 
                print('The entry was out of bounds:')
                printList()
        else:
            try: os.system('wget -O '+abspath+ar[i]+baseURL+pi+ar[i])
            except: 
                print('The entry was out of bounds:')
                printList()

shared_urls = [
    'cooperate.py',
    'printer.py',
    'update.py'
    ]

control_urls = [
    'client_control.py',
    'globalvars.py',
    'LED.py',
    'loader.py',
    'mdns_control.py',
    'server_control.py',
    'unabstractor.py'
    ]

music_urls = ['default.mp3']

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
    'guiassets/updating.png',
    'guiassets/kozgoxl.otf',
    ]
guiassets_float_urls = [
    'guiassets/float/base.png',
    'guiassets/float/play.png',
    'guiassets/float/stop.png'
    ]
guiassets_main_urls = [
    'guiassets/main/60min.png',
    'guiassets/main/90min.png',
    'guiassets/main/custommin.png',
    'guiassets/main/lightoff.png',
    'guiassets/main/nonemin.png'
    ]
guiassets_settings_urls = [
    'guiassets/settings/audio.png',
    'guiassets/settings/blank.png',
    'guiassets/settings/check.png',
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
    
url_names=['shared','control','music','gui','guiassets','float','main','settings']
urls=[shared_urls,control_urls,music_urls,gui_urls,guiassets_urls,guiassets_float_urls,guiassets_main_urls,guiassets_settings_urls]

def lsprint(ar):
    if ar==urls:
        q=0
        for i in ar: 
            print(url_names[q]+':')            
            lsprint(i)
            print('')            
            q+=1
    else:
        q=0
        for i in ar: 
            print(str(q)+')    '+i)
            q+=1        

args=sys.argv

def printList():
    if   'shared'    in args: lsprint(shared_urls)
    elif 'control'   in args: lsprint(control_urls)
    elif 'music'     in args: lsprint(music_urls)
    elif 'gui'       in args: lsprint(gui_urls)
    elif 'guiassets' in args: lsprint(guiassets_urls)
    elif 'float'     in args: lsprint(guiassets_float_urls)
    elif 'main'      in args: lsprint(guiassets_main_urls)
    elif 'settings'  in args: lsprint(guiassets_settings_urls)
    else: lsprint(urls)
    exit(0)

if '-ls' in args: printList()

if (myID[-7:]=='control' and not ('control' in args or 'music' in args)) or (myID[-3:]=='gui' and ('control' in args or 'music' in args)):
    print("Downloading into "+myID)
    a=''
    while a!='y' and a!='n': a=input("Are you sure you want to download these? (y/n) ")
    if a=='n': exit(0)  

if   's0' in args: baseURL=baseURL0
elif 's1' in args: baseURL=baseURL1
elif 's2' in args: baseURL=baseURL2
else: 
    print("Select a source:")
    print("")
    man()

for i in range(0,len(args)):
    for q in range(0,8):
        if args[i]==str(q): args[i]=str(q)+":"

i1=0
i2=END
for i in args:
    if ':' in i: 
        c=i.find(':')
        try: i1=int(i[:c])
        except: pass
        try: i2=int(i[c+1:])
        except: i2=i1+1

if   'shared'    in args: get('',shared_urls,                           i1,i2)
elif 'control'   in args: get('Proto-DEVI-control/',control_urls,       i1,i2)
elif 'music'     in args: get('Proto-DEVI-control/',music_urls,         i1,i2)
elif 'gui'       in args: get('Proto-DEVI-gui/',gui_urls,               i1,i2)
elif 'guiassets' in args: get('Proto-DEVI-gui/',guiassets_urls,         i1,i2)
elif 'float'     in args: get('Proto-DEVI-gui/',guiassets_float_urls,   i1,i2)
elif 'main'      in args: get('Proto-DEVI-gui/',guiassets_main_urls,    i1,i2)
elif 'settings'  in args: get('Proto-DEVI-gui/',guiassets_settings_urls,i1,i2)