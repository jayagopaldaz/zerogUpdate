# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='control'
myname="unabstractor.py"
version="v.a.3.00"
abspath='/home/pi/Desktop/'
spoofthermo=False

#=============================================================================================================================================================#
import printer
import i2crelay as relay
import time
import math
import subprocess
import os
import vlc
import random
import json
import RPi.GPIO as GPIO
from subprocess import call
from threading import Thread
from Adafruit_MAX9744 import MAX9744
import server_control as server
import client_control as client
import globalvars as glb

######### INITIALIZE STUFF #########
printer.hello(myname,version)
print(myname+', '+version)
#"""
hmi_ip=False
hmi_ip  = "169.254.0.109"             #HMI-PI'S FIXED IP
client.HOST = hmi_ip
while not server.ready: continue
Thread(target=server.init).start()    # This will actually open the server stream
Thread(target=client.init).start()    # This will actually open the client stream

alive=True
#sleepMode=False
init=True
quickLight=3
fade1Light=60
fade2Light=60
fade1Music=60
fade2Music=60
nomusicfade=False
topHeatOn=30
topHeatOff=3*60

music = 0
vlc_i=0
lastPrint=-30
pdelay=12
tick=0
tock=0
#--------------------------------------------------------
volume=0
volume_base=0
volume_targ=1
volume_time=time.time()
volume_dur=1
new_max_vol=False

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
acoustictherapymode=False
colortherapymode=False

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

i_heater1=0 #heater1
i_heater2=1 #heater2
i_heater3=2 #heater3
i_heater4=3 #heater4


#relay2
p_plo =18
p_phi =16
p_h2o2=15
p_uv  =13

i_plo =4
i_phi =5
i_h2o2=6
i_uv  =7


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

lightToggle=GPIO.input(p_user)
alertToggle=GPIO.input(p_alert)


#--------------------------------------------------------
def thermo_calibrate(t):
    try: return math.floor((t+glb.t_offset)*10)/10
    except: return 0.0

    
def temperatureThread():
    OOO="         "
    printer.p(OOO+"temperatureThread === checking in...")    
    global alive
    global fthermo
    
    printer.p(OOO+"temperatureThread === entering circuit...")    
    
    if spoofthermo:
        t=93
        ti=0
        while alive:
            if t<93.5: ti+=.005
            if t>93.5: ti-=.005
            t+=ti
            client.que({'fthermo':t})
            time.sleep(1)
                
    thermo_sensor=-1
    while alive:
        if thermo_sensor!=-1:
            try:
                f = open(thermo_sensor, 'r')
                lines = f.readlines()
                f.close()

                if lines[0].strip()[-3:] != 'YES': thermo_sensor=-1
                else:
                    thermo_output = lines[1].find('t=')
                    if thermo_output != -1:
                        thermo_string = lines[1].strip()[thermo_output+2:]
                        thermo_c = float(thermo_string) / 1000.0
                        thermo_f = thermo_c * 9.0 / 5.0 + 32.0
                        fthermo=math.floor(thermo_f*10)/10
                        client.que({'fthermo':fthermo})
                
            except: 
                print('thermo exception@171')
                thermo_sensor=-1
        else:
            fthermo=''
            if thermo_sensor!=-1: client.que({'fthermo':fthermo})
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            fns = [fn for fn in os.listdir("/sys/bus/w1/devices/")]
            for i in fns:
                if i[:2]=="28": 
                    thermo_sensor = '/sys/bus/w1/devices/'+i+'/w1_slave'
                    break
                else: thermo_sensor = -1
                
        time.sleep(1)
    
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
    global lightToggle,alertToggle
    global alive
    global tick,tock
    
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
    pu=''
    pa=''
    pu_=''
    pa_=''
    heaterchange=time.time()
    while alive:
        filtermode=glb.manualfilter
        h2o2mode=glb.manualh2o2
        #session=glb.floatInProgress
        #session=(glb.phase!=-1)
        #custom_session_duration=math.floor(glb.custom_duration)
        thermotarg=glb.targ_temp

        #print(str(glb.phase))
        if glb.phase!=glb.PHASE_NONE:                
            #print(str(glb.phase))
            if glb.phase==glb.PHASE_SHUTOFF:
                statusstring="Ready to float :)"
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, OFF)
                GPIO.output(p_h2o2, OFF)
                GPIO.output(p_uv, OFF)
                relay.relay(i_plo, (0))
                relay.relay(i_phi, (0))
                relay.relay(i_h2o2,(0))
                relay.relay(i_uv,  (0))
                glb.phase=glb.PHASE_NONE
            
            bit1=glb.phase%10
            bit2=(glb.phase-bit1)%100
            bit3=glb.phase-bit1-bit2
            
            if bit1==glb.PHASE_PHI:
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, ON)
                relay.relay(i_plo, (0))
                relay.relay(i_phi, (1))
                
                if bit2==glb.PHASE_UV: 
                    GPIO.output(p_uv, ON)
                    relay.relay(i_uv, (1))
                else: 
                    GPIO.output(p_uv, OFF)
                    relay.relay(i_uv, (0))
                    
                if bit3==glb.PHASE_H2O2: 
                    GPIO.output(p_h2o2, ON)
                    relay.relay(i_h2o2, (1))
                else: 
                    GPIO.output(p_h2o2, OFF)
                    relay.relay(i_h2o2, (0))
            
            if glb.phase==glb.PHASE_PLO:
                #print('lo pump!!!!!!!!!!')
                GPIO.output(p_plo, ON)
                relay.relay(i_plo, (1))
            
        elif filtermode or h2o2mode:
            if filtermode:
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, ON)
                GPIO.output(p_uv,  ON)
                relay.relay(i_plo, (0))
                relay.relay(i_phi, (1))
                relay.relay(i_uv,  (1))
            else:
                GPIO.output(p_phi, OFF)
                GPIO.output(p_uv,  OFF)
                relay.relay(i_phi, (0))
                relay.relay(i_uv,  (0))
            if h2o2mode:
                GPIO.output(p_h2o2, ON)
                relay.relay(i_h2o2, (1))
            else:
                GPIO.output(p_h2o2, OFF)
                relay.relay(i_h2o2, (0))

        else:
            GPIO.output(p_plo, OFF)
            GPIO.output(p_phi, OFF)
            GPIO.output(p_h2o2,OFF)
            GPIO.output(p_uv,  OFF)
            relay.relay(i_plo, (0))
            relay.relay(i_phi, (0))
            relay.relay(i_h2o2,(0))
            relay.relay(i_uv,  (0))
            statusstring="Ready to float :)"

        calThermo=thermo_calibrate(fthermo)
        
        #if calThermo<thermotarg and GPIO.input(p_heater1) and time.time()-h12cool>topHeatOff:
        if GPIO.input(p_heater1) and time.time()-h12cool>topHeatOff:
            GPIO.output(p_heater1,ON)
            GPIO.output(p_heater2,ON)
            relay.relay(i_heater1, (1))
            relay.relay(i_heater2, (1))
            h12hot=time.time()            
        if not GPIO.input(p_heater1) and time.time()-h12hot>topHeatOn:
            GPIO.output(p_heater1,OFF)
            GPIO.output(p_heater2,OFF)
            relay.relay(i_heater1, (0))
            relay.relay(i_heater2, (0))
            h12cool=time.time()

        if calThermo<thermotarg-0  and GPIO.input(p_heater3)==OFF:
            GPIO.output(p_heater3,ON)
            GPIO.output(p_heater4,ON)
            relay.relay(i_heater3, (1))
            relay.relay(i_heater4, (1))
            heaterchange=time.time()
        if calThermo>thermotarg+.5 and GPIO.input(p_heater3)==ON:
            GPIO.output(p_heater3,OFF)
            GPIO.output(p_heater4,OFF)
            relay.relay(i_heater3, (0))
            relay.relay(i_heater4, (0))
            heaterchange=time.time()
            
        """
        tick=time.time()
        pu_=''
        pa_=''
        while time.time()-tick<.001 and not filtermode:
            pu_+=str(GPIO.input(p_user))
            pa_+=str(GPIO.input(p_alert))
        
        if pu_.find('0')!=-1 and pu_.find('1')>0: pu+='X'
        elif pu_.find('0')!=-1: pu+='0'
        elif pu_.find('1')!=-1: pu+='1'
        
        if pa_.find('0')!=-1 and pa_.find('1')>0: pa+='X'
        elif pa_.find('0')!=-1: pa+='0'
        elif pa_.find('1')!=-1: pa+='1'
        
        if time.time()-tock>3:
            msg=(str(math.floor(time.time()))+'> ')
            if pu.find('X')!=-1: msg+=('p_user : MISMATCH | ')
            elif pu.find('0')!=-1: msg+=('p_user : 0 | ')
            elif pu.find('1')!=-1: msg+=('p_user : 1 | ')
            
            if pa.find('X')!=-1: msg+=('p_alert: MISMATCH')
            elif pa.find('0')!=-1: msg+=('p_alert: 0')
            elif pa.find('1')!=-1: msg+=('p_alert: 1')
            
            print(msg)
            tock=time.time()
            pu=''
            pa=''
        """
        
        inductance_safeguard=(filtermode or glb.phase>=glb.PHASE_PLO or time.time()<heaterchange+1)
        if GPIO.input(p_user)!=lightToggle and not inductance_safeguard:
            lightToggle=not lightToggle
            lightMode=not lightMode
            client.que({'lightMode':lightMode})
            setLED(100*(lightMode),quickLight)
            
        if GPIO.input(p_alert)!=alertToggle and not inductance_safeguard:
            alertToggle=not alertToggle
            alertMode=not alertMode
            client.que({'alertMode':alertMode})
            if alertMode: setLED('alert',quickLight)
            else:         setLED('safe',2*quickLight)
            
        #if not GPIO.input(p_audio) and not jack_in_use:
        #    jack_plugged_in=True
        #    jack_in_use=True
        #elif GPIO.input(p_audio) and jack_in_use:
        #    jack_unplugged=True
        #    jack_in_use=False
        #if nojack:
        #    jack_in_use=False
        #    jack_plugged_in=False
            
        #glb.debugstring=statusstring
        
        if time.time()>lastPrint+pdelay: #and glb.phase>0:
            #pdelay+=.1
            lastPrint=time.time()
            #printer.p("phase: "+str(glb.phase))
            
            pre=OOO+"actionThread === "
            br="<br>"+pre
            try:
                statusstring=pre+"=========================="
                statusstring+=br+"session      : "+str(session)
                #statusstring+=br+"min_float    : "+str(glb.min_float+2*glb.min_fade)
                statusstring+=br+"raw temp     : "+str(fthermo)
                #statusstring+=br+"times        : "+glb.timeleft_str
                #statusstring+=br+"phase        : "+glb.dephaser()
                #statusstring+="<br>"
                #statusstring+=br+"fade         : "+str(math.floor(glb.fade*100))+"%"
                #statusstring+=br+"lightsOkay   : "+str(glb.lightsOkay)
                #statusstring+="<br>"
                #statusstring+=br+"jack_in_use  : "+str(jack_in_use)
                statusstring+=br+"p_user|alert : "+bool_to_on_off(GPIO.input(p_user))+"|"+bool_to_on_off(GPIO.input(p_alert))
                statusstring+=br+"p_heater1234 : "+heaterString()
                #statusstring+="<br>"
                statusstring+=br+"man_filter   : "+str(filtermode)
                statusstring+=br+"man_h2o2     : "+str(h2o2mode)
                #statusstring+=br+"max_vol      : "+str(math.floor(glb.max_vol*100))+"%"
                #statusstring+=br+"cust_dur     : "+str(custom_session_duration)
                #statusstring+="<br>"
                statusstring+=br+"pdelay       : "+str(math.floor(pdelay*10))+"ds"
                printer.p(statusstring)
            except: printer.p('unabstractor === status string exception')

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
def musicThread():
    OOO="                                                                                                                         "
    printer.p(OOO+"musicThread === checking in...")    
    global music,vlc_i,alive,new_max_vol
    global volume,volume_base,volume_targ,volume_time,volume_dur
    
    try:
        amp = MAX9744() #amp = MAX9744(busnum=2, address=0x4C)
        amp.set_volume(0)
        noAmp=False        
    except Exception as e:
        print('amp init exception')
        noAmp=True

    vlc_i=vlc.Instance()
    music=vlc_i.media_player_new()
    music.set_media(vlc_i.media_new(abspath+"default.mp3"))
    
    printer.p(OOO+"musicThread === entering circuit...")    
    old_ampvol=ampvol=0
    while alive:
        music.play()
        mstate=str(music.get_state())
        if mstate=="State.Ended": music.set_media(music.get_media())
        printer.p(OOO+"musicThread === play...")
        while mstate == "State.Opening": mstate=str(music.get_state())
        while mstate == "State.Playing" or mstate == "State.Paused":
            mstate=str(music.get_state())
            if volume==0 and mstate=="State.Playing" and not auxaudio:
                print('pause') 
                music.pause()
            if volume!=0 and mstate=="State.Paused" and not auxaudio:
                print('unpause')
                music.pause()
            if mstate=="State.Playing" and auxaudio: music.pause()
                
            vd=volume_dur*1.2
            vgap=(volume_targ-volume_base)
            volume=volume_base+vgap/vd*(time.time()-volume_time)
            if volume>1: volume=1
            if volume<0: volume=0
            m ="v:"+str(int(100*volume))+" | gap:"
            m+=str(int(100*vgap))+" | el:"
            m+=str(int(time.time()-volume_time))+" | dur:"
            m+=str(volume_dur)
            #print(m)
            def clamp64(v): #60 cuz clipping
                if v<0: v=0
                if v>60: v=60
                return int(v)
                
            ampvol=.9*ampvol +.1*(volume*60*glb.max_vol)
            if (old_ampvol != ampvol or new_max_vol) and not noAmp:
                amp.set_volume(clamp64(ampvol))
                new_max_vol=False
                #print(str(ampvol))
            old_ampvol=ampvol

    
#--------------------------------------------------------
def setLED(l,v):
    global lightMode
    print('setLED === lum:'+str(l)+", vel:"+str(v))
    if l==100: lightMode=True
    if l==0: lightMode=False
    if v==0: v=.001
    if l!='alert' and l!='safe': l=int(l)
    printer.fout('targ_lum',str(l))
    printer.fout('targ_lum_vel',str(int(v)))
    #printer.fout('targ_lum_time',str(time.time()))
    
def setMusic(l,v):
    global volume,volume_base,volume_targ,volume_time,volume_dur
    if nomusicfade: 
        l=100
        v=.001
    print('setMusic === volume:'+str(l)+", m_vel:"+str(v))
    volume_base=volume
    volume_targ=l/100
    volume_time=time.time()
    volume_dur=v
    
    
#--------------------------------------------------------
#                      SERVER STUFF
#--------------------------------------------------------
def setlm(ll,vl,lm,vm):
    setLED(ll,vl)
    setMusic(lm,vm)
                
auxaudio=False
def getserverupdates():
    global alive, init, auxaudio
    global new_max_vol,lightMode,acoustictherapymode,colortherapymode
    global fade1Light,fade2Light,fade1Music,fade2Music,nomusicfade

    while alive:
        if True:
            if server.data!='':
                if "reinit" not in server.data: print('unabstractor === serverdata:'+str(server.data))
                #if True:
                try: 
                    j=json.loads(server.data)
                    jk=j.keys()
                    server.data='' #used it up ;)
                    
                    if 'fileget' in jk: 
                        os.system('wget -O '+j['fileget']+' http://'+hmi_ip+':8000/temp')
                        music.set_media(vlc_i.media_new(abspath+'usb.mp3'))
                        client.que({'filegotten':True})
                    if 'audiomode' in jk:
                        if j['audiomode']==0: 
                            auxaudio=False
                            music.set_media(vlc_i.media_new(abspath+'default.mp3'))
                        if j['audiomode']==1: 
                            auxaudio=False
                            music.set_media(vlc_i.media_new(abspath+'usb.mp3'))
                        if j['audiomode']==2:
                            if str(music.get_state())=="State.Playing": 
                                auxaudio=True
                                
                            #and str(music.get_state())=="State.Playing": music.pause() 
                            #music.set_media(vlc_i.media_new(abspath+'default.mp3'))
                        
                    if 'colvals' in jk: printer.fout('colvals',str(j['colvals']))
                    if 'phase' in jk:
                        if glb.phase!=int(j['phase']):
                            mus_=0+acoustictherapymode*100
                            lum_=0+colortherapymode*100
                            fade1Music_=acoustictherapymode+(not acoustictherapymode)*fade1Music
                            fade1Light_=colortherapymode+(not colortherapymode)*fade1Light
                            glb.phase=int(j['phase'])
                            if glb.phase==glb.PHASE_NONE:   setlm(100, quickLight, 100,quickLight)                            
                            if glb.phase==glb.PHASE_SHOWER: setlm(100, quickLight, 100,quickLight)                            
                            if glb.phase==glb.PHASE_FADE1:  setLED(lum_,fade1Light_)#music set below
                            if glb.phase==glb.PHASE_FLOAT:  setLED(lum_,quickLight)#,   0,quickLight)
                            if glb.phase==glb.PHASE_FADE2:  setLED(100,fade2Light) #music set below
                            if glb.phase==glb.PHASE_WAIT:   setlm(100, quickLight, 100,quickLight)
                    if 'fadeoutmusic' in jk: setMusic(mus_,_fade1Music)
                    if 'fadeinmusic' in jk: setMusic(100,fade2Music)
                    if 'fade1_light' in jk: fade1Light=60*float(j['fade1_light'])                                           
                    if 'fade2_light' in jk: fade2Light=60*float(j['fade2_light'])
                    if 'fade1_music' in jk: fade1Music=60*float(j['fade1_music'])
                    if 'fade2_music' in jk: fade2Music=60*float(j['fade2_music'])

                    if 'h2o2' in jk: glb.manualh2o2=bool(j['h2o2'])
                    if 'filter' in jk: glb.manualfilter=bool(j['filter'])
                    if 'targ_temp' in jk: glb.targ_temp=float(j['targ_temp'])
                    if 't_offset' in jk: glb.t_offset=float(j['t_offset'])                            
                    if 'topon_lev' in jk: topHeatOn=float(j['topon_lev'])                            
                    if 'topoff_lev' in jk: topHeatOff=float(j['topoff_lev'])                            
                    
                    if 'max_vol' in jk:
                        glb.max_vol=float(j['max_vol'])
                        printer.fout('max_vol',str(glb.max_vol))
                        new_max_vol=True
                        
                    if 'acoustictherapymode' in jk: acoustictherapymode=bool(j['acoustictherapymode'])
                    if 'colortherapymode' in jk: colortherapymode=bool(j['colortherapymode'])
                    if 'lightMode' in jk:                           
                        lightMode=bool(j['lightMode'])
                        if lightMode: setlm(100,quickLight,100,quickLight)
                        else:         setlm(  0,quickLight,  0,quickLight)
                        
                    if 'reboot' in jk: os.system('reboot')
                    
                except: print('json exception@getserverupdates')
        if fade1Music<60*.1: nomusicfade=True
        else: nomusicfade=False
        #print((fade1Music,60*.1,nomusicfade))
        time.sleep(.1)
        
#--------------------------------------------------------
timeout=time.time()
#while not alive and time.time()-timeeout<5: continue

Thread(target = temperatureThread).start()
Thread(target = getserverupdates).start()
Thread(target = actionThread).start()
Thread(target = musicThread).start()
 
#time.sleep(5)
#printer.fout('led_startup',True) 
#printer.goodbye(myname,version)
        
#=============================================================================================================================================================#
