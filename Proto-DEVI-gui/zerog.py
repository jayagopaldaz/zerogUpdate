# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='gui'
myname="zerog.py"
version="v.a.1.00"
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

def socketboot():
    import mdns_hmi as mdns
    control_ip= (mdns.info.properties[b'eth0']).decode('utf-8')
    print("zerog control's ip: "+control_ip)
    client.HOST=control_ip
    Thread(target=server.init).start()
    Thread(target=client.init).start()

Thread(target=socketboot).start()

#printer.silent=True
printer.hello(myname,version)


pygame.init()
pygame.display.init()
pygame.display.set_caption("Float Control "+version)
pygame.mouse.set_visible(0)
pygame.font.init()

#clock = pygame.time.Clock()
#FRAMES_PER_SECOND = 0
#deltat = clock.tick(FRAMES_PER_SECOND)
screen=pygame.display.set_mode((800, 480), NOFRAME|RLEACCEL)
stage=pygame.Surface((800,480))

#================================ SOME GLOBAL VARIABLES ================================                
debugstring=''
t_offset=0
fthermo=0
max_vol=.65
ct=78.1
old_cur_temp=0
cur_temp=0
targ_temp=93.5
pH_lev=7.0
ORP_lev=200
p_heater1234="----"
thermoString=str(ct)+" °F"
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
floatelapsed=0
status_str="READY"
phase=-1
stopcount=False
lightMode=True
alertMode=False
timeleft_str="READY"
sleepMode=False

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
runtimescreen     = False
r1screen          = False
r2screen          = False
r3screen          = False
trendsscreen      = False
manualfilter      = False
manualh2o2        = False
floatpreset       = -1
filter_runtime    = 0

min_fade1       = float(printer.fin('min_fade1'))
min_fade2       = float(printer.fin('min_fade2'))
floatstart      = float(printer.fin('floatstart'))
custom_duration = float(printer.fin('custom_duration'))
targ_temp       = float(printer.fin('targ_temp'))
pH_lev          = float(printer.fin('pH_lev'))   
ORP_lev         = float(printer.fin('ORP_lev'))  
t_offset        = float(printer.fin('t_offset'))  
filter_runtime  = float(printer.fin('filter_runtime'))
uvbulb_runtime  = float(printer.fin('uvbulb_runtime'))
rt_solution_start= float(printer.fin('rt_solution_start'))
rt_filter_max   = float(printer.fin('rt_filter_max'))
rt_uvbulb_max   = float(printer.fin('rt_uvbulb_max'))
rt_solution_max = float(printer.fin('rt_solution_max'))
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
runtime  =pygame.image.load(abspath+'guiassets/settings/runtime.png')
rt_edit  =pygame.image.load(abspath+'guiassets/settings/rt_edit.png')
trends   =pygame.image.load(abspath+'guiassets/settings/trends.png')

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
exit_button      = pygame.Rect(0, 0, 20, 20)

sixtymin_button  = pygame.Rect(116, 204-vOffset, 140,140)
ninetymin_button = pygame.Rect(322, 204-vOffset, 140,140)
custommin_button = pygame.Rect(528, 204-vOffset, 140,140)

back_button      = pygame.Rect( 56,  78-vOffset, 76,76)
play_button      = pygame.Rect(190, 340-vOffset, 94,98)
stop_button      = pygame.Rect(505, 340-vOffset, 94,98)
sleep_button     = pygame.Rect( 60, 352-vOffset, 76,76)

gear_button      = pygame.Rect(668, 352-vOffset, 76,76)

therm_button     = pygame.Rect( 60, 352-vOffset, 76,76)
runtime_button   = pygame.Rect(668,  78-vOffset, 76,76)
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


tcur_button      = pygame.Rect(115, 100-vOffset, 270,150)
ttarg_button     = pygame.Rect(400, 100-vOffset, 270,150)
pH_button        = pygame.Rect(115, 270-vOffset, 270,150)
ORP_button       = pygame.Rect(400, 270-vOffset, 270,150)

#rt_total_button  = pygame.Rect(171, 79,480,60)
rt_filter_button = pygame.Rect(71,149,680,44)
rt_uvbulb_button = pygame.Rect(71,219,680,44)
rt_salt_button   = pygame.Rect(71,289,680,44)
rt_max_button    = pygame.Rect(115, 160-vOffset, 270,150)
rt_thresh_button = pygame.Rect(400, 160-vOffset, 270,150)
rt_reset_button  = pygame.Rect(300, 330-vOffset, 200,150)

gradbar_button   = pygame.Rect(gradBarLeft,gradBarTop,gradBarWidth,gradBarHeight)

default_font      = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",16)
tankname_font     = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",54)
status_font       = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",30)

introfade1=0
introfade2=0



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
    global tname

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
    #12:04 pm"
    tar=time.localtime( floatstart+totalDuration*60 )
    ampm=" am"
    hb=tar[3]
    if hb>11: ampm=" pm"
    if hb>12: hb-=12
    mb=tar[4]
    mb_str=str(mb)
    if mb<10: mb_str="0"+mb_str
    timeleft_str=h_str+":"+m_str+":"+s_str+" • "+str(hb)+":"+mb_str+ampm

    fps1=time.time()-fpst
    fps=fps*.99+fps1*.01
    fpst=time.time()
    if not floatInProgress: timeleft_str = "READY"    
    #if lightMode: print(str(lightMode))
    if alertMode or lightMode:        
        timeleft_str+=" - "
        if alertMode: timeleft_str+="ALERT"
        elif lightMode: timeleft_str+="LIGHT ON"
    thermoString=str(int(10*(cur_temp+t_offset))/10)+" °F"

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
    w=700-100-4
    h=400-150-4
    graph = pygame.Surface((w,h))
    graph.fill((25,25,25))
    y2=0
    
    for x in range(0,w-1):
        y1=y2
        pygame.draw.line(graph, (212,228,232), (x,h-y1),(x+1,h-y2), 2)
        y2=150+math.sin(x/100+time.time())*50-25*math.cos(x/50)-x/10
      
    stage.blit(graph,(102,152))
    more1=status_font.render("Trends will become available",1,(28,103,124))
    more2=status_font.render("after more data has been logged :)",1,(28,103,124))
    stage.blit(more1, (400-more1.get_rect().width/2, 50))
    stage.blit(more2, (400-more2.get_rect().width/2, 90))

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
def levelsbars(cur,targ,pH,ORP):
    curtext=str(math.floor(cur*10)/10)
    targtext=str(math.floor(targ*10)/10)
    pHtext=str(math.floor(pH*10)/10)
    ORPtext=str(math.floor(ORP_lev))
    cur=tankname_font.render(curtext,1,(28,103,124))
    targ=tankname_font.render(targtext,1,(28,103,124))
    pH=tankname_font.render(pHtext,1,(28,103,124))
    ORP=tankname_font.render(ORPtext,1,(28,103,124))

    stage.blit(cur, (252-cur.get_rect().width/2, 130-vOffset))        
    stage.blit(targ,(537-targ.get_rect().width/2,130-vOffset))        
    stage.blit(pH,  (252-pH.get_rect().width/2,  310-vOffset))        
    stage.blit(ORP, (537-ORP.get_rect().width/2, 310-vOffset))        

#-----------------------------------------------------------------
def custombar(muin,mout,liin,lout,ldur):
    #asdf
    muin_=tankname_font.render(muin,1,(28,103,124))
    mout_=tankname_font.render(mout,1,(28,103,124))
    liin_=tankname_font.render(liin,1,(28,103,124))
    lout_=tankname_font.render(lout,1,(28,103,124))
    ldur_=tankname_font.render(ldur,1,(28,103,124))
    #floatlength.set_alpha(alpha0)
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
    _fade1   =w/totalDuration*min_fade1
    _float  =w/totalDuration*min_float
    _fade2  =w/totalDuration*min_fade2
    _wait   =w/totalDuration*min_wait
    _plo    =w/totalDuration*min_plo
    _filter =w/totalDuration*min_phi

    gradsurface = pygame.Surface((w,h))
    progbar     = pygame.Surface((w,h))
    progbar.fill((22,27,33))
    progbar.set_alpha(math.floor(255*.7)) # 70% white prog bar... remember ;) ?
    #gradsurface.set_alpha(math.floor(.65*255)) # 65% grad bar... remember ;) ?
    for x in range(0,799):
        #try:
        if True:
            #THE GRADIENT
            if x<_shower:                                                  _r=_g=_b=255#math.floor(255-    (x         )   /_shower*255)
            if x>_shower and x<_shower+_fade1:                             _r=_g=_b=   math.floor(255-   (x-_shower     )    /_fade1*255)
            if x>_shower+_fade1 and x<_shower+_fade1+_float:               _r=_g=_b=0#math.floor(255-  (x-_shower-_fade1   )     /_float*255)
            if x>_shower+_fade1+_float and x<_shower+_fade1+_float+_fade2: _r=_g=_b= math.floor( 0 + (x-_shower-_fade1-_float)      /_fade2*255)
            if x>_shower+_fade1+_float+_fade2+_wait:      
                _r= math.floor(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *4)
                _g= math.floor(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *3)
                _b= math.floor(255-(x-_shower-(_fade1+_fade2)-_float  ) /_filter*255 *2)
                if _r<0: _r=0
                if _g<0: _g=0
                if _b<0: _b=0
                _r+=math.floor( 0 +(x-_shower-(_fade1+_fade2)-_float  ) / _filter*255)
                _b+=math.floor( 0 +(x-_shower-(_fade1+_fade2)-_float  ) / _filter*255)
                if _r>255: _r=255
                if _g>255: _g=255
                if _b>255: _b=255
                
            pygame.draw.line(gradsurface, (_r,_g,_b), (x,0),(x,h), 1)
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


def getserverupdates():
    while alive:
        global cur_temp,fthermo,alertMode,lightMode
        #print("sd=["+server.data+"]")
        if server.data!='':
            #print("sd inside=["+server.data+"]")
            try: j=json.loads(server.data)
            except Exception as e:
                print('server-'+str(e))
                break
            
            server.data='' #used it up ;)
            jk=j.keys()
            
            if 'fthermo'   in jk: cur_temp=fthermo=float(j['fthermo'])
            if 'alertMode' in jk: alertMode=j['alertMode']
            if 'lightMode' in jk: lightMode=bool(j['lightMode'])
        time.sleep(.1)
        
reason=status_font.render("Are both override switches set to OFF?", 1, (194,184,174))
reasonSurface.blit(reason,(400-reason.get_rect().width/2,240-reason.get_rect().height/2))

lastLog=time.time()
lastInit=time.time()-100
if trendsscreen: updatelog()

#================================ THE MAIN LOOP ================================                
##def zerogAlive():
##    global lastLog,lastInit
##    global debugstring
##    global alive,touched,go
##    global introfade1,introfade2
##    global layer0,layer1,layer2,layer3,layer4
##    global floatscreen,settingsscreen,customscreen,levelsscreen,runtimescreen,trendsscreen
##    global playfloat,prog
##    global alpha0,alpha1,alpha2,alpha3,alpha4,gradalpha
##    global lastPrint,reloaded,stepperSpeed
##    global min_float,max_vol,sleepMode
##    global manualfilter,manualh2o2,overrideWarning
##    global min_fade1,min_fade2,custom_duration
##    global countdown_num, countdownstart, stopcount
##    global fout_customMFadein,fout_customMFadeout,fout_customLFadein,fout_customLFadeout,fout_customDuration
##    global ct,cur_temp,targ_temp,pH_lev,ORP_lev,t_offset,old_cur_temp,thermoString
##    global fout_currentTemperature,fout_targetTemperature,fout_pH,fout_ORP
##    global floatpreset,floatInProgress,floatelapsed,floatstart,fade,status_str,phase
##    global r1screen,r2screen,r3screen
##    global rt_filter_max,rt_uvbulb_max,rt_solution_max
##    global rt_filter_thresh,rt_uvbulb_thresh,rt_solution_thresh
##    global fout_rt_max,fout_rt_thresh
##    global filter_runtime,uvbulb_runtime,rt_solution_start,last_rt
##    global json_obj,remote,init
##    global lightMode,alertMode
    
    
if settingsscreen and manualfilter: layer1=filter
if settingsscreen and manualh2o2: layer2=h2o2

OOO="               "
printer.p(OOO+"zerogAlive === checking in...")    
printer.p(OOO+"zerogAlive === entering circuit...")    

#pygame.mouse.set_pos(799,479)
changed=1
mlock=False
old_lightMode=lightMode
old_alertMode=alertMode
old_phase=phase
old_fade=fade
old_sleepMode=sleepMode
old_manualfilter=manualfilter
old_manualh2o2=manualh2o2
old_max_vol=max_vol
old_targ_temp=targ_temp_i=int(targ_temp*10)/10
old_t_offset=t_offset
old_min_fade1=min_fade1
old_min_fade1=min_fade2

mouseL=old_mouseL=0
fout_ct_time=time.time()

Thread(target=getserverupdates).start()
while alive:
    exScr=(not customscreen and not levelsscreen and not runtimescreen and not trendsscreen)

    for e in pygame.event.get(): continue
    #try: debugstring=(str(time.time()%10)[:4]+" : "+str(e.dict['pos'])+" | "+str(pygame.event.get_grab()))
    #except Exception as ex: pass #print(str(ex)+"[pygame.event]")
    
    #pygame.event.pump()
    if time.time()-start<2:
        bglogo.set_alpha(introfade1)
        introfade1+=10
        if introfade1>255: introfade1=255
        screen.blit(bglogo,(0,-vOffset))
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
        else: go=touched=mlock=False
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
        on_tcur      =      tcur_button.collidepoint(pos)
        on_ttarg     =     ttarg_button.collidepoint(pos)
        on_pH        =        pH_button.collidepoint(pos)
        on_ORP       =       ORP_button.collidepoint(pos)
        
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

            if on_runtime and go and settingsscreen and exScr: 
                mlock=True
                runtimescreen = True 
                printer.fout('runtimescreen',str(runtimescreen)) 
                
            if ((on_levels and go and not settingsscreen) or (on_therm and go and settingsscreen)) and exScr: 
                mlock=True
                levelsscreen = True
                ct=cur_temp+t_offset
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
                if on_ccol and go and not mlock:
                    hpos=-.15+1/.75*(pos[0]-ccol_button.left)/(ccol_button.width-20)
                    vpos=-.05+1/.9*(pos[1]-ccol_button.top)/ccol_button.height
                    def clamp(n): return n*(n>0 and n<1) + (n>1)
                    r=clamp( 2*hpos*( clamp((.333-vpos)/.167) + clamp(1-(.833-vpos)/.167)                         ) )
                    g=clamp( 2*hpos*( clamp(1-(.167-vpos)/.167)*(vpos<.333) + clamp((.667-vpos)/.167)*(vpos>=.333) ) )
                    b=clamp( 2*hpos*( clamp(1-(.500-vpos)/.167)*(vpos<.667) + clamp((1.00-vpos)/.167)*(vpos>=.667) ) )
                    w=clamp((hpos-.5)*2)
                    if w==1: r=g=b=w
                    debugstring=str((int(100*r),int(100*g),int(100*b),100*w))
                    client.send(json.dumps({"colvals":{
                        "colval_r":r,
                        "colval_g":g,
                        "colval_b":b,
                        "colval_w":w
                        }}))

                #CUSTOM MUSIC FADEIN--------------------------------
                if on_cmusicin and mouseL and not mlock:
                    stepper=(pos[0]-cmusicin_button.left) / cmusicin_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade1-=.1
                    if stepper>0 and stepperSpeed==0: min_fade1+=.1
                    if stepper<0: min_fade1-=stepperSpeed
                    if stepper>0: min_fade1+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade1<0: min_fade1=0
                    if min_fade1>999: min_fade1=999
                    fout_customMFadein=True
                elif fout_customMFadein:
                    printer.fout('min_fade1',str(min_fade1))
                    if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)
                    fout_customDuration=True
                    fout_customMFadein=False
                    reloaded=True
                elif on_cmusicin: stepperSpeed=0

                #CUSTOM MUSIC FADEOUT--------------------------------
                if on_cmusicout and mouseL and not mlock:
                    stepper=(pos[0]-cmusicout_button.left) / cmusicout_button.width - .5
                    if stepper<0 and stepperSpeed==0: min_fade2-=.1
                    if stepper>0 and stepperSpeed==0: min_fade2+=.1
                    if stepper<0: min_fade2-=stepperSpeed
                    if stepper>0: min_fade2+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.01
                    elif stepperSpeed<2: stepperSpeed*=1.08
                    if min_fade2<0: min_fade2=0
                    if min_fade2>999: min_fade2=999
                    fout_customMFadeout=True
                elif fout_customMFadeout:
                    printer.fout('min_fade2',str(min_fade2))
                    if custom_duration<(min_fade1+min_fade2): custom_duration=(min_fade1+min_fade2)
                    fout_customDuration=True
                    fout_customMFadeout=False
                    reloaded=True
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
                elif on_clightout: stepperSpeed=0


                #CUSTOM DURATION--------------------------------
                if on_clength and mouseL and not mlock:
                    stepper=(pos[0]-clength_button.left) / clength_button.width - .5
                    if stepper<0 and stepperSpeed==0: custom_duration-=1
                    if stepper>0 and stepperSpeed==0: custom_duration+=1
                    if stepper<0: custom_duration-=stepperSpeed
                    if stepper>0: custom_duration+=stepperSpeed
                    if  stepperSpeed<.5: stepperSpeed+=.02
                    elif stepperSpeed<4: stepperSpeed*=1.18
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
            #                            RUNTIMESCREEN
            #============================================================================
            if runtimescreen:
                layer0=runtime
                
                if on_rt_filter and go and not r2screen and not r3screen: mlock=r1screen=True
                if on_rt_uvbulb and go and not r1screen and not r3screen: mlock=r2screen=True
                if on_rt_salt   and go and not r1screen and not r2screen: mlock=r3screen=True
                
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
                    if time.time()>fout_ct_time+3: ct=cur_temp+t_offset
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
            
            
            #============================================================================
            #                            FLOATSCREEN
            #============================================================================                
            if floatscreen and not settingsscreen and exScr:
                if on_back and go: 
                    floatscreen=False
                    printer.fout('floatscreen',str(floatscreen))
                layer0=play
             
                if not manualfilter and not manualh2o2:
                    if on_play and go: prog=0
                    if on_play and go: floatstart=time.time()
                    if on_play and go: floatInProgress=True
                    if on_play and go: printer.fout('floatstart',str(floatstart))
                    if on_play and go: printer.fout('floatInProgress',str(floatInProgress))
                    
                    if on_play and go: playfloat=True 
                    if on_play and go: printer.fout('playfloat',str(playfloat))

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
        if reloaded: reloaded=False
        
        if on_sleep and go and not settingsscreen:
            sleepMode=not sleepMode
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
            if sleepMode: stage.blit(lightoff,(69, 363-vOffset))
            
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
            even=True
            
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
            levelsbars(ct,targ_temp,pH_lev,ORP_lev)

        if customscreen:                
            #debugstring="cust"
            if on_back and go: customscreen=False
            if on_back and go: printer.fout('customscreen',str(customscreen))                
            custombar(
                str(round(min_fade1,1)),
                str(round(min_fade2,1)),
                str(round(min_fade1,1)),
                str(round(min_fade2,1)),
                str(math.floor(custom_duration)))
            #asdf
                
        if changed>0: screen.blit(stage,(0,0))
        tfade=1
        tlights=False
        if floatInProgress:
            tfade=0
            tlights=True
            phase=PHASE_SHOWER
            status_str="SHOWER"
            
            if floatelapsed/60>min_shower:
                if phase!=PHASE_FADE1: lightMode=False
                phase=PHASE_FADE1
                status_str="FADE"
                tfade=(floatelapsed/60-min_shower)/min_fade1
                if tfade>1: tfade=1
            
            if floatelapsed/60>min_shower+min_fade1: 
                tlights=False
                if phase!=PHASE_FLOAT: lightMode=False
                phase=PHASE_FLOAT
                status_str="FLOAT"
            
            if floatelapsed/60>min_shower+min_fade1+min_float:
                tlights=True
                phase=PHASE_FADE2
                status_str="FADE"
                tfade=1-(floatelapsed/60-(min_shower+min_fade1+min_float))/min_fade2
                if tfade<0: tfade=0
            
            if floatelapsed/60>min_shower+(min_fade1+min_fade2)+min_float: 
                if phase!=PHASE_WAIT: lightMode=True
                phase=PHASE_WAIT
                status_str="SHOWER"
                
            if floatelapsed/60>min_shower+(min_fade1+min_fade2)+min_float+min_wait: 
                phase=PHASE_PLO
                status_str="FILTER"
            
            if floatelapsed/60>min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo: 
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
            if phase!=PHASE_NONE: lightMode=True
            phase=PHASE_NONE
            status_str="READY"
            tfade=fade
            if tfade>0: tfade-=.01
            if tfade<0: tfade=0
        #set the actual fade just once! otherwise every so often the other thread will call on it before it is prepared ;)
        
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
        
        if sleepMode:
            #tlights=False
            if tfade<1: tfade+=.1
            if tfade>1: tfade=1
            blackout.set_alpha(128)
            screen.blit(blackout,(0,0))
        
        fade=tfade
                    
        floatelapsed=(time.time()-floatstart)*1+60*min_shower-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+1*min_fade1)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+1*min_fade1+min_float)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo)-10
        #floatelapsed=(time.time()-floatstart)*1+60*(min_shower+(min_fade1+min_fade2)+min_float+min_wait+min_plo+min_phi)-10
    
        #================ ================ ================ ================ ================ 
        #floatelapsed=(time.time()-floatstart)   #this is the not-testing-for one
        #================ ================ ================ ================ ================ 
        
        debug = default_font.render(debugstring,1,(90,90,78))
        screen.blit(debug, (55, 400))
        
        #================ ACTUALLY DRAW TARGET ZONES FOR TESTING ======================
        #pygame.draw.rect(screen, (0, 0, 0),exit_button, 2)    

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

        #pygame.draw.rect(screen, (100,0,0),tcur_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ttarg_button, 2)
        #pygame.draw.rect(screen, (0,0,100),pH_button, 2)
        #pygame.draw.rect(screen, (0,100,0),ORP_button, 2)

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
        if (time.time()>lastInit+30): init=True
        
        #old0=(old_alertMode!=alertMode or old_lightMode!=lightMode)
        old1=(old_sleepMode!=sleepMode or old_phase!=phase or old_t_offset!=t_offset)
        old2=(old_max_vol!=max_vol or old_targ_temp!=targ_temp_i)
        old3=(old_min_fade1!=min_fade1 or old_min_fade2!=min_fade2)
        old=(old1 or old2 or old3)

        misc=(mouseL!=old_mouseL or remote)
        faded= (fade!=old_fade and (fade==0 or fade==1) and not go)
        
        if t or go or old or misc or faded or init:
            msg_obj={}
            #if init or old_alertMode!=alertMode: msg_obj["alertMode"]=alertMode
            #if init or old_lightMode!=lightMode: msg_obj["lightMode"]=lightMode
            if init or old_phase    !=phase    : msg_obj["phase"    ]=phase
            if init or old_sleepMode!=sleepMode: msg_obj["sleepMode"]=sleepMode
            if init or old_max_vol  !=max_vol  : msg_obj["max_vol"  ]=max_vol
            if init or old_t_offset !=t_offset:   msg_obj["t_offset"]=t_offset
            if init or old_targ_temp!=targ_temp_i:msg_obj["targ_temp"]=targ_temp_i
            if init or old_min_fade1!=min_fade1:  msg_obj["fade1"]=round(min_fade1,1)
            if init or old_min_fade2!=min_fade2:  msg_obj["fade2"]=round(min_fade2,1)
            if init or old_manualh2o2  !=manualh2o2:   msg_obj["h2o2"  ]=manualh2o2
            if init or old_manualfilter!=manualfilter: msg_obj["filter"]=manualfilter                
            
            if init:
                msg_obj["reinit"]=True
                lastInit=time.time()
                init=False
                
            msg=json.dumps(msg_obj)                  
            if msg!="{}": client.send(msg)
            
            if t:    
                logMsg ="\n  cur_temp     : "+str(math.floor(cur_temp*10)/10)
                logMsg+="\n  targ_temp    : "+str(math.floor(targ_temp*10)/10)
                logMsg+="\n  pH_lev       : "+str(math.floor(pH_lev*10)/10)
                logMsg+="\n  ORP_lev      : "+str(math.floor(ORP_lev))
                logMsg+="\n  min_float    : "+str(min_float+(min_fade1+min_fade2))
                logMsg+="\n  times        : "+timeleft_str
                logMsg+="\n  phase        : "+dephaser()+" ("+str(phase)+")"
                logMsg+="\n  fade         : "+str(math.floor(fade*100))+"%"
                logMsg+="\n  p_user|alert : "+str(lightMode)+"|"+str(alertMode)
                logMsg+="\n  p_heater1234 : "+p_heater1234 #temporary
                logMsg+="\n  man_filter   : "+str(manualfilter)
                logMsg+="\n  man_h2o2     : "+str(manualh2o2)
                logMsg+="\n  max_vol      : "+str(math.floor(max_vol*100))+"%"
                logMsg+="\n  mainscreen    : "+str(mainscreen and not floatscreen and not settingsscreen)
                logMsg+="\n  floatscreen   : "+str(floatscreen and not settingsscreen and not levelsscreen)
                logMsg+="\n  settingsscreen: "+str(settingsscreen and not levelsscreen and not runtimescreen and not trendsscreen)
                logMsg+="\n  levelsscreen  : "+str(levelsscreen)
                logMsg+="\n  runtimescreen : "+str(runtimescreen)
                logMsg+="\n  trendsscreen  : "+str(trendsscreen)
                logMsg+="\n============================================================================="
                #printer.log(logMsg)
                
                remote=False
                json_obj={
                    'tname'        : tname,
                    'temperature'  : fthermo+t_offset,
                    'cur_temp'     : math.floor(cur_temp*10)/10,
                    'targ_temp'    : math.floor(targ_temp*10)/10,
                    'pH_lev'       : math.floor(pH_lev*10)/10,
                    'ORP_lev'      : math.floor(ORP_lev),
                    'min_float'    : min_float+(min_fade1+min_fade2),
                    'times'        : timeleft_str,
                    'phase'        : status_str,
                    'fade'         : str(math.floor(fade*100))+"%",
                    'p_user_alert' : str(lightMode)+"|"+str(alertMode),
                    'p_heater1234' : p_heater1234, #temporary
                    'man_filter'   : manualfilter,
                    'man_h2o2'     : manualh2o2,
                    'max_vol'      : str(math.floor(max_vol*100))+"%",
                    'custom_duration': math.floor(custom_duration),
                    'playfloat'      : str(playfloat),
                    'mainscreen'     : str(mainscreen and not floatscreen and not settingsscreen),
                    'floatscreen'    : str(floatscreen and not settingsscreen and not levelsscreen),
                    'settingsscreen' : str(settingsscreen and not levelsscreen and not runtimescreen and not trendsscreen),
                    'levelsscreen'   : str(levelsscreen),
                    'runtimescreen'  : str(runtimescreen),
                    'trendsscreen'   : str(trendsscreen),
                }          
            
        old_lightMode=lightMode
        old_alertMode=alertMode
        old_phase=phase
        old_fade=fade
        old_sleepMode=sleepMode
        old_manualfilter=manualfilter
        old_manualh2o2=manualh2o2
        old_max_vol=max_vol
        old_targ_temp=targ_temp_i
        old_t_offset=t_offset
        old_min_fade1=min_fade1
        old_min_fade2=min_fade2
        
#=============================================================================================================================================================#

printer.goodbye(myname,version)   