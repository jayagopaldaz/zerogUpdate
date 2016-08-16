# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

myname="unabstractor.py"
version="v4.03"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
develop=0
if develop==1: abspath='./'

import sys
sys.path.insert(0, abspath)
import printer
printer.hello(myname,version)
#printer.silent=True
pdelay=12+develop*999999
print(myname+', '+version)
import time
import math
import subprocess
import os
import pygame
import vlc
import random
import json
import _rpi_ws281x as ws
import RPi.GPIO as GPIO
from subprocess import call
from threading import Thread
from Adafruit_MAX9744 import MAX9744
import mdns_control as mdns
import server_control as server
import client_control as client
import zerog

hmi_ip=(mdns.info.properties[b'eth0']).decode('utf-8')
my_ip=mdns.ip
print("hmi ip: "+hmi_ip)
client.HOST=hmi_ip
Thread(target=server.init).start()
Thread(target=client.init).start()

sleepMode=False
init=True
music = 0
lastPrint=0+develop*time.time()-30

LED_CHANNEL    = 0
LED_COUNT      = 64         # How many LEDs to light.
LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM    = 0          # DMA channel to use, can be 0-14.
LED_GPIO       = 18         # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN
leds = ws.new_ws2811_t()
for channum in range(2):    # Initialize all channels to off
    channel = ws.ws2811_channel_get(leds, channum)
    ws.ws2811_channel_t_count_set(channel, 0)
    ws.ws2811_channel_t_gpionum_set(channel, 0)
    ws.ws2811_channel_t_invert_set(channel, 0)
    ws.ws2811_channel_t_brightness_set(channel, 0)

channel = ws.ws2811_channel_get(leds, LED_CHANNEL)
ws.ws2811_channel_t_count_set(channel, LED_COUNT)
ws.ws2811_channel_t_gpionum_set(channel, LED_GPIO)
ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)
ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)
ws.ws2811_init(leds)

OFF=1
ON=0
jack_unplugged=False
jack_plugged_in=False
jack_in_use=False
#fade=0
faded_out=False
unfaded=False
lightMode=not False #inverted for faster on (slower off)
alertMode=False
    
  
thermoString="I can't feel the water"
fthermo=0

session_60=True
session_90=False
session_custom=False
filtermode=False
h2o2mode=False

session=False
#session_start_time=0

#relay1
p_heater1=31 #heater1
p_heater2=33 #heater2
p_heater3=35 #heater3
p_heater4=37 #heater4

#relay2
p_plo=18
p_phi=16
p_h2o2=15
p_uv=13

p_user=8 #user light   (gray)
p_alert=10 #emergency light    (purple)
p_thermo=7 #thermo sensor
p_audio=11 #music from jack

nojack=not False

if printer.myID=='Harmony-DEVI': nojack=True

#reset pins in case they were left on from program termination
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(p_plo, GPIO.OUT)
GPIO.setup(p_phi, GPIO.OUT)
GPIO.setup(p_h2o2, GPIO.OUT)
GPIO.setup(p_uv, GPIO.OUT)
GPIO.setup(p_heater1, GPIO.OUT)
GPIO.setup(p_heater2, GPIO.OUT)
GPIO.setup(p_heater3, GPIO.OUT)
GPIO.setup(p_heater4, GPIO.OUT)
GPIO.output(p_plo, True)
GPIO.output(p_phi, True)
GPIO.output(p_h2o2, True)
GPIO.output(p_uv, True)
GPIO.output(p_heater1, True)
GPIO.output(p_heater2, True)
GPIO.output(p_heater3, True)
GPIO.output(p_heater4, True)
GPIO.cleanup()

#set pins fresh
GPIO.setmode(GPIO.BOARD)
GPIO.setup(p_plo, GPIO.OUT)
GPIO.setup(p_phi, GPIO.OUT)
GPIO.setup(p_h2o2, GPIO.OUT)
GPIO.setup(p_uv, GPIO.OUT)
GPIO.setup(p_heater1, GPIO.OUT)
GPIO.setup(p_heater2, GPIO.OUT)
GPIO.setup(p_heater3, GPIO.OUT)
GPIO.setup(p_heater4, GPIO.OUT)
GPIO.setup(p_thermo, GPIO.IN)
GPIO.setup(p_audio, GPIO.IN)
GPIO.setup(p_user, GPIO.IN)
GPIO.setup(p_alert, GPIO.IN)


#--------------------------------------------------------
def thermo_calibrate(t):
    if printer.myID=='Portland-DEVI1' or printer.myID=='Harmony-DEVI': 
        a1=90
        a2=90.1
        b1=90
        b2=90.1
        
        if printer.myID=='Portland-DEVI1':
            a1=87.4 #DEVI's thermal probe
            a2=88.4 #DEVI's thermal probe
            b1=88.6 #Handheld tester
            b2=89.6 #Handheld tester
        
        if printer.myID=='Harmony-DEVI': 
            a1=96.0 #DEVI's thermal probe
            a2=96.7 #DEVI's thermal probe
            b1=97.0 #Handheld tester
            b2=97.7 #Handheld tester
        
        ad=a2-a1
        bd=b2-b1
        
        t=b1+(t-a1)/ad*bd
        
        return math.floor(t*10)/10

    t+=zerog.t_offset
    return math.floor(t*10)/10
    
    
def temperatureThread():
    OOO="         "
    printer.p(OOO+"temperatureThread === checking in...")    
    global thermoString
    global fthermo
    
    printer.p(OOO+"temperatureThread === entering circuit...")    
    while zerog.alive:
        try:
            catdata = subprocess.Popen(['cat',thermo_sensor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = catdata.communicate()
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            
            #f = open(thermo_sensor, 'r')
            #lines = f.readlines()
            #f.close()

            if lines[0].strip()[-3:] != 'YES':
                return 0
            thermo_output = lines[1].find('t=')
            if thermo_output != -1:
                thermo_string = lines[1].strip()[thermo_output+2:]
                thermo_c = float(thermo_string) / 1000.0
                thermo_f = thermo_c * 9.0 / 5.0 + 32.0
                fthermo=math.floor(thermo_f*10)/10
                zerog.fthermo=fthermo
                #fthermo=thermo_calibrate(thermo_f)
                thermoString=str(thermo_calibrate(fthermo))+" °F"
                client.send(json.dumps({'thermoString':thermoString}))
        except:
            thermoString="I can't feel the water"
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            try:
                fns = [fn for fn in os.listdir("/sys/bus/w1/devices/")]
                if str(fns[0][:2])=="28": thermoID=str(fns[0])
                else: thermoID=str(fns[1])
                thermo_sensor = '/sys/bus/w1/devices/'+thermoID+'/w1_slave'
            except:
                thermo_sensor = ''                
        print('no thermo')
        client.send(json.dumps({'thermoString':thermoString}))
        time.sleep(5)
            
#--------------------------------------------------------
def actionThread():
    OOO="                                                                                                               "
    #printer.p(OOO+"actionThread === checking in...")    
    global session
    global fthermo
    global jack_unplugged,jack_plugged_in,jack_in_use
    global unfaded,faded_out
    global lastPrint,pdelay
    global lightMode,alertMode
    
    try:
        amp = MAX9744() #amp = MAX9744(busnum=2, address=0x4C)
        amp.set_volume(0)
        #print('\namp init\n')
        noAmp=False
    except Exception:
        noAmp=True
        pass
    
    thermo="I can't feel the water"
    alert="No alert, probably"
    status = "Just getting warmed up..."

    DIM=0
    VOL=0
    h12hot=time.time()
    h12cool=time.time()
    #lightToggleTime=-1
    #toggleThreshold=.25
    lightOffTime=time.time()
    togs=0
    #printer.p(OOO+"actionThread === entering circuit...")    
    while zerog.alive:
        getserverupdates()
        try:
            filtermode=zerog.manualfilter
            h2o2mode=zerog.manualh2o2
            #session=zerog.floatInProgress
            #session=(zerog.phase!=-1)
            custom_session_duration=math.floor(zerog.custom_duration)
            zerog.cur_temp=thermo_calibrate(fthermo)
            zerog.fthermo=fthermo
            zerog.thermoString=thermoString
            thermotarg=zerog.targ_temp

            #print(str(zerog.phase))
            if zerog.phase!=zerog.PHASE_NONE:                
                #print(str(zerog.phase))
                if zerog.phase==zerog.PHASE_SHUTOFF:
                    statusstring="Ready to float :)"
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, OFF)
                    GPIO.output(p_h2o2, OFF)
                    GPIO.output(p_uv, OFF)
                    zerog.phase=zerog.PHASE_NONE
                
                bit1=zerog.phase%10
                bit2=(zerog.phase-bit1)%100
                bit3=zerog.phase-bit1-bit2
                
                if bit1==zerog.PHASE_PHI:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    if bit2==zerog.PHASE_UV: GPIO.output(p_uv, ON)
                    else: GPIO.output(p_uv, OFF)
                    if bit3==zerog.PHASE_H2O2: GPIO.output(p_h2o2, ON)
                    else: GPIO.output(p_h2o2, OFF)
                
                if zerog.phase==zerog.PHASE_PLO:
                    #print('lo pump!!!!!!!!!!')
                    GPIO.output(p_plo, ON)
                
            elif filtermode or h2o2mode:
                if filtermode:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    GPIO.output(p_uv, ON)
                else:
                    GPIO.output(p_phi, OFF)
                    GPIO.output(p_uv, OFF)
                if h2o2mode:
                    GPIO.output(p_h2o2, ON)
                else:
                    GPIO.output(p_h2o2, OFF)

            else:
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, OFF)
                GPIO.output(p_h2o2, OFF)
                GPIO.output(p_uv, OFF)
                statusstring="Ready to float :)"

            oldVOL=VOL
            if zerog.phase==zerog.PHASE_FLOAT: VOL=0
            elif sleepMode: VOL*=.99
            else: VOL=VOL*.99+.01*(1-zerog.fade**2)*zerog.max_vol
            if not init: VOL=0
            if oldVOL != VOL:
                if not noAmp:
                    ampvol=math.floor(VOL*63)
                    if ampvol<0: ampvol=0
                    if ampvol>63: ampvol=63
                    amp.set_volume(ampvol)
            
            #thermotarg=93.5
            calThermo=thermo_calibrate(fthermo)
            
            topHeatOn=3*60
            topHeatOff=5*60
            if printer.myID=='Harmony-DEVI': 
                topHeatOn=30
                topHeatOff=3*60
            if printer.myID=='Portland-DEVI1': 
                topHeatOn=15
                topHeatOff=2*60
            
            if calThermo<thermotarg and GPIO.input(p_heater1) and time.time()-h12cool>topHeatOff:
                GPIO.output(p_heater1,ON)
                GPIO.output(p_heater2,ON)
                h12hot=time.time()
            if (calThermo>thermotarg or time.time()-h12hot>topHeatOn) and not GPIO.input(p_heater1):
                GPIO.output(p_heater1,OFF)
                GPIO.output(p_heater2,OFF)
                h12cool=time.time()

            if calThermo<thermotarg and GPIO.input(p_heater3):
                GPIO.output(p_heater3,ON)
                GPIO.output(p_heater4,ON)
            if calThermo>thermotarg+.5 and not GPIO.input(p_heater3):
                GPIO.output(p_heater3,OFF)
                GPIO.output(p_heater4,OFF)
                
            if GPIO.input(p_user) and not not lightMode:
                #print('on  | '+str(togs))
                togs+=1
                if togs>12 and time.time()>lightOffTime+1:
                    zerog.lightMode=lightMode=not True #inverted cuz fast
                    client.send(json.dumps({'lightMode':0})) #was 1 !!!
                    printer.p("USER LIGHT ***NOT*** TRUE");                    
                    #setLED(100,6)
                    setLED(0,6)
                    
            if not GPIO.input(p_user):
                #print('off | '+str(togs))
                lightOffTime=time.time()
                togs=0
                if not lightMode: #inverted
                    zerog.lightMode=lightMode=not False #inverting cuz slow
                    client.send(json.dumps({'lightMode':1})) #was 0 !!!
                    printer.p("USER LIGHT ***NOT*** FALSE");                    
                    #setLED(0,6)
                    setLED(100,6)
                
            if zerog.fade==1 and unfaded: unfaded=False
            if zerog.fade!=1 and faded_out: faded_out=False

            #removed portland conditional
            if GPIO.input(p_alert) and not alertMode and False:
                #alertStart=time.time()
                printer.p("Emergency Light On")
                zerog.alertMode=True
                alertMode=True
                setLED('alert',6)
                client.send(json.dumps({'alertMode':alertMode}))
            if not GPIO.input(p_alert) and alertMode and False: 
                printer.p("Emergency Light Off")
                zerog.alertMode=False
                alertMode=False
                setLED('safe',12)
                client.send(json.dumps({'alertMode':alertMode}))
                
            #if not GPIO.input(p_audio) and not jack_in_use:
            #    jack_plugged_in=True
            #    jack_in_use=True
            #elif GPIO.input(p_audio) and jack_in_use:
            #    jack_unplugged=True
            #    jack_in_use=False
            #if nojack:
            #    jack_in_use=False
            #    jack_plugged_in=False
                
            #zerog.debugstring=statusstring
            
            if time.time()>lastPrint+pdelay: #and zerog.phase>0:
                #pdelay+=.1
                lastPrint=time.time()
                #printer.p("phase: "+str(zerog.phase))
                
                pre=OOO+"actionThread === "
                br="<br>"+pre
                try:
                    statusstring=pre+"=========================="
                    statusstring+=br+"session      : "+str(session)
                    statusstring+=br+"min_float    : "+str(zerog.min_float+2*zerog.min_fade)
                    statusstring+=br+"temperature  : "+thermoString
                    statusstring+=br+"raw temp     : "+str(fthermo)
                    statusstring+=br+"times        : "+zerog.timeleft_str
                    statusstring+=br+"phase        : "+zerog.dephaser()
                    statusstring+="<br>"
                    statusstring+=br+"fade         : "+str(math.floor(zerog.fade*100))+"%"
                    statusstring+=br+"lightsOkay   : "+str(zerog.lightsOkay)
                    statusstring+="<br>"
                    statusstring+=br+"jack_in_use  : "+str(jack_in_use)
                    statusstring+=br+"p_user|alert : "+bool_to_on_off(GPIO.input(p_user))+"|"+bool_to_on_off(GPIO.input(p_alert))
                    statusstring+=br+"p_heater1234 : "+heaterString()
                    statusstring+="<br>"
                    statusstring+=br+"man_filter   : "+str(filtermode)
                    statusstring+=br+"man_h2o2     : "+str(h2o2mode)
                    statusstring+=br+"max_vol      : "+str(math.floor(zerog.max_vol*100))+"%"
                    statusstring+=br+"cust_dur     : "+str(custom_session_duration)
                    statusstring+="<br>"
                    statusstring+=br+"pdelay       : "+str(math.floor(pdelay*10))+"ds"
                    printer.p(statusstring)
                except: printer.p('unabstractor === status string exception')
        except:
            zerog.alive=False
        #print(str(zerog.fade))

    #cleanup on exit
    GPIO.output(p_plo, False)
    GPIO.output(p_phi, False)
    GPIO.output(p_h2o2, False)
    GPIO.output(p_uv, False)
    GPIO.output(p_heater1, False)
    GPIO.output(p_heater2, False)
    GPIO.output(p_heater3, False)
    GPIO.output(p_heater4, False)
    GPIO.cleanup()
    music.stop()
    #pygame.mixer.music.stop()
    
    try:
        #global client
        amp.set_volume(0)
        #print('amp off')
        #color = [ (0,0,0) ] * 512
        #client.put_pixels(color)
    except Exception:
        print('exit')
        exit(0)
        pass


def bool_to_on_off(b):
    if b: return "ON"
    else: return "OFF"
    
def heaterString():
    h1="OFF"
    h2="OFF"
    h3="OFF"
    h4="OFF"
    if GPIO.input(p_heater1)==ON: h1="ON"
    if GPIO.input(p_heater2)==ON: h2="ON"
    if GPIO.input(p_heater3)==ON: h3="ON"
    if GPIO.input(p_heater4)==ON: h4="ON"
    return h1+"|"+h2+"|"+h3+"|"+h4
    
#--------------------------------------------------------
#--------------------------------------------------------
def musicThread():
    OOO="                                                                                                                         "
    printer.p(OOO+"musicThread === checking in...")    
    global jack_in_use
    global jack_plugged_in
    global jack_unplugged
    #global fade
    global faded_out
    global unfaded
    global music
    
    #pygame.mixer.init()
    #pygame.mixer.music.load(abspath+"default.mp3")
    music=vlc.MediaPlayer("file://"+abspath+"default.mp3")
    #print("file://"+abspath+"default.mp3")
    #music.play()
    printer.p(OOO+"musicThread === entering circuit...")    
    while zerog.alive:
        music.play()
        mstate=str(music.get_state())
        #print(mstate+'\n')
        if mstate=="State.Ended": music.set_media(music.get_media())
        printer.p(OOO+"musicThread === play...")
        while mstate == "State.Opening": mstate=str(music.get_state())
        #while mstate == "State.Playing": continue
        
        while mstate == "State.Playing" or mstate == "State.Paused":
            mstate=str(music.get_state())
            #print(mstate)
            #if (jack_plugged_in and not nojack) or (zerog.fade==1 and not faded_out and (not jack_in_use or nojack)):
            if zerog.fade==1 and mstate=="State.Playing":
                print('pause')
                music.pause()
                #printer.p(OOO+"musicThread === pause...")
                #if mstate=="State.Playing":
                #    print('pause')
                #    music.pause()
                #if not nojack: jack_plugged_in=False
                #faded_out=True
                
            #if zerog.fade!=1 and (jack_unplugged or (not unfaded and not jack_in_use)):
            if zerog.fade!=1 and mstate=="State.Paused":
                print('unpause')
                music.pause()
                #printer.p(OOO+"musicThread === ...unpause")                    
                #if mstate=="State.Paused":
                #    print('unpause')
                #    music.pause()
                #jack_unplugged=False
                #unfaded=True
                
            continue
        continue        

    
#--------------------------------------------------------
def setLED(l,v):
    if not lightMode:
        l=100
        v=6
    elif not alertMode and (sleepMode and l>0): return
    print('[setLED: lum='+str(l)+", vel="+str(v)+']')
    printer.fout('targ_lum',str(l))
    printer.fout('targ_lum_vel',str(v))
    printer.fout('targ_lum_time',str(time.time()))    
    
    
#--------------------------------------------------------
Thread(target = zerog.zerogAlive).start()
timeout=time.time()
#while not zerog.alive and time.time()-timeeout<5: continue

if zerog.alive or True:
    Thread(target = temperatureThread).start()
    Thread(target = actionThread).start()
    Thread(target = musicThread).start()
                  

#--------------------------------------------------------
#--------------------------------------------------------
#---------             SERVER STUFF
#--------------------------------------------------------
#--------------------------------------------------------
def getserverupdates():
    global init
    global sleepMode

    if server.data!='':
        #print('unabstractor === serverdata:'+str(server.data))
        if server.data=='reboot': os.system('reboot')
        try: j=json.loads(server.data)
        except: return False
        
        server.data='' #used it up ;)
        jk=j.keys()
        if 'phase' in jk:
            if zerog.phase!=int(j['phase']):                    
                zerog.phase=int(j['phase'])
                if zerog.phase==zerog.PHASE_NONE: setLED(100,6)
                if zerog.phase==zerog.PHASE_FADE1: setLED(0,60)
                if zerog.phase==zerog.PHASE_FLOAT: setLED(0,6)
                if zerog.phase==zerog.PHASE_FADE2: setLED(100,60)
                if zerog.phase>zerog.PHASE_FADE2: setLED(100,6)
        if 'fade_t' in jk: zerog.fadetime=time.time()-j['fade_t']
        if 'h2o2'   in jk: zerog.manualh2o2  =bool(j['h2o2'])
        if 'filter' in jk: zerog.manualfilter=bool(j['filter'])
        if 'max_vol' in jk: zerog.max_vol    =float(j['max_vol'])
        if 'targ_temp' in jk: zerog.targ_temp=float(j['targ_temp'])
        if 'sleepMode' in jk and not 'reinit' in jk:
            sleepMode=bool(j['sleepMode'])
            if sleepMode: setLED(0,6)
            elif zerog.phase!=zerog.PHASE_FLOAT: setLED(100,6)
                
printer.goodbye(myname,version)
        
#=============================================================================================================================================================#
