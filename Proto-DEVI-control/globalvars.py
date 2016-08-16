import time
import printer

alive=True
t_offset=0
fthermo=0
manualfilter=False
manualh2o2=False
targ_temp=93.5
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
phase=PHASE_NONE

fade=1
max_vol=.65
lightMode=False
alertMode=False

try: t_offset = float(printer.fin('t_offset'))
except: pass
try: max_vol  = float(printer.fin('max_vol'))
except: pass

if printer.fin('manualfilter')=="True": manualfilter      = True
if printer.fin('manualh2o2')  =="True": manualh2o2        = True


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