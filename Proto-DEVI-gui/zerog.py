# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='gui'
myname="zerog.py"
version="v.a.1.22"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import printer
import os
import math
import time
import pygame
import json
from pygame.locals import *
from threading import Thread
import server_hmi as server
import client_hmi as client

printer.hello(myname,version)

def socketboot():
    import mdns_hmi as mdns
    control_ip= (mdns.info.properties[b'eth0']).decode('utf-8')
    my_ip=mdns.ip
    print("control's ip: "+control_ip)
    client.HOST=control_ip
    while not server.ready: continue
    Thread(target=server.init).start()
    Thread(target=client.init).start()

#Thread(target=socketboot).start()
socketboot()

pygame.init()
pygame.display.init()
pygame.display.set_caption("Float Control "+version)
pygame.mouse.set_visible(0)
pygame.font.init()

screen=pygame.display.set_mode((800, 480), NOFRAME|RLEACCEL)
stage=pygame.Surface((800,480))

#================================ SOME GLOBAL VARIABLES ================================                
debugstring=''
t_offset=0
max_vol=.65
ct=78.1
old_cur_temp=0
cur_temp=0
targ_temp=93.5
pH_lev=7.0
ORP_lev=200
specgrav_lev=1.25
lbssalt_lev=0
p_heater1234="----"
thermoString=""
remote=False
init=True
even=False

last_rt=time.time()
rt_total_start=1468092055

vOffset=26
minAlpha=25
gradalpha=0
gradsurface=False
stepperSpeed=0
fade=1
prog=0
lastPrint=0
lastsend=0
floatelapsed=0
status_str="READY"
phase=-3
stopcount=False
lightMode=True
alertMode=False
colorthereapymode=False
timeleft_str="READY"
wlanSorted=[]
ssidSelect=False
pwdSelect=''

#sleepMode=False
try: colvals=json.loads(printer.fin('colvals'))
except: colvals={"colval_r":1.0,"colval_g":0.7,"colval_b":1.0,"colval_w":1.0}
print("this is .fin colvals:"+str(colvals))

PHASE_NONE   = -1
PHASE_SHOWER = 0
PHASE_FADE1  = 1
PHASE_FLOAT  = 2
PHASE_FADE2  = 3
PHASE_WAIT   = 4
PHASE_PLO    = 5
PHASE_PHI    = 6
PHASE_UV     = 70
PHASE_H2O2   = 800
PHASE_SHUTOFF= -2

floatstart=time.time()
floatInProgress=False
fout_customMFadein=False
fout_customMFadeout=False
fout_customLFadein=False
fout_customLFadeout=False
fout_customDuration=False

fout_currentTemperature=False
fout_targetTemperature=False
fout_rt_max=False
fout_rt_thresh=False
fout_pH=False
fout_ORP=False
fout_specgrav=False
fout_lbs=False
custom_duration=120
max_vol=.65
overrideWarning=False

min_shower=5
min_fade1 =1
min_float =58
min_fade2 =1
min_wait  =3
min_plo   =3
min_phi   =20
min_uv    =20
min_h2o2  =1/60*10

min_fade1_m =1
min_fade2_m =1
fadeinmusic=False

totalDuration=-1
countdown_num=3
countdownstart=time.time()

_shower=0
_fade1 =0
_float =0
_fade2 =0
_wait  =0
_plo   =0
_filter=0

mainscreen        = True
floatscreen       = False
playfloat         = False
settingsscreen    = False
customscreen      = False
levelsscreen      = False
wifiscreen        = False
runtimescreen     = False
r1screen          = False
r2screen          = False
r3screen          = False
trendsscreen      = False
manualfilter      = False
manualh2o2        = False
floatpreset       = -1
filter_runtime    = 0

min_fade1          = float(printer.fin('min_fade1'))
min_fade2          = float(printer.fin('min_fade2'))
min_fade1_m        = float(printer.fin('min_fade1_m'))
min_fade2_m        = float(printer.fin('min_fade2_m'))
floatstart         = float(printer.fin('floatstart'))
custom_duration    = float(printer.fin('custom_duration'))
targ_temp          = float(printer.fin('targ_temp'))
pH_lev             = float(printer.fin('pH_lev'))   
ORP_lev            = float(printer.fin('ORP_lev'))  
specgrav_lev       = float(printer.fin('specgrav_lev'))  
lbssalt_lev        = float(printer.fin('lbssalt_lev'))  
t_offset           = float(printer.fin('t_offset'))  
filter_runtime     = float(printer.fin('filter_runtime'))
uvbulb_runtime     = float(printer.fin('uvbulb_runtime'))
rt_solution_start  = float(printer.fin('rt_solution_start'))
rt_filter_max      = float(printer.fin('rt_filter_max'))
rt_uvbulb_max      = float(printer.fin('rt_uvbulb_max'))
rt_solution_max    = float(printer.fin('rt_solution_max'))
rt_filter_thresh   = float(printer.fin('rt_filter_thresh'))
rt_uvbulb_thresh   = float(printer.fin('rt_uvbulb_thresh'))
rt_solution_thresh = float(printer.fin('rt_solution_thresh'))

if not rt_solution_start: rt_solution_start=rt_total_start
if not rt_filter_max:   rt_filter_max   =  200
if not rt_uvbulb_max:   rt_uvbulb_max   = 2000
if not rt_solution_max: rt_solution_max = 3000

if not rt_filter_thresh:   rt_filter_thresh   = .9
if not rt_uvbulb_thresh:   rt_uvbulb_thresh   = .9
if not rt_solution_thresh: rt_solution_thresh = .9


fout_currentTemperature=False
fout_targetTemperature=False
fout_pH=False
fout_ORP=False


floatpreset     = float(printer.fin('floatpreset'))
max_vol         = float(printer.fin('max_vol'))

if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)

if printer.fin('floatInProgress')=="True": floatInProgress= True
if printer.fin('floatscreen')    =="True": floatscreen    = True
if printer.fin('playfloat')      =="True": playfloat      = True
if printer.fin('settingsscreen') =="True": settingsscreen = True
if printer.fin('customscreen')   =="True": customscreen   = True
if printer.fin('levelsscreen')   =="True": levelsscreen   = True
if printer.fin('wifiscreen')     =="True": wifiscreen     = True
if printer.fin('runtimescreen')  =="True": runtimescreen  = True
if printer.fin('trendsscreen')   =="True": trendsscreen   = True
if printer.fin('manualfilter')   =="True": manualfilter   = True
if printer.fin('manualh2o2')     =="True": manualh2o2     = True
reloaded=True

if floatpreset==60: min_float=60-(min_fade1+min_fade2)
if floatpreset==90: min_float=90-(min_fade1+min_fade2)
if floatpreset==-1: min_float=math.floor(custom_duration)-(min_fade1+min_fade2)



gradBarWidth=800
gradBarHeight=108+5
gradBarLeft=0#(800-gradBarWidth)/2+5
gradBarTop=210

#================================ LOAD IMAGES ================================
#logo   =pygame.image.load(abspath+'guiassets/logo.png')
bglogo   =pygame.image.load(abspath+'guiassets/bglogo.png')
bg       =pygame.image.load(abspath+'guiassets/bg.png')

nonemin  =pygame.image.load(abspath+'guiassets/main/nonemin.png')
sixtymin =pygame.image.load(abspath+'guiassets/main/60min.png')
ninetymin=pygame.image.load(abspath+'guiassets/main/90min.png')
custommin=pygame.image.load(abspath+'guiassets/main/custommin.png')
lightoff =pygame.image.load(abspath+'guiassets/main/lightoff.png')

play     =pygame.image.load(abspath+'guiassets/float/play.png')
stop     =pygame.image.load(abspath+'guiassets/float/stop.png')

settings =pygame.image.load(abspath+'guiassets/settings/settings.png')
custom   =pygame.image.load(abspath+'guiassets/settings/custom.png')
filter   =pygame.image.load(abspath+'guiassets/settings/filter.png')
h2o2     =pygame.image.load(abspath+'guiassets/settings/h2o2.png')
volume   =pygame.image.load(abspath+'guiassets/settings/volume.png')
levels   =pygame.image.load(abspath+'guiassets/settings/levels.png')
wifi     =pygame.image.load(abspath+'guiassets/settings/trends.png')
runtime  =pygame.image.load(abspath+'guiassets/settings/runtime.png')
rt_edit  =pygame.image.load(abspath+'guiassets/settings/rt_edit.png')
trends   =pygame.image.load(abspath+'guiassets/settings/trends.png')
check    =pygame.image.load(abspath+'guiassets/settings/check.png')

blackout     =pygame.Surface((800,480))
amber        =pygame.Surface((800,480))
progbar      =pygame.Surface((800,10))
reasonSurface=pygame.Surface((800,480))                

#================================ SOME MORE GLOBAL VARIABLES ================================                
blackout.fill((0,0,0))
amber.fill((255,64,16))

alive=True
touched=False
go=False
json_obj={}

oldTarg0=0
oldTarg1=0
oldTarg2=0
oldTarg3=0
oldTarg4=0
layer0=nonemin
layer1=False
layer2=False
layer3=False
layer4=False
start=time.time()
gradalpha=64
alpha0=255
alpha1=255
alpha2=255
alphaStep=5

screens_BEGIN=screens_END=0

#================================ BUTTON RECTANGLES ================================                
exit_button      = pygame.Rect(0, 0, 40, 40)

sixtymin_button  = pygame.Rect(116, 204-vOffset, 140,140)
ninetymin_button = pygame.Rect(322, 204-vOffset, 140,140)
custommin_button = pygame.Rect(528, 204-vOffset, 140,140)

back_button      = pygame.Rect( 56,  78-vOffset, 76,76)
play_button      = pygame.Rect(190, 340-vOffset, 94,98)
stop_button      = pygame.Rect(505, 340-vOffset, 94,98)
sleep_button     = pygame.Rect( 60, 352-vOffset, 76,76)

gear_button      = pygame.Rect(668, 352-vOffset, 76,76)

therm_button     = pygame.Rect( 60, 352-vOffset, 76,76)
wifi_button      = pygame.Rect(668,  78-vOffset, 76,76)
runtime_button   = pygame.Rect(668, 78+(352-78)/2-vOffset, 76,76)
trends_button    = pygame.Rect(668, 352-vOffset, 76,76)
levels_button    = pygame.Rect(0,0,1,1)

filter_button    = pygame.Rect(170,  80-vOffset, 160,160)
h2o2_button      = pygame.Rect(460,  80-vOffset, 160,160)
volume_button    = pygame.Rect(170-20, 280-vOffset, 160+30,160)
custom_button    = pygame.Rect(400, 270-vOffset, 270,160)

cmusicin_button  = pygame.Rect(160, 130-vOffset, 245,100)
cmusicout_button = pygame.Rect(160, 230-vOffset, 245,100)
clightin_button  = pygame.Rect(405, 130-vOffset, 245,100)
clightout_button = pygame.Rect(405, 230-vOffset, 245,100)
clength_button   = pygame.Rect(160, 360-vOffset, 245,100)
ccol_button      = pygame.Rect(660,  55-vOffset,  95,390)
ctherapy_button  = pygame.Rect(410, 370-vOffset,  76, 76)


tcur_button      = pygame.Rect(155,  70-vOffset, 270,120)
ttarg_button     = pygame.Rect(440,  70-vOffset, 270,120)
pH_button        = pygame.Rect(155, 200-vOffset, 270,120)
ORP_button       = pygame.Rect(440, 200-vOffset, 270,120)
specgrav_button  = pygame.Rect(155, 330-vOffset, 270,120)
lbssalt_button   = pygame.Rect(440, 330-vOffset, 270,120)

#rt_total_button  = pygame.Rect(171, 79,480,60)
rt_filter_button = pygame.Rect(71,149,680,44)
rt_uvbulb_button = pygame.Rect(71,219,680,44)
rt_salt_button   = pygame.Rect(71,289,680,44)
rt_max_button    = pygame.Rect(115, 160-vOffset, 270,150)
rt_thresh_button = pygame.Rect(400, 160-vOffset, 270,150)
rt_reset_button  = pygame.Rect(300, 330-vOffset, 200,150)

gradbar_button   = pygame.Rect(gradBarLeft,gradBarTop,gradBarWidth,gradBarHeight)

default_font      = pygame.font.Font(abspath+"guiassets/kozgoxl.otf",16)
tankname_font     = pygame.font.Font(abspath+"guiassets/kozgoxl.otf",54)
status_font       = pygame.font.Font(abspath+"guiassets/kozgoxl.otf",30)

introfade1=0
introfade2=0

wifilist=-5

#================================ DEFINE SUBROUTINES ================================                
#-----------------------------------------------------------------
fpst=time.time()
fps=0
tname="ZEROGRAVITY"
def tankname():
    global fpst,fps
    global floatelapsed
    global timeleft_str
    global levels_button
    global tname,debugstring

    tn=tname
    if printer.myID=='Harmony-DEVI': tn="HARMONY"
    if printer.myID=='Portland-DEVI1': tn="FLOAT ON"
    if printer.myID=='SantaCruz-DEVI1': tn="TANK ONE"
    if printer.myID=='SantaCruz-DEVI2': tn="TANK TWO"
    if printer.myID=='DeBoisPA-DEVI1': tn="ZEROGRAVITY"
    tname=tn
    numletters=len(tn)
    tnFull=tankname_font.render(tn,1,(28,103,114))
    charspacing=9
    tw=tnFull.get_rect().width+charspacing*(numletters-1)
    x=400-tw/2
    for c in tn:
        tnLetter=tankname_font.render(c,1,(80,180,208))
        tnLetter.set_alpha(alpha0)
        stage.blit(tnLetter, (x, 54))
        x+=tnLetter.get_rect().width+charspacing

    f=(min_shower+(min_fade1+min_fade2)+min_float)*60-floatelapsed
    if f<0: f=totalDuration*60-floatelapsed
    
    h=math.floor(f/60/60)
    f-=h*60*60
    m=math.floor(f/60)
    f-=m*60
    s=math.floor(f)
    h_str=str(h)
    m_str=str(m)
    s_str=str(s)
    if m<10: m_str="0"+m_str
    if s<10: s_str="0"+s_str
    
    def time_str(t):
        tar=time.localtime( t )
        ampm=" am"
        hb=tar[3]
        if hb>11: ampm=" pm"
        if hb>12: hb-=12
        if hb==0: hb=12
        mb=tar[4]
        mb_str=str(mb)
        if mb<10: mb_str="0"+mb_str
        return str(hb)+":"+mb_str+ampm
    
    timeleft_str=h_str+":"+m_str+":"+s_str+" • "+time_str(floatstart+totalDuration*60)

    fps1=time.time()-fpst
    fps=fps*.99+fps1*.01
    fpst=time.time()
    if not floatInProgress: timeleft_str = "READY"    
    if alertMode or lightMode:
        timeleft_str+=" - "
        if alertMode: timeleft_str+="ALERT"
        elif lightMode: timeleft_str+="LIGHT ON"
    
    #debugstring=str(time.time()-cur_temp_refresh)
    if time.time()>cur_temp_refresh+6: thermoString=time_str(time.time())+" • - °F"
    else: 
        try: thermoString=time_str(time.time())+" • "+str(int(10*(cur_temp+t_offset))/10)+" °F"
        except: thermoString=time_str(time.time())+" • - °F"
    
    
    timeleft = default_font.render(timeleft_str,1,(140,140,128))
    timeelapsed = default_font.render(str(math.floor(floatelapsed/60))+"min",1,(140,140,128))
    temperature = default_font.render(str(thermoString),1,(140,140,128))
    
    timeelapsed.set_alpha(alpha0)
    temperature.set_alpha(alpha0)
    stage.blit(timeleft, (400-tw/2, 108))
    stage.blit(temperature, (400+tw/2-temperature.get_rect().width, 108))
    levels_button = pygame.Rect(400+tw/2-temperature.get_rect().width-10,108-10, temperature.get_rect().width+20,temperature.get_rect().height+20)
    if floatInProgress and floatscreen and not settingsscreen:
        tx=prog-timeelapsed.get_rect().width/2
        if tx<gradBarLeft+10: tx=gradBarLeft+10
        stage.blit(timeelapsed, (tx,gradBarTop+gradBarHeight+20-vOffset-timeelapsed.get_rect().height))

#-----------------------------------------------------------------
def statusbar(text):
    status=status_font.render(text,1,(128,203,224))
    status.set_alpha(alpha0)
    stage.blit(status, (400-status.get_rect().width/2, 374-vOffset))

#-----------------------------------------------------------------


def updatelog():
    return 0
    print('log')
    logfile=open(abspath+'log.txt', 'r')
    #logline = logfile.readline().strip()
    lines=logfile.readline()
    
    for line in lines:
        if line[2:16]=="phase        :":
            line=line.strip()
            print(line[15:]+" | "+line[line.find('(')+1:-1])
            
#-----------------------------------------------------------------
def trendgraph():
    #tankname()
    pygame.draw.line(stage, (112,128,232), (100,150),(700,150), 2)
    pygame.draw.line(stage, (112,128,232), (100,150),(100,400), 2)
    pygame.draw.line(stage, (112,128,232), (100,400),(700,400), 2)
    pygame.draw.line(stage, (112,128,232), (700,150),(700,400), 2)
    w=700-100-3
    h=400-150-3
    graph = pygame.Surface((w,h))
    graph.fill((25,25,25))
    y2=0
    
    pygame.draw.line(graph, (56,94,116), (0,100),(600,100), 1)
    
    for x in range(-2,w-1):
        y1=y2
        xt=x+time.time()*10
        y2=10*math.sin(xt/100)-5*math.cos(xt/50)#-xt/50
        pygame.draw.line(graph, (212,228,232), (x,100+y1),(x+1,100+y2), 2)
      
    
    stage.blit(graph,(102,152))
    more1=status_font.render("TEMPERATURE",1,(128,203,224))
    more2=default_font.render("pH  |  ORP  |  SPEC.GRAV.  |  SALT  |  H2O2 s.",1,(28,103,124))
    targ=default_font.render("93.5 °F",1,(28,103,124))
    stage.blit(more1, (400-more1.get_rect().width/2, 50))
    stage.blit(more2, (400-more2.get_rect().width/2, 90))
    stage.blit(targ, (710, 250))

#-----------------------------------------------------------------
keybshift=False
keybcaps=False
keybEnter=False
keyb_str=''
keyb_i=0
blink=time.time()
blinktoggle=True
def keyboard():
    global debugstring,blink,blinktoggle
    
    kreg=[
        "`1234567890-=",
        "qwertyuiop[]",
        "asdfghjkl;'",
        "zxcvbnm,./"
        ]

    kshift=[
        "~!@#$%^&*()_+",
        "QWERTYUIOP{}",
        'ASDFGHJKL:"',
        "ZXCVBNM<>?"
        ]

    wb=799
    hb=201
    board = pygame.Surface((wb,hb))
    board.fill((25,25,25))
    
    #debugstring=str(pos)
    def insert(l):
        global keyb_i,keyb_str,keybshift,keybcaps,keybEnter
        
        if l=='Caps': 
            keybcaps=not keybcaps
            if keybcaps: keybshift=False
        
        elif l=='Shift': 
            keybshift=not keybshift
            if keybshift: keybcaps=False
        
        elif l=='Back':
            if keyb_i>0: 
                keyb_str=keyb_str[:keyb_i-1]+keyb_str[keyb_i:]
                keyb_i-=1
        
        elif l=='Esc': 
            keyb_i=0
            keyb_str=''
            
        elif l=='Enter': 
            keybEnter=True
            print('ENTER')
            
        elif l=='←': keyb_i-=1
        elif l=='→': keyb_i+=1
        
        else:
            keyb_str=keyb_str[:keyb_i]+l+keyb_str[keyb_i:]
            keybshift=False
            keyb_i+=1
    
        if keyb_i<0:keyb_i=0
        if keyb_i>len(keyb_str):keyb_i=len(keyb_str)
        
    def addkey(l,x,y,w):
        global debugstring,blink,blinktoggle
        #debugstring=l
        c=(128,203,224)
        if (l=='Shift' and keybshift) or (l=='Caps' and keybcaps): c=(255,255,255)
        keyrect=pygame.Rect(x, y, w, 51+50*(l=='Enter'))
        keyrectmouse=pygame.Rect(x, y+479-hb, w, 51+50*(l=='Enter'))
        pygame.draw.rect(board, (90,90,90),keyrect, 1-(keybshift and l=='Shift')-(keybcaps and l=='Caps'))
        kl=status_font.render(l,1,c)
        board.blit(kl, (x+w/2-kl.get_rect().width/2, 10+y+25*(l=='Enter')))
        if go and keyrectmouse.collidepoint(pos): 
            blink=time.time()
            blinktoggle=True
            insert(l)
    
    ky=0
    kxo=50
    
    if keybshift or keybcaps: karr=kshift
    else: karr=kreg
    
    for krow in karr:
        for kx in range(0,len(krow)): addkey(krow[kx],kxo+kx*50,ky,50)
        ky+=50
        kxo+=25
    
    #shift
    addkey('Esc',0,0,50)
    addkey('Caps',0,50,75)
    addkey('Shift',0,100,100)
    addkey(' ',0,150,125)
    addkey('Back',700,0,100)
    addkey('Enter',700,50,100)
    addkey('←',700,150,50)
    addkey('→',750,150,50)
      
    stage.blit(board,(0,479-hb))
    
    txt=status_font.render(keyb_str,1,(128,203,224))
    txtx=400-txt.get_rect().width/2
    stage.blit(txt, (txtx, 150))
    for i in range(0,keyb_i):
        c=status_font.render(keyb_str[i],1,(128,203,224))
        txtx+=c.get_rect().width
        
    if time.time()>blink+.3:
        blink=time.time()
        blinktoggle=not blinktoggle
    if blinktoggle: pygame.draw.line(stage, (156,224,255), (txtx,145),(txtx,185), 2)
    
    return keyb_str


#-----------------------------------------------------------------
def timey(t):
    hrs=math.floor(t/3600)
    t-=hrs*3600
    min=math.floor(t/60)
    t-=min*60
    sec=math.floor(t)
    
    hrs=str(hrs)
    min="0"+str(min)
    sec="0"+str(sec)
    return hrs+":"+min[-2:]+":"+sec[-2:]

#-----------------------------------------------------------------

def rteditbars():
    if r1screen:
        ms=str(math.floor(rt_filter_max))
        ts=str(math.floor(rt_filter_thresh*100))+"%"
        rts="FILTER  RUNTIME"
        
    if r2screen:
        ms=str(math.floor(rt_uvbulb_max))
        ts=str(math.floor(rt_uvbulb_thresh*100))+"%"
        rts="UV  BULB  RUNTIME"
        
    if r3screen:
        ms=str(math.floor(rt_solution_max))
        ts=str(math.floor(rt_solution_thresh*100))+"%"
        rts="SOLUTION  RUNTIME"
        
    title =tankname_font.render(rts,1,(132, 202, 232))
    maxi  =tankname_font.render(ms, 1,(28,103,124))
    thresh=tankname_font.render(ts, 1,(28,103,124))
    stage.blit(title,  (410- title.get_rect().width/2,  70))
    stage.blit(maxi,   (265-  maxi.get_rect().width/2, 170))
    stage.blit(thresh, (545-thresh.get_rect().width/2, 170))

    
def runtimebars():
    global filter_runtime,uvbulb_runtime,rt_solution_start,last_rt
    w=398
    h=44
    
    if manualfilter and time.time()>last_rt+1:
      filter_runtime+=1
      uvbulb_runtime+=1
      printer.fout('filter_runtime',str(filter_runtime))
      printer.fout('uvbulb_runtime',str(uvbulb_runtime))
      last_rt=time.time()

    rt_total   =math.floor(time.time())-rt_total_start
    rt_filter  =math.floor(filter_runtime)
    rt_uvbulb  =math.floor(uvbulb_runtime)
    rt_solution=math.floor(time.time())-rt_solution_start
        
    filter_w   = 1+rt_filter/rt_filter_max/3600*w
    uvbulb_w   = 1+rt_uvbulb/rt_uvbulb_max/3600*w
    solution_w = 1+rt_solution/rt_solution_max/3600*w
    
    pygame.draw.line(stage, (212,228,232), (211,149+h/2),(211+filter_w,149+h/2), h-4)
    pygame.draw.line(stage, (212,228,232), (211,219+h/2),(211+uvbulb_w,219+h/2), h-4)
    pygame.draw.line(stage, (212,228,232), (211,289+h/2),(211+solution_w,289+h/2), h-4)

    rt_total_text    = default_font.render(timey(rt_total),1,(140,140,128))
    rt_filter_text   = default_font.render(timey(rt_filter)  +" of "+str(math.floor(rt_filter_max)),  1,(140,140,128))
    rt_uvbulb_text   = default_font.render(timey(rt_uvbulb)  +" of "+str(math.floor(rt_uvbulb_max)),  1,(140,140,128))
    rt_solution_text = default_font.render(timey(rt_solution)+" of "+str(math.floor(rt_solution_max)),1,(140,140,128))
    
    stage.blit(rt_total_text,    (480,108-1))
    stage.blit(rt_filter_text,   (228+w,149+13))
    stage.blit(rt_uvbulb_text,   (228+w,219+13))
    stage.blit(rt_solution_text, (228+w,289+13))
    
#-----------------------------------------------------------------
def levelsbars(cur,targ,pH,ORP,sg,ls):
    curtext=str(math.floor(cur*10)/10)
    targtext=str(math.floor(targ*10)/10)
    pHtext=str(math.floor(pH*10)/10)
    ORPtext=str(math.floor(ORP))
    sgtext=str(math.floor(sg*100)/100)
    lstext=str(math.floor(ls))
    
    cur  = tankname_font.render(curtext, 1,(28,103,124))
    targ = tankname_font.render(targtext,1,(28,103,124))
    pH   = tankname_font.render(pHtext,  1,(28,103,124))
    ORP  = tankname_font.render(ORPtext, 1,(28,103,124))
    sg   = tankname_font.render(sgtext,  1,(28,103,124))
    ls   = tankname_font.render(lstext,  1,(28,103,124))

    #(155,  70-vOffset, 270,120)
    #(440,  70-vOffset, 270,120)
    #(155, 200-vOffset, 270,120)
    #(440, 200-vOffset, 270,120)
    #(155, 330-vOffset, 270,120)
    #(440, 330-vOffset, 270,120)
    #asdf
    stage.blit(cur, (290 -  cur.get_rect().width/2, 100-vOffset))        
    stage.blit(targ,(575 - targ.get_rect().width/2, 100-vOffset))        
    stage.blit(pH,  (290 -   pH.get_rect().width/2, 235-vOffset))        
    stage.blit(ORP, (575 -  ORP.get_rect().width/2, 235-vOffset))        
    stage.blit(sg,  (290 -   sg.get_rect().width/2, 360-vOffset))        
    stage.blit(ls,  (575 -   ls.get_rect().width/2, 360-vOffset))        

#-----------------------------------------------------------------
def custombar(muin,mout,liin,lout,ldur):
    #asdf
    if muin=='0' or muin=='0.0': muin=mout='Off'
    muin_=tankname_font.render(muin,1,(28,103,124))
    mout_=tankname_font.render(mout,1,(28,103,124))
    liin_=tankname_font.render(liin,1,(28,103,124))
    lout_=tankname_font.render(lout,1,(28,103,124))
    ldur_=tankname_font.render(ldur,1,(28,103,124))
    
    stage.blit(muin_, (285-muin_.get_rect().width/2, 154-vOffset))        
    stage.blit(mout_, (285-mout_.get_rect().width/2, 254-vOffset))        
    stage.blit(liin_, (530-liin_.get_rect().width/2, 154-vOffset))        
    stage.blit(lout_, (530-lout_.get_rect().width/2, 254-vOffset))        
    stage.blit(ldur_, (285-ldur_.get_rect().width/2, 382-vOffset))        

#-----------------------------------------------------------------
def gradbar():
    if gradsurface: 
        gradsurface.set_alpha(math.floor(.65*255)) # 65% grad bar... remember ;) ?
        stage.blit(gradsurface, (gradBarLeft, gradBarTop-vOffset))
        
    m1 = default_font.render("5min",1,(140,140,128))
    m2 = default_font.render(str(math.floor(min_float+min_shower+(min_fade1+min_fade2)))+"min",1,(140,140,128))
    stage.blit(m1, (gradBarLeft+_shower, gradBarTop-20-vOffset))
    stage.blit(m2, (gradBarLeft+_shower+(_fade1+_fade2)+_float-0*m2.get_rect().width, gradBarTop-20-vOffset))
    
#-----------------------------------------------------------------
def drawgradbar():
    global gradsurface
    global progbar
    global gradalpha
    global gradBarWidth
    global gradBarHeight
    global _shower,_fade1,_float,_fade2,_wait,_plo,_filter
    global totalDuration
    gradalpha=minAlpha
    
    h=gradBarHeight
    w=gradBarWidth
    _r=0
    _g=0
    _b=0

    totalDuration=min_shower+min_fade1+min_float+min_fade2+min_wait+min_plo+min_phi
    _shower =w/totalDuration*min_shower
    _fade1  =w/totalDuration*min_fade1
    _fade1m =w/totalDuration*min_fade1_m
    _float  =w/totalDuration*min_float
    _fade2  =w/totalDuration*min_fade2
    _fade2m =w/totalDuration*min_fade2_m
    _wait   =w/totalDuration*min_wait
    _plo    =w/totalDuration*min_plo
    _filter =w/totalDuration*min_phi

    gradsurface = pygame.Surface((w,h))
    progbar     = pygame.Surface((w,h))
    progbar.fill((22,27,33))
    progbar.set_alpha(math.floor(255*.7)) # 70% white prog bar... remember ;) ?

    c_r=colvals['colval_r']
    c_g=colvals['colval_g']
    c_b=colvals['colval_b']

    def byteclamp(n):
        n=int(n)
        if n<0: n=0
        if n>255: n=255
        return n

    for x in range(0,799):
        #THE GRADIENT
        cth=(colorthereapymode)*196
        
        mus_y=1
        if x>_shower: mus_y=1-(x-_shower)/(_fade1m+.0001)
        if x>_shower+_fade1+_float+_fade2-_fade2m: mus_y=(x-_shower-_fade1-_float-_fade2+_fade2m)/(_fade2m+.0001)
        if mus_y<0: mus_y=0
        if mus_y>1: mus_y=1
        if _fade1m<.1: mus_y=1
        
        if x<_shower: _r=_g=_b=255                                                                                                        #shower
        if x>_shower and x<_shower+_fade1: _r=_g=_b=byteclamp(cth+(1-(x-_shower)/_fade1)*(255-cth))                                       #fade1
        if x>_shower+_fade1 and x<_shower+_fade1+_float: _r=_g=_b=cth                                                                     #float
        if x>_shower+_fade1+_float and x<_shower+_fade1+_float+_fade2: _r=_g=_b=byteclamp(cth+(x-_shower-_fade1-_float)/_fade2*(255-cth)) #fade2
        if x>_shower+_fade1+_float+_fade2: _r=_g=_b=255                                                                                   #wait
        if x>_shower+_fade1+_float+_fade2+_wait:                                                                                          #plo/hi
            _r= byteclamp(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *4)
            _g= byteclamp(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *3)
            _b= byteclamp(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *2)
            if _r<0: _r=0
            if _g<0: _g=0
            if _b<0: _b=0
            _r+=byteclamp( 0 +(x-_shower-(_fade1+_fade2)-_float  ) / _filter*255)
            _b+=byteclamp( 0 +(x-_shower-(_fade1+_fade2)-_float  ) / _filter*255)
            if _r>255: _r=255
            if _g>255: _g=255
            if _b>255: _b=255
                    
        if x<_shower+_fade1+_float+_fade2+_wait or True: 
            _r=byteclamp(_r*(.8*c_r+.2))
            _g=byteclamp(_g*(.8*c_g+.2))
            _b=byteclamp(_b*(.8*c_b+.2))
        else:
            _r=byteclamp(_r*(.3*c_r+.7))
            _g=byteclamp(_g*(.3*c_g+.7))
            _b=byteclamp(_b*(.3*c_b+.7))
            
        pygame.draw.line(gradsurface, (_r,_g,_b), (x,0),(x,h), 1)
        pygame.draw.line(gradsurface, (byteclamp(8+1.5*_r),byteclamp(8+1.5*_g),byteclamp(8+1.5*_b),), (x,h-mus_y*h/2),(x,h), 1)
            
    pygame.draw.line(gradsurface, (0,0,0), (_shower,0),(_shower,h), 1)
    pygame.draw.line(gradsurface, (0,0,0), (_shower+_fade1+_float+_fade2,0),(_shower+_fade1+_float+_fade2,h), 1)
    pygame.draw.line(gradsurface, (0,0,0), (_shower+_fade1+_float+_fade2+_wait,0),(_shower+_fade1+_float+_fade2+_wait,h), 1)
    pygame.draw.line(gradsurface, (0,0,0), (_shower+_fade1+_float+_fade2+_wait+_plo,0),(_shower+_fade1+_float+_fade2+_wait+_plo,h), 1)

#-----------------------------------------------------------------
def dephaser():
    ph=phase
    if ph==-1: return "PHASE_NONE"
    if ph==0: return "PHASE_SHOWER"
    if ph==1: return "PHASE_FADE1"
    if ph==2: return "PHASE_FLOAT"
    if ph==3: return "PHASE_FADE2"
    if ph==4: return "PHASE_WAIT"
    if ph==5: return "PHASE_PLO"
    if ph==6: return "PHASE_PHI"
    if ph==70: return "PHASE_UV"
    if ph==76: return "PHASE_UV+PHI"
    if ph==800: return "PHASE_H2O2"
    if ph==806: return "PHASE_H2O2+PHI"
    if ph==870: return "PHASE_H2O2+UV"
    if ph==876: return "PHASE_H2O2+UV+PHI"
    if ph==9000: return "PHASE_SHUTOFF"
    return "WEIRD->"+str(ph)

cur_temp_refresh=0
def getserverupdates():
    try:
        while alive:
            global cur_temp,alertMode,lightMode,debugstring,cur_temp_refresh
            if server.data!='':
                try: j=json.loads(server.data)
                except Exception as e:
                    print('server-'+str(e))
                    break
                
                server.data='' #used it up ;)
                jk=j.keys()
                
                if 'alertMode' in jk: alertMode=j['alertMode']
                if 'lightMode' in jk: lightMode=bool(j['lightMode'])
                if 'fthermo'   in jk: 
                    cur_temp=j['fthermo']
                    cur_temp_refresh=time.time()
                #old_sleepMode=sleepMode=not lightMode
            time.sleep(.1)
    except: print('serverupdate reboot')
    
reason=status_font.render("Are both override switches set to OFF?", 1, (194,184,174))
reasonSurface.blit(reason,(400-reason.get_rect().width/2,240-reason.get_rect().height/2))

lastLog=time.time()
lastInit=time.time()-100
if trendsscreen: updatelog()

#================================ THE MAIN LOOP ================================                
if settingsscreen and manualfilter: layer1=filter
if settingsscreen and manualh2o2: layer2=h2o2

OOO="               "
printer.p(OOO+"zerogAlive === checking in...")    
printer.p(OOO+"zerogAlive === entering circuit...")    

#pygame.mouse.set_pos(799,479)
changed=1
mlock=False
#old_lightMode=lightMode
#old_alertMode=alertMode
old_phase=phase
old_fade=fade
#old_sleepMode=sleepMode
old_manualfilter=manualfilter
old_manualh2o2=manualh2o2
old_max_vol=max_vol
old_targ_temp=targ_temp_i=int(targ_temp*10)/10
old_t_offset=t_offset
#old_min_fade1=min_fade1
#old_min_fade2=min_fade2
#old_min_fade1_m=min_fade1_m
#old_min_fade2_m=min_fade2_m

mouseL=old_mouseL=0
fout_ct_time=time.time()

Thread(target=getserverupdates).start()
while alive:
    exScr=(not customscreen and not levelsscreen and not wifiscreen and not runtimescreen and not trendsscreen)

    for e in pygame.event.get(): continue
    #try: debugstring=(str(time.time()%10)[:4]+" : "+str(e.dict['pos'])+" | "+str(pygame.event.get_grab()))
    #except: pass#print('exception@768')
    
    #pygame.event.pump()
    if time.time()-start<2:
        bglogo.set_alpha(introfade1)
        introfade1+=10
        if introfade1>255: introfade1=255
        screen.blit(bglogo,(0,0))
        #pygame.display.flip()
        pygame.display.update()

    #elif time.time()-start<2.5:
    #    bg.set_alpha(introfade2)
    #    introfade2+=10
    #    if introfade2>255: introfade2=255
    #    screen.blit(bg,(0,-vOffset)) #yOffset
    #    #pygame.display.flip()
    #    pygame.display.update()
        
    else:
        #mouse position and button clicking
        pos = pygame.mouse.get_pos()
        old_mouseL=mouseL
        (mouseL,mouseM,mouseR) = pygame.mouse.get_pressed()
        
        if mouseL==1 and not touched: go=touched=True
        elif mouseL==1 and touched: go=False
        else:
            go=touched=mlock=False
            lastsend=time.time()-1
        if go: even=False
        changed=1
        
        #=== CHECK IF THE MOUSE IS OVER ANY TARGET ZONES ===
        #
        on_exit      =      exit_button.collidepoint(pos)
        on_sixtymin  =  sixtymin_button.collidepoint(pos)
        on_ninetymin = ninetymin_button.collidepoint(pos)
        on_custommin = custommin_button.collidepoint(pos)

        on_back      =      back_button.collidepoint(pos)

        on_sleep     =     sleep_button.collidepoint(pos)
        on_play      =      play_button.collidepoint(pos)
        on_stop      =      stop_button.collidepoint(pos)

        on_gear      =      gear_button.collidepoint(pos)

        on_therm     =     therm_button.collidepoint(pos)
        on_levels    =    levels_button.collidepoint(pos)
        on_wifi      =      wifi_button.collidepoint(pos)
        on_runtime   =   runtime_button.collidepoint(pos)
        on_trends    =    trends_button.collidepoint(pos)

        on_filter    =    filter_button.collidepoint(pos)
        on_h2o2      =      h2o2_button.collidepoint(pos)
        on_volume    =    volume_button.collidepoint(pos)
        on_custom    =    custom_button.collidepoint(pos)

        on_cmusicin  =  cmusicin_button.collidepoint(pos)
        on_cmusicout = cmusicout_button.collidepoint(pos)
        on_clightin  =  clightin_button.collidepoint(pos)
        on_clightout = clightout_button.collidepoint(pos)
        on_clength   =   clength_button.collidepoint(pos)
        on_ccol      =      ccol_button.collidepoint(pos)
        on_ctherapy  =  ctherapy_button.collidepoint(pos)
        
        on_tcur      =      tcur_button.collidepoint(pos)
        on_ttarg     =     ttarg_button.collidepoint(pos)
        on_pH        =        pH_button.collidepoint(pos)
        on_ORP       =       ORP_button.collidepoint(pos)
        on_specgrav  =  specgrav_button.collidepoint(pos)
        on_lbssalt   =   lbssalt_button.collidepoint(pos)
        
        on_rt_filter = rt_filter_button.collidepoint(pos)
        on_rt_uvbulb = rt_uvbulb_button.collidepoint(pos)
        on_rt_salt   =   rt_salt_button.collidepoint(pos)
        on_rt_max    =    rt_max_button.collidepoint(pos)
        on_rt_thresh = rt_thresh_button.collidepoint(pos)
        on_rt_reset  = rt_reset_button.collidepoint(pos)

        on_gradbar   =  gradbar_button.collidepoint(pos)
        
        #printer.p(OOO+"zerogAlive === about to go into the buttons...")
        oldTarg0 = layer0
        oldTarg1 = layer1
        oldTarg2 = layer2
        oldTarg3 = layer3
        oldTarg4 = layer4

        #============================================================================#
        #                                                                            #
        #                 BUTTON AND SCREEN BRANCHING FLOW CHART                     #
        #                                                                            #
        #============================================================================#
        screens_BEGIN=mainscreen+2*floatscreen+4*settingsscreen

        if mainscreen:
            layer0=nonemin
            if floatpreset==60: layer0 = sixtymin
            if floatpreset==90: layer0 = ninetymin
            if floatpreset==-1: layer0 = custommin
            #if on_sixtymin    : layer0 = sixtymin
            #if on_ninetymin   : layer0 = ninetymin
            #if on_custommin   : layer0 = custommin
            
            if on_exit and go: alive = False
            if on_exit and go: printer.p(OOO+"zerogAlive === ending...")

            #asdf
            custom_condition=(on_custom and settingsscreen and exScr)
            gradbar_condition=(on_gradbar and floatscreen and exScr and not settingsscreen)
            if not mlock and go and (custom_condition or gradbar_condition): 
                mlock=True
                customscreen = True
                printer.fout('customscreen',str(customscreen)) 
            
            if on_trends and go and settingsscreen and exScr: 
                trendsscreen = True 
                updatelog()
                printer.fout('trendsscreen',str(trendsscreen)) 

            if on_wifi and go and settingsscreen and exScr: 
                mlock=True
                wifiscreen = True 
                wifilist=-5
                ssidSelect=False
                printer.fout('wifiscreen',str(wifiscreen)) 
            
            if on_runtime and go and settingsscreen and exScr: 
                mlock=True
                runtimescreen = True 
                printer.fout('runtimescreen',str(runtimescreen)) 
                
            if ((on_levels and go and not settingsscreen) or (on_therm and go and settingsscreen)) and exScr: 
                mlock=True
                levelsscreen = True
                try: ct=cur_temp+t_offset
                except: print('exception @885')
                printer.fout('levelsscreen',str(levelsscreen))

            #============================================================================
            #                            MAINSCREEN ONLY
            #============================================================================
            if not floatscreen and not settingsscreen and not levelsscreen:
                if on_sixtymin and go: floatpreset=60
                if on_ninetymin and go: floatpreset=90
                if on_custommin and go: floatpreset=-1
                if on_sixtymin or on_ninetymin or on_custommin: mlock=True
                
                if (on_sixtymin or on_ninetymin or on_custommin) and go: 
                    floatscreen = True
                    if floatpreset==-1: min_float = math.floor(custom_duration)-(min_fade1+min_fade2)
                    else: min_float = floatpreset-(min_fade1+min_fade2)
                    #printer.fout('min_float',str(min_float))
                    printer.fout('floatpreset',str(floatpreset))
                    printer.fout('floatscreen',str(floatscreen))
            
            if on_gear and go and not levelsscreen:
                settingsscreen=True
                printer.fout('settingsscreen',str(settingsscreen))
                if manualfilter: layer1=filter
                if manualh2o2: layer2=h2o2

            #============================================================================
            #                            CUSTOMSCREEN
            #============================================================================
            if customscreen:
                layer0=custom
                #asdf
                if on_ctherapy and go and not mlock: 
                    colorthereapymode=not colorthereapymode
                    client.send(json.dumps({"colorthereapymode":colorthereapymode}))
                    reloaded=True
    
                if on_ccol and go and not mlock:
                    hpos=-.15+1/.75*(pos[0]-ccol_button.left)/(ccol_button.width-20)
                    vpos=-.05+1/.9*(pos[1]-ccol_button.top)/ccol_button.height
                    def clamp(n): return n*(n>0 and n<1) + (n>1)
                    r=clamp( 2*hpos*( clamp((.333-vpos)/.167) + clamp(1-(.833-vpos)/.167)                         ) )
                    g=clamp( 2*hpos*( clamp(1-(.167-vpos)/.167)*(vpos<.333) + clamp((.667-vpos)/.167)*(vpos>=.333) ) )
                    b=clamp( 2*hpos*( clamp(1-(.500-vpos)/.167)*(vpos<.667) + clamp((1.00-vpos)/.167)*(vpos>=.667) ) )
                    w=clamp((hpos-.5)*2)
                    if w==1: r=g=b=w
                    #debugstring=str((int(100*r),int(100*g),int(100*b),int(100*w)))
                    colvals={
                        "colval_r":r,
                        "colval_g":g,
                        "colval_b":b,
                        "colval_w":w
                        }
                    colvals_=json.dumps(colvals)
                    client.send(json.dumps({"colvals":colvals_}))
                    printer.fout('colvals',colvals_)
                    reloaded=True

                #i mistakenly made IN and OUT reversed on all of these. 
                #they work but the naming is backwards. oops. 
                #fix it in so many places when i refactor the GUI (etc)
                
                #CUSTOM MUSIC FADEIN--------------------------------
                if on_cmusicin and mouseL and not mlock:
                    stepper=(pos[0]-cmusicin_button.left) / cmusicin_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade1_m-=.1
                    if stepper>0 and stepperSpeed==0: min_fade1_m+=.1
                    if stepper<0: min_fade1_m-=stepperSpeed
                    if stepper>0: min_fade1_m+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade1_m<0: min_fade1_m=0
                    if min_fade1_m>999: min_fade1_m=999
                    if min_fade1_m+min_fade2_m>custom_duration:
                        if min_fade1_m>custom_duration: min_fade1_m=custom_duration
                        min_fade2_m=custom_duration-min_fade1_m
                    fout_customMFadein=True
                elif fout_customMFadein:
                    printer.fout('min_fade1_m',str(min_fade1_m))
                    printer.fout('min_fade2_m',str(min_fade2_m))
                    fout_customDuration=True
                    fout_customMFadein=False
                    reloaded=True
                    client.send(json.dumps({"fade1_music":round(min_fade1_m,1)}))
                elif on_cmusicin: stepperSpeed=0

                #CUSTOM MUSIC FADEOUT--------------------------------
                if on_cmusicout and mouseL and not mlock:
                    stepper=(pos[0]-cmusicout_button.left) / cmusicout_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade2_m-=.1
                    if stepper>0 and stepperSpeed==0: min_fade2_m+=.1
                    if stepper<0: min_fade2_m-=stepperSpeed
                    if stepper>0: min_fade2_m+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade2_m<0: min_fade2_m=0
                    if min_fade2_m>999: min_fade2_m=999
                    if min_fade1_m+min_fade2_m>custom_duration:
                        if min_fade2_m>custom_duration: min_fade2_m=custom_duration
                        min_fade1_m=custom_duration-min_fade2_m
                    fout_customMFadeout=True
                elif fout_customMFadeout:
                    printer.fout('min_fade1_m',str(min_fade1_m))
                    printer.fout('min_fade2_m',str(min_fade2_m))
                    fout_customDuration=True
                    fout_customMFadeout=False
                    reloaded=True
                    client.send(json.dumps({"fade2_music":round(min_fade2_m,1)}))
                elif on_cmusicout: stepperSpeed=0

                #CUSTOM LIGHT FADEIN--------------------------------
                if on_clightin and mouseL and not mlock:
                    stepper=(pos[0]-clightin_button.left) / clightin_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade1-=.1
                    if stepper>0 and stepperSpeed==0: min_fade1+=.1
                    if stepper<0: min_fade1-=stepperSpeed
                    if stepper>0: min_fade1+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade1<0: min_fade1=0
                    if min_fade1>999: min_fade1=999
                    fout_customLFadein=True
                elif fout_customLFadein:
                    printer.fout('min_fade1',str(min_fade1))
                    if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)
                    fout_customDuration=True
                    fout_customLFadein=False
                    reloaded=True
                    client.send(json.dumps({"fade1_light":round(min_fade1,1)}))
                elif on_clightin: stepperSpeed=0

                #CUSTOM LIGHT FADEOUT--------------------------------
                if on_clightout and mouseL and not mlock:
                    stepper=(pos[0]-clightout_button.left) / clightout_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade2-=.1
                    if stepper>0 and stepperSpeed==0: min_fade2+=.1
                    if stepper<0: min_fade2-=stepperSpeed
                    if stepper>0: min_fade2+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade2<0: min_fade2=0
                    if min_fade2>999: min_fade2=999
                    fout_customLFadeout=True
                elif fout_customLFadeout:
                    printer.fout('min_fade2',str(min_fade2))
                    if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)
                    fout_customDuration=True
                    fout_customLFadeout=False
                    reloaded=True
                    client.send(json.dumps({"fade2_light":round(min_fade2,1)}))
                elif on_clightout: stepperSpeed=0


                #CUSTOM DURATION--------------------------------
                if on_clength and mouseL and not mlock:
                    stepper=(pos[0]-clength_button.left) / clength_button.width - .5
                    if stepper<0 and stepperSpeed==0: custom_duration-=1
                    if stepper>0 and stepperSpeed==0: custom_duration+=1
                    if stepper<0: custom_duration-=stepperSpeed
                    if stepper>0: custom_duration+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<4: stepperSpeed*=1.08
                    if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)
                    if custom_duration>999.9: custom_duration=999
                    floatpreset=math.floor(custom_duration)
                    fout_customDuration=True
                elif fout_customDuration:
                    printer.fout('custom_duration',str(custom_duration))
                    fout_customDuration=False
                    min_float = math.floor(custom_duration)-(min_fade1+min_fade2)
                    reloaded=True
                elif on_clength: stepperSpeed=0


            #============================================================================
            #                            TRENDSSCREEN
            #============================================================================
            if trendsscreen:
                layer0=trends
            
            #============================================================================
            #                             WIFISCREEN
            #============================================================================
            if wifiscreen:
                layer0=wifi
                        
            #============================================================================
            #                            RUNTIMESCREEN
            #============================================================================
            if runtimescreen:
                layer0=runtime
                
                if on_rt_filter and go and not r2screen and not r3screen and not mlock: mlock=r1screen=True
                if on_rt_uvbulb and go and not r1screen and not r3screen and not mlock: mlock=r2screen=True
                if on_rt_salt   and go and not r1screen and not r2screen and not mlock: mlock=r3screen=True
                
                if r1screen or r2screen or r3screen:
                    layer0=rt_edit
                    if on_rt_max and mouseL and not mlock:
                        if r1screen: rtmax=rt_filter_max
                        if r2screen: rtmax=rt_uvbulb_max
                        if r3screen: rtmax=rt_solution_max
                        
                        stepper=(pos[0]-tcur_button.left) / tcur_button.width - .5
                        if stepper<0 and stepperSpeed==0: rtmax-=.5
                        if stepper>0 and stepperSpeed==0: rtmax+=.5
                        if stepper<0: rtmax-=stepperSpeed*5
                        if stepper>0: rtmax+=stepperSpeed*5
                        if stepperSpeed<.5: stepperSpeed+=.1
                        elif stepperSpeed<2: stepperSpeed*=1.1
                        if rtmax<0: rtmax=0
                        if rtmax>9999: rtmax=9999

                        if r1screen: rt_filter_max=rtmax
                        if r2screen: rt_uvbulb_max=rtmax
                        if r3screen: rt_solution_max=rtmax

                        fout_rt_max=True
                        
                    elif fout_rt_max:
                        if r1screen: printer.fout('rt_filter_max',str(rt_filter_max))
                        if r2screen: printer.fout('rt_uvbulb_max',str(rt_uvbulb_max))
                        if r3screen: printer.fout('rt_solution_max',str(rt_solution_max))
                        fout_rt_max=False
                        
                    elif not mouseL: stepperSpeed=0
 
                    if on_rt_thresh and mouseL and not mlock:
                        if r1screen: rtthresh=rt_filter_thresh
                        if r2screen: rtthresh=rt_uvbulb_thresh
                        if r3screen: rtthresh=rt_solution_thresh

                        stepper=(pos[0]-ttarg_button.left) / ttarg_button.width - .5
                        if stepper<0 and stepperSpeed==0: rtthresh-=.01
                        if stepper>0 and stepperSpeed==0: rtthresh+=.01
                        if stepper<0: rtthresh-=stepperSpeed*.005
                        if stepper>0: rtthresh+=stepperSpeed*.005
                        if  stepperSpeed<.5: stepperSpeed+=.02
                        elif stepperSpeed<2: stepperSpeed*=1.1
                        if rtthresh<0: rtthresh=0
                        if rtthresh>1: rtthresh=1

                        if r1screen: rt_filter_thresh=rtthresh
                        if r2screen: rt_uvbulb_thresh=rtthresh
                        if r3screen: rt_solution_thresh=rtthresh

                        fout_rt_thresh=True
                        
                    elif fout_rt_thresh:
                        if r1screen: printer.fout('rt_filter_thresh',str(rt_filter_thresh))
                        if r2screen: printer.fout('rt_uvbulb_thresh',str(rt_uvbulb_thresh))
                        if r3screen: printer.fout('rt_solution_thresh',str(rt_solution_thresh))
                        fout_rt_max=False
                        
                    elif not mouseL: stepperSpeed=0

                    if on_rt_reset and mouseL and not mlock:
                        stopcount=True
                        countdown_num=3-(time.time()-countdownstart)
                        if countdown_num<0:
                            if r1screen:
                                filter_runtime=0
                                printer.fout('filter_runtime',str(filter_runtime))
                            if r2screen:
                                uvbulb_runtime=0
                                printer.fout('filter_runtime',str(uvbulb_runtime))                                
                            if r3screen:
                                rt_solution_start=time.time()
                                printer.fout('rt_solution_start',str(rt_solution_start))                                

                            #playfloat=False
                            #printer.fout('playfloat',str(playfloat))
                            #printer.fout('floatInProgress',str(floatInProgress))
                            countdown_num=0
                            stopcount=False
                            
                    elif on_rt_reset: 
                        stopcount=False
                        countdown_num=3
                        countdownstart=time.time()


            #============================================================================
            #                            LEVELSSCREEN
            #============================================================================
            if levelsscreen:
                layer0=levels
                
                if on_tcur and mouseL:
                    if old_cur_temp==-1: old_cur_temp=cur_temp
                    stepper=(pos[0]-tcur_button.left) / tcur_button.width - .5
                    if stepper<0 and stepperSpeed==0: ct-=.1
                    if stepper>0 and stepperSpeed==0: ct+=.1
                    if stepper<0: ct-=stepperSpeed*.5
                    if stepper>0: ct+=stepperSpeed*.5
                    if stepperSpeed<.5: stepperSpeed+=.03
                    elif stepperSpeed<2: stepperSpeed*=1.1
                    if ct<-99: ct=-99
                    if ct>999: ct=999
                    fout_currentTemperature=True
                    fout_ct_time=time.time()
                elif fout_currentTemperature:
                    t_offset=ct-old_cur_temp
                    old_cur_temp=-1
                    printer.fout('t_offset',str(t_offset))
                    fout_currentTemperature=False
                elif not mouseL:
                    try: 
                        if time.time()>fout_ct_time+3: ct=cur_temp+t_offset
                    except: print('exception@1168')
                    stepperSpeed=0

                if on_ttarg and mouseL and not mlock:
                    stepper=(pos[0]-ttarg_button.left) / ttarg_button.width - .5
                    if stepper<0 and stepperSpeed==0: targ_temp-=.1
                    if stepper>0 and stepperSpeed==0: targ_temp+=.1
                    if stepper<0: targ_temp-=stepperSpeed*.5
                    if stepper>0: targ_temp+=stepperSpeed*.5
                    if  stepperSpeed<.5: stepperSpeed+=.02
                    elif stepperSpeed<2: stepperSpeed*=1.1
                    if targ_temp<32: targ_temp=32
                    if targ_temp>120: targ_temp=120
                    fout_targetTemperature=True
                elif fout_targetTemperature:
                    printer.fout('targ_temp',str(targ_temp))
                    fout_targetTemperature=False
                    targ_temp_i=int(targ_temp*10)/10
                elif not mouseL: stepperSpeed=0

                if on_pH and mouseL:
                    stepper=(pos[0]-pH_button.left) / pH_button.width - .5
                    if stepper<0 and stepperSpeed==0: pH_lev-=.1
                    if stepper>0 and stepperSpeed==0: pH_lev+=.1
                    if stepper<0: pH_lev-=stepperSpeed*.2
                    if stepper>0: pH_lev+=stepperSpeed*.2
                    if  stepperSpeed<.5: stepperSpeed+=.02
                    elif stepperSpeed<2: stepperSpeed*=1.1
                    if pH_lev<0: pH_lev=0
                    if pH_lev>14: pH_lev=14
                    fout_pH=True
                elif fout_pH:
                    printer.fout('pH_lev',str(pH_lev))
                    fout_pH=False
                elif not mouseL: stepperSpeed=0

                if on_ORP and mouseL:
                    stepper=(pos[0]-ORP_button.left) / ORP_button.width - .5
                    if stepper<0 and stepperSpeed==0: ORP_lev-=1
                    if stepper>0 and stepperSpeed==0: ORP_lev+=1
                    if stepper<0: ORP_lev-=stepperSpeed
                    if stepper>0: ORP_lev+=stepperSpeed
                    if stepperSpeed<.5: stepperSpeed+=.1
                    elif stepperSpeed<2: stepperSpeed*=1.1
                    if ORP_lev<0: ORP_lev=0
                    if ORP_lev>800: ORP_lev=800                        
                    fout_ORP=True
                elif fout_ORP:
                    printer.fout('ORP_lev',str(ORP_lev))
                    fout_ORP=False
                elif not mouseL: stepperSpeed=0
            
                if on_specgrav and mouseL:
                    stepper=(pos[0]-specgrav_button.left) / specgrav_button.width - .5
                    if stepper<0 and stepperSpeed==0: specgrav_lev-=.01
                    if stepper>0 and stepperSpeed==0: specgrav_lev+=.01
                    if stepper<0: specgrav_lev-=stepperSpeed*.06
                    if stepper>0: specgrav_lev+=stepperSpeed*.06
                    if  stepperSpeed<.5: stepperSpeed+=.02
                    elif stepperSpeed<1: stepperSpeed*=1.1
                    if specgrav_lev<0: specgrav_lev=0
                    if specgrav_lev>4: specgrav_lev=14
                    fout_specgrav=True
                elif fout_specgrav:
                    printer.fout('specgrav_lev',str(specgrav_lev))
                    fout_specgrav=False
                elif not mouseL: stepperSpeed=0

                if on_lbssalt and mouseL:
                    stepper=(pos[0]-lbssalt_button.left) / lbssalt_button.width - .5
                    if stepper<0 and stepperSpeed==0: lbssalt_lev-=1
                    if stepper>0 and stepperSpeed==0: lbssalt_lev+=1
                    if stepper<0: lbssalt_lev-=stepperSpeed
                    if stepper>0: lbssalt_lev+=stepperSpeed
                    if stepperSpeed<.5: stepperSpeed+=.1
                    elif stepperSpeed<4: stepperSpeed*=1.1
                    if lbssalt_lev<0: lbssalt_lev=0
                    if lbssalt_lev>4000: lbssalt_lev=4000                        
                    fout_lbs=True
                elif fout_lbs:
                    printer.fout('lbssalt_lev',str(lbssalt_lev))
                    fout_lbs=False
                elif not mouseL: stepperSpeed=0
            
            
            #============================================================================
            #                            FLOATSCREEN
            #============================================================================                
            if floatscreen and not settingsscreen and exScr:
                if on_back and go: 
                    floatscreen=False
                    printer.fout('floatscreen',str(floatscreen))
                layer0=play
             
                if not manualfilter and not manualh2o2:
                    if on_play and go: 
                        prog=0
                        floatstart=time.time()
                        floatInProgress=True
                        printer.fout('floatstart',str(floatstart))
                        printer.fout('floatInProgress',str(floatInProgress))
                        playfloat=True 
                        fadeinmusic=False
                        printer.fout('playfloat',str(playfloat))
                        msg_obj={
                            "fade1_light":round(min_fade1,1),
                            "fade2_light":round(min_fade2,1),
                            "fade1_music":round(min_fade1_m,1),
                            "fade2_music":round(min_fade2_m,1),
                            "colorthereapymode":colorthereapymode                            
                            }
                        client.send(json.dumps(msg_obj))

                    if on_stop and go: countdownstart=time.time()                            
                    if on_stop and mouseL and playfloat:
                        stopcount=True                            
                        countdown_num=3-(time.time()-countdownstart)
                        if countdown_num<0:
                            playfloat=False
                            printer.fout('playfloat',str(playfloat))
                            printer.fout('floatInProgress',str(floatInProgress))
                            countdown_num=0
                            stopcount=False                                
                    elif on_stop and not mouseL: 
                        stopcount=False
                        countdown_num=3
                        countdownstart=time.time()
                
                else:    
                    if on_play and go: overrideWarning=time.time()
                    #else: overrideWarning=False
           
                if playfloat:
                    layer0=stop
                    prog=math.floor(floatelapsed/60/totalDuration*gradBarWidth)
            
            #============================================================================
            #                            SETTINGSSCREEN ONLY
            #============================================================================
            if settingsscreen and exScr:
                layer0=settings
                if on_back and go: printer.fout('custom_duration',str(custom_duration))
                if on_back and go: printer.fout('max_vol',str(max_vol))
                if on_back and go: layer0=layer1=layer2=layer3=layer4=0
                if on_back and go: 
                    reloaded=True
                    settingsscreen=False
                    printer.fout('settingsscreen',str(settingsscreen))
                    continue
                    
                if not floatInProgress:
                    if on_filter and go: manualfilter = not manualfilter
                    if on_filter and go: printer.fout('manualfilter',str(manualfilter))
                    if on_filter and go   and   manualfilter: layer1 = filter
                    if on_filter and go and not manualfilter: layer1 = 0
                    
                    if on_h2o2 and go: manualh2o2 = not manualh2o2
                    if on_h2o2 and go: printer.fout('manualh2o2',str(manualh2o2))
                    if on_h2o2 and go   and   manualh2o2: layer2 = h2o2
                    if on_h2o2 and go and not manualh2o2: layer2 = 0
                
                if on_volume and mouseL: 
                    max_vol=(pos[0]-10-volume_button.left) / (volume_button.width*.8)
                    if max_vol<0: max_vol=0
                    if max_vol>1: max_vol=1
                    
                    
        screens_END=mainscreen+2*floatscreen+4*settingsscreen
        if screens_BEGIN!=screens_END and floatscreen or reloaded: drawgradbar()
        if reloaded: 
            floatpreset=-1
            reloaded=False
        
        if on_sleep and go and not settingsscreen:
            lightMode=not lightMode
            client.send(json.dumps({"lightMode":lightMode}))
            countdownstart=time.time()                
        if on_sleep and mouseL and not settingsscreen and time.time()>countdownstart+1:
            stopcount=True
            countdown_num=6-(time.time()-countdownstart)
            if countdown_num<-.9:
                client.send("reboot")
                os.system('reboot')
        elif on_sleep and not mouseL:
            stopcount=False
            countdown_num=3
            countdownstart=time.time()
        
        if changed>0 and layer0: stage.blit(layer0,(0,0))
        if changed>0 and oldTarg1 and exScr: stage.blit(oldTarg1,(153,42))
        if changed>0 and oldTarg2 and exScr: stage.blit(oldTarg2,(422,42))
        
        if settingsscreen and exScr:
            for x in range(0,6):
                a=0
                if max_vol>(x+.5)/6: a=255
                #elif max_vol>(x-.75)/6: a=64
                #elif max_vol>(x-.50)/6: a=128
                #elif max_vol>(x-.25)/6: a=192
                #volume.set_alpha(math.floor(a))
                if changed>0 and a==255: stage.blit(volume,(174+x*26,316))
                    
        if not settingsscreen and exScr:
            tankname()
            if not lightMode: stage.blit(lightoff,(69, 363-vOffset))
            
            if floatscreen and exScr:
                gradbar()
                statusbar(status_str)
                if playfloat:
                    #debugstring='playfloat'
                    #progbar.set_alpha(.7)
                    stage.blit(progbar,(gradBarLeft-gradBarWidth+prog,gradBarTop-vOffset))
                    x=gradBarLeft+prog
                    pygame.draw.line(stage,(255,255,255),(x-1,gradBarTop-vOffset),(x-1,gradBarTop+gradBarHeight-vOffset-1), 1)
                    pygame.draw.line(stage,(  0,  0,  0),(x,  gradBarTop-vOffset),(x,  gradBarTop+gradBarHeight-vOffset-1), 1)

        if trendsscreen:
            if on_back and go: trendsscreen=False
            if on_back and go: printer.fout('trendsscreen',str(trendsscreen))
            trendgraph()
            even=True #render every frame
        
        if wifiscreen:
            if on_back and go: 
                mlock=True
                if ssidSelect: ssidSelect=False
                else: 
                    wifiscreen=False
                    printer.fout('wifiscreen',str(wifiscreen))
            
            if not ssidSelect:
                if wifilist<0:
                    ssid=default_font.render("I'm looking for Wireless Networks now...",1,(64,108,160))
                    stage.blit(ssid, (400-ssid.get_rect().width/2, 50))
                    wifilist+=1
                elif wifilist==0:
                    wifilist=1
                    os.system('iwlist wlan0 scan > '+abspath+'var/wlan0list')
                    os.system('iwlist wlan1 scan > '+abspath+'var/wlan1list')
                    
                    wlan=[]
                    def wifiparse(raw,arr):
                        global wlan
                        pos=1
                        while pos and pos<len(raw):
                            pos=raw.find('\n')
                            line = raw[:pos]
                            raw=raw[pos+1:]
                            if "Cell " in line: wlan.append({})
                            if "Quality=" in line: 
                                quality=line[line.find('=')+1:]
                                quality="000"+quality[:quality.find('/')]
                                quality=quality[-3:]
                                wlan[len(wlan)-1]['quality']=quality
                            if "SSID:" in line: 
                                ssid=line[line.find('"')+1:]
                                ssid=ssid[:ssid.find('"')]
                                wlan[len(wlan)-1]['ssid']=ssid
                            
                        return 0

                    wifiparse(printer.fin('wlan0list'),wlan)
                    wifiparse(printer.fin('wlan1list'),wlan)

                    for i in wlan:
                        keys=i.keys()
                        if not 'quality' in keys: wlan.remove(i)

                    wlanSorted = sorted(wlan, key=lambda k: k['quality'], reverse=True)
                    
                else:
                    ssid=default_font.render("Select your Wireless Network whenever you're ready :)",1,(64,108,160))
                    stage.blit(ssid, (400-ssid.get_rect().width/2, 50))
                    y=100
                    for i in wlanSorted:
                        if y>420: continue
                        ssid=status_font.render(i['ssid'],1,(128,183,224))
                        stage.blit(ssid, (500-ssid.get_rect().width, y))
                        
                        qualityrect = pygame.Rect(520, y+5, int(i['quality']), 20)
                        maxrect     = pygame.Rect(520, y+5, 100,               20)
                        
                        pygame.draw.rect(stage, (90,110,130),qualityrect, 0)        
                        pygame.draw.rect(stage, (90,90,90),maxrect, 1)        
                        y+=50
            
                    if not on_back and go and not mlock:
                        select=int((pos[1]-100)/50)
                        if select<0: select=0
                        if select<=len(wlanSorted) and select<=6: ssidSelect=wlanSorted[select]['ssid']
                        #    select=len(wlanSorted)
                        #    debugstring=wlanSorted[select]['ssid']
                    
            else:
                mlock=True
                #commit=keyboard()
                keyboard()
                if keybEnter:
                    keybEnter=False
                    pwdSelect=keyb_str
                    #newkey='ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
                    #newkey+='\nnetwork={\n\tssid=\"'+ssidSelect+'\"\n\tpsk=\"'+pwdSelect+'\"\n\tkey_mgmt=WPA-PSK\n}'
                    #os.system('echo "'+newkey+'" > /etc/wpa_supplicant/wpa_supplicant.conf')
                    newkey='\nnetwork={\n\tssid=\\"'+ssidSelect+'\\"\n\tpsk=\\"'+pwdSelect+'\\"\n\tkey_mgmt=WPA-PSK\n}'
                    os.system('echo "'+newkey+'" >> /etc/wpa_supplicant/wpa_supplicant.conf')
                    #asdf
                    
                    os.system('/etc/init.d/networking restart')
                    os.system('systemctl daemon-reload')
                    connected=False
                    ctime=time.time()
                    ctxt='Connecting'
                    while not connected and time.time()<ctime+7:
                        ctxt+='.'
                        connect=status_font.render(ctxt,1,(64,108,160))
                        screen.blit(trends,(0,0))
                        screen.blit(connect, (300, 200))
                        pygame.display.update()
                        os.system('ping -c1 google.com > '+abspath+'var/ping_result')
                        pingres=printer.fin('ping_result')
                        connected=("unknown host" not in pingres and pingres!='')
                        time.sleep(.5)
                    
                    if connected: result="Connected :D"
                    else: result="I couldn't connect :|"
                    
                    connect=status_font.render(result,1,(64,108,160))
                    screen.blit(trends,(0,0))
                    screen.blit(connect, (400-connect.get_rect().width/2, 200))
                    pygame.display.update()
                    time.sleep(2)
                    #do the wpa_conf thing
                    
                    wifiscreen=False
                    printer.fout('wifiscreen',str(wifiscreen))
                    
                else:
                    ssid=default_font.render('(Wireless Network)',1,(64,108,160))
                    stage.blit(ssid, (400-ssid.get_rect().width/2, 90))
                    net=status_font.render(ssidSelect,1,(128,203,224))
                    stage.blit(net, (400-net.get_rect().width/2, 50))
                    
                    pwd=default_font.render('(Password)',1,(64,108,160))
                    stage.blit(pwd, (400-pwd.get_rect().width/2, 190))
            even=True #render every frame
                
        if runtimescreen:
            if on_back and go:
                if r1screen or r2screen or r3screen:
                    r1screen=r2screen=r3screen=False
                else:
                    runtimescreen=False
                    printer.fout('runtimescreen',str(runtimescreen))
            if r1screen or r2screen or r3screen:
                rteditbars()
            else: runtimebars()

        if levelsscreen:
            if on_back and go: levelsscreen=False
            if on_back and go: printer.fout('levelsscreen',str(levelsscreen))
            levelsbars(ct,targ_temp,pH_lev,ORP_lev,specgrav_lev,lbssalt_lev)

        if customscreen:                
            #debugstring="cust"
            if on_back and go: customscreen=False
            if on_back and go: printer.fout('customscreen',str(customscreen))                
            custombar(
                str(round(min_fade1_m,1)),
                str(round(min_fade2_m,1)),
                str(round(min_fade1,1)),
                str(round(min_fade2,1)),
                str(math.floor(custom_duration)))
            #asdf
            if colorthereapymode: stage.blit(check,(424, 381-vOffset))
            
        if changed>0: screen.blit(stage,(0,0))
        tfade=1
        tlights=False
        
        old_phase=phase
        if floatInProgress:
            tfade=0
            tlights=True
            phase=PHASE_SHOWER
            status_str="SHOWER"
            
            if floatelapsed/60>min_shower:
                phase=PHASE_FADE1
                status_str="FADE"
                tfade=(floatelapsed/60-min_shower)/min_fade1
                if tfade>1: tfade=1
            
            if floatelapsed/60>min_shower+min_fade1: 
                tlights=False
                phase=PHASE_FLOAT
                status_str="FLOAT"
            
            if floatelapsed/60>min_shower+min_fade1+min_float:
                tlights=True
                phase=PHASE_FADE2
                status_str="FADE"
                tfade=1-(floatelapsed/60-(min_shower+min_fade1+min_float))/min_fade2
                if tfade<0: tfade=0
            
            if floatelapsed/60>min_shower+min_fade1+min_float+min_fade2-min_fade2_m: 
                if not fadeinmusic: client.send(json.dumps({"fadeinmusic":fadeinmusic}))
                fadeinmusic=True
                
            if floatelapsed/60>min_shower+min_fade1+min_float+min_fade2: 
                phase=PHASE_WAIT
                status_str="SHOWER"
                
            if floatelapsed/60>min_shower+min_fade1+min_float+min_fade2+min_wait: 
                phase=PHASE_PLO
                status_str="FILTER"
            
            if floatelapsed/60>min_shower+min_fade1+min_float+min_fade2+min_wait+min_plo: 
                phase=PHASE_PHI
                if floatelapsed/60<min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo+min_uv: phase+=PHASE_UV
                if floatelapsed/60<min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo+min_h2o2: phase+=PHASE_H2O2
            
            if tfade>0:
                blackout.set_alpha(tfade*192)
                screen.blit(blackout,(0,0))
                #if floatscreen and not settingsscreen: screen.blit(blackout,(0,0))
            
            if floatelapsed/60>totalDuration:
                playfloat=False
                floatInProgress=False
                phase=PHASE_SHUTOFF
                printer.fout('playfloat',str(playfloat))
                printer.fout('floatInProgress',str(floatInProgress))
                                                
        else:
            tlights=True
            phase=PHASE_NONE
            status_str="READY"
            tfade=fade
            if tfade>0: tfade-=.01
            if tfade<0: tfade=0
        #set the actual fade just once! otherwise every so often the other thread will call on it before it is prepared ;)
        
        if old_phase!=phase and phase==PHASE_FADE1: lightMode=False
        if old_phase!=phase and (phase==PHASE_NONE or phase==PHASE_SHOWER or phase==PHASE_WAIT): lightMode=True
        
        if not playfloat: floatInProgress=False
        if not floatInProgress: floatstart=time.time()
        if stopcount:
            blackout.set_alpha(192)# -(255-alpha0)/255*fade)
            countdown=tankname_font.render(str(math.floor(countdown_num+1)), 1, (164,154,144))
            screen.blit(blackout,(0,0))
            screen.blit(countdown, (400-countdown.get_rect().width/2,240-countdown.get_rect().height/2))

        if overrideWarning!=False:
            th=(time.time()-overrideWarning)/2*3.14
            if th>2*3.14: overrideWarning=False
            a=(.5-math.cos(th)/2)*192
            #print(str(th))
            reasonSurface.set_alpha(a)
            screen.blit(reasonSurface, (0,0))
    
        #if lightMode:
        #    #tfade=0
        #    
        #if alertMode:
        #    #tfade=.5+.5*math.sin((time.time()/3)*3.14)
        #    #amber.set_alpha(DIM*255)
        #    #screen.blit(amber,(0,0))
        
        if not lightMode:
            #tlights=False
            if tfade<1: tfade+=.1
            if tfade>1: tfade=1
            blackout.set_alpha(128)
            screen.blit(blackout,(0,0))
        
        fade=tfade
                    
        #floatelapsed=(time.time()-floatstart)*1+60*min_shower-5
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+1*min_fade1)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+1*min_fade1+min_float)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo+min_phi)-10
    
        #================ ================ ================ ================ ================ 
        floatelapsed=(time.time()-floatstart)   #this is the not-testing-for one
        #debugstring=str(int(min_float+min_fade1+min_fade2))
        if int(1+min_float+min_fade1+min_fade2)==21: floatelapsed=(time.time()-floatstart)*20
        if int(1+min_float+min_fade1+min_fade2)==22: floatelapsed=(time.time()-floatstart)*1+60*min_shower-5
        if int(1+min_float+min_fade1+min_fade2)==23: floatelapsed=(time.time()-floatstart)*1+60*(min_shower+1*min_fade1+min_float)-5
        #================ ================ ================ ================ ================ 
        
        debug = default_font.render(debugstring,1,(190,190,178))
        screen.blit(debug, (55, 50))
        
        #debug = default_font.render(debugstring,1,(90,90,78))
        #screen.blit(debug, (55, 400))
        
        #================ ACTUALLY DRAW TARGET ZONES FOR TESTING ======================
        pygame.draw.rect(screen, (0, 0, 0),exit_button, 2)    

        #pygame.draw.rect(screen, (100,0,0),sixtymin_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ninetymin_button, 2)
        #pygame.draw.rect(screen, (0,0,100),custommin_button, 2)

        #pygame.draw.rect(screen, (0,0,100),back_button, 2)
        #pygame.draw.rect(screen, (0,0,100),sleep_button, 2)
        #pygame.draw.rect(screen, (0,100,0),play_button, 2)
        #pygame.draw.rect(screen, (100,0,0),stop_button, 2)

        #pygame.draw.rect(screen, (100,0,0),gear_button, 2)

        #pygame.draw.rect(screen, (100,0,0),therm_button, 2)
        #pygame.draw.rect(screen, (0,100,0),runtime_button, 2)
        #pygame.draw.rect(screen, (0,100,0),wifi_button, 2)
        #pygame.draw.rect(screen, (100,0,0),trends_button, 2)
        #pygame.draw.rect(screen, (100,0,0),levels_button, 2)
        
        #pygame.draw.rect(screen, (0,100,0),filter_button, 2)
        #pygame.draw.rect(screen, (0,0,100),h2o2_button, 2)
        #pygame.draw.rect(screen, (0,0,100),volume_button, 2)
        #pygame.draw.rect(screen, (0,100,0),custom_button, 2)

        #pygame.draw.rect(screen, (0,100,0),cmusicin_button, 2)
        #pygame.draw.rect(screen, (0,100,0),cmusicout_button, 2)
        #pygame.draw.rect(screen, (0,100,0),clightin_button, 2)
        #pygame.draw.rect(screen, (0,100,0),clightout_button, 2)
        #pygame.draw.rect(screen, (0,100,0),clength_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ccol_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ctherapy_button, 2)

        #pygame.draw.rect(screen, (100,0,0),tcur_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ttarg_button, 2)
        #pygame.draw.rect(screen, (0,0,100),pH_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ORP_button, 2)
        #pygame.draw.rect(screen, (0,0,100),specgrav_button, 2)
        #pygame.draw.rect(screen, (0,0,100),lbssalt_button, 2)

        #pygame.draw.rect(screen, (100,0,0),rt_filter_button, 2)
        #pygame.draw.rect(screen, (100,0,0),rt_uvbulb_button, 2)
        #pygame.draw.rect(screen, (100,0,0),rt_salt_button, 2)
        #pygame.draw.rect(screen, (0,100,0),rt_max_button, 2)
        #pygame.draw.rect(screen, (0,100,0),rt_thresh_button, 2)
        #pygame.draw.rect(screen, (0,100,0),rt_reset_button, 2)

        if even: pygame.display.update()
        even = not even

        #pygame.display.flip()

        t= (time.time()>lastLog+60*60) #update once an hour
        if (time.time()>lastInit+60): init=True
        
        #old0=(old_alertMode!=alertMode or old_lightMode!=lightMode)
        #old1=(old_sleepMode!=sleepMode or old_phase!=phase or old_t_offset!=t_offset)
        old1=(old_phase!=phase or old_t_offset!=t_offset)
        old2=((old_max_vol!=max_vol and time.time()>lastsend+.2) or old_targ_temp!=targ_temp_i)
        #old3=(old_min_fade1!=min_fade1 or old_min_fade2!=min_fade2)
        #old4=(old_min_fade1_m!=min_fade1_m or old_min_fade2_m!=min_fade2_m)
        old=(old1 or old2)# or old3 or old4)

        misc=(mouseL!=old_mouseL or remote)
        faded= (fade!=old_fade and (fade==0 or fade==1) and not go)
        
        if (t or go or old or misc or faded or init):
            lastsend=time.time()
            msg_obj={}
            if init or        old_phase!=phase:        msg_obj["phase"]       = phase
            if init or      old_max_vol!=max_vol:      msg_obj["max_vol"]     = max_vol
            if init or     old_t_offset!=t_offset:     msg_obj["t_offset"]    = t_offset
            if init or    old_targ_temp!=targ_temp_i:  msg_obj["targ_temp"]   = targ_temp_i
            if init or   old_manualh2o2!=manualh2o2:   msg_obj["h2o2"]        = manualh2o2
            if init or old_manualfilter!=manualfilter: msg_obj["filter"]      = manualfilter                
            
            if init:
                msg_obj["reinit"]=True
                lastInit=time.time()
                init=False
                
            msg=json.dumps(msg_obj)                  
            if msg!="{}": client.send(msg)
            
            #LOG!!!
            
            #old_lightMode=lightMode
            #old_alertMode=alertMode
            #old_phase=phase
            old_fade=fade
            #old_sleepMode=sleepMode
            old_manualfilter=manualfilter
            old_manualh2o2=manualh2o2
            old_max_vol=max_vol
            old_targ_temp=targ_temp_i
            old_t_offset=t_offset
            #old_min_fade1=min_fade1
            #old_min_fade2=min_fade2
            #old_min_fade1_m=min_fade1_m
            #old_min_fade2_m=min_fade2_m
            
#=============================================================================================================================================================#

pygame.quit()
printer.goodbye(myname,version)
print('ended')
exit(0)