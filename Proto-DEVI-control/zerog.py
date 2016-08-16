# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

myname="zerog.py"
version="v5.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import math
import time
import sys
sys.path.insert(0, abspath)
import printer
printer.silent=True
printer.hello(myname,version)

#================================ SOME GLOBAL VARIABLES ================================                
t_offset=0
fthermo=78.1
max_vol=.65
ct=cur_temp=78.1
old_ct=ct
targ_temp=93.5
pH_lev=7.0
ORP_lev=200
p_heater1234="----"
filtermode=False
h2o2mode=False
thermoString=str(cur_temp)+" °F"

alive=True
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
stopcount=False
lightMode=False
alertMode=False
timeleft_str="READY"
lightsOkay=False
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

phase=PHASE_FLOAT

floatInProgress=False
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
min_fade  =1
min_float =58
min_fade  =1
min_wait  =3
min_plo   =3
min_phi   =20
min_uv    =20
min_h2o2  =1/60*10
totalDuration=-1
countdown_num=3

_shower=0
_fade  =0
_float =0
_fade  =0
_wait  =0
_plo   =0
_filter=0

mainscreen        = True
floatscreen       = False
playfloat         = False
maintenancescreen = False
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

#min_float       = float(printer.fin('min_float'))
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

if custom_duration<2*min_fade: custom_duration=2*min_fade

if printer.fin('floatInProgress')  =="True": floatInProgress   = True
if printer.fin('floatscreen')      =="True": floatscreen       = True
if printer.fin('playfloat')        =="True": playfloat         = True
if printer.fin('maintenancescreen')=="True": maintenancescreen = True
if printer.fin('levelsscreen')     =="True": levelsscreen      = True
if printer.fin('runtimescreen')    =="True": runtimescreen     = True
if printer.fin('trendsscreen')     =="True": trendsscreen      = True
if printer.fin('manualfilter')     =="True": manualfilter      = True
if printer.fin('manualh2o2')       =="True": manualh2o2        = True
reloaded=True

if floatpreset==60: min_float=60-2*min_fade
if floatpreset==90: min_float=90-2*min_fade
if floatpreset==-1: min_float=math.floor(custom_duration)-2*min_fade

if not floatInProgress: lightsOkay=True


#--------------------------------------------------------
def updatelog():
    return 0
    print('log')
    logfile=open(abspath+'log.txt', 'r')
    #logline = logfile.readline().strip()
    lines=logfile.readlines()
    
    for line in lines:
        if line[2:16]=="phase        :":
            line=line.strip()
            print(line[15:]+"   |   "+line[line.find('(')+1:-1])


#--------------------------------------------------------           
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
    


#================================ THE MAIN LOOP ================================                
fadetime=time.time()
def zerogAlive():
    global lastLog
    global debugstring
    global alive,touched,go
    global introfade1,introfade2
    global layer0,layer1,layer2,layer3,layer4
    global floatscreen,maintenancescreen,levelsscreen,runtimescreen,trendsscreen,playfloat,prog
    global phonealpha,alpha0,alpha1,alpha2,alpha3,alpha4,gradalpha
    global lastPrint,reloaded,stepperSpeed
    global min_float,max_vol,lightsOkay,sleepMode
    global manualfilter,manualh2o2,overrideWarning
    global custom_duration, countdown_num, stopcount, fout_customDuration
    global ct,cur_temp,targ_temp,pH_lev,ORP_lev,t_offset,old_ct,thermoString
    global fout_currentTemperature,fout_targetTemperature,fout_pH,fout_ORP
    global floatpreset,floatInProgress,floatelapsed,floatstart,fade,status_str,phase
    global r1screen,r2screen,r3screen
    global rt_filter_max,rt_uvbulb_max,rt_solution_max
    global rt_filter_thresh,rt_uvbulb_thresh,rt_solution_thresh
    global fout_rt_max,fout_rt_thresh
    global filter_runtime,uvbulb_runtime,rt_solution_start,last_rt
    global fadetime
    
    OOO="               "
    printer.p(OOO+"zerogAlive === checking in...")    
    printer.p(OOO+"zerogAlive === entering circuit...")    

    st=time.time()
    fade=1
    tfade=1
    first=0
    while alive:
        ct=time.time()-st
        if phase==PHASE_FADE1:
            tfade=(time.time()-fadetime)/60
            #if int(time.time()-fadetime)!=first:
            #    print('[fade counter: '+str(first)+" | "+str(int(fade*100)/100))
            #    first=int(time.time()-fadetime)
        elif phase==PHASE_FADE2: fade=1-(time.time()-fadetime)/60
        elif phase==PHASE_FLOAT: tfade=0
        else: tfade=0
        if tfade<0: tfade=0
        if tfade>1: tfade=1
        fade=fade*.99+.01*tfade

    printer.fout('targ_lum','end')
    print("ended zerog")
    
    #=============================================================================================================================================================#

    printer.goodbye(myname,version)   

#zerogAlive()

#try:
#    if __name__ == '__main__': zerogAlive()
#finally:
#    print("zerog finally")
#    printer.fout('targ_lum','end')
