#=============================================================================================================================================================#

mypi='control'
myname="test.py"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import time
import math
import subprocess
import os
import vlc
import RPi.GPIO as GPIO
from subprocess import call
from threading import Thread
from Adafruit_MAX9744 import MAX9744
#import server_control as server
#import client_control as client

print(myname+', '+version)

"""def socketboot():
    import mdns_control as mdns
    hmi_ip=(mdns.info.properties[b'eth0']).decode('utf-8')
    my_ip=mdns.ip
    print("hmi ip: "+hmi_ip)
    client.HOST=hmi_ip
    while not server.ready: continue
    Thread(target=server.init).start()
    Thread(target=client.init).start()

Thread(target=socketboot).start()
#socketboot()
"""

OFF=1
ON=0

fthermo=0

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
GPIO.setup(p_user, GPIO.IN)
GPIO.setup(p_alert, GPIO.IN)


def temperatureThread():
    thermo_sensor=-1
    st=time.time()
    while time.time()<st+6:
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
                        print('thermo: '+ str(fthermo))
                
            except: 
                print('thermo exception@171')
                thermo_sensor=-1
        else:
            fthermo=''
            if thermo_sensor!=-1: client.send(json.dumps({'fthermo':fthermo}))
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            fns = [fn for fn in os.listdir("/sys/bus/w1/devices/")]
            for i in fns:
                if i[:2]=="28": thermo_sensor = '/sys/bus/w1/devices/'+i+'/w1_slave'
                else: thermo_sensor = -1
                
        time.sleep(1)
    
#--------------------------------------------------------
def actionThread():
    def toggle(p):
        print(str(p))
        GPIO.output(p, ON)
        time.sleep(2)
        GPIO.output(p, OFF)
    toggle(p_plo)
    toggle(p_phi)
    toggle(p_h2o2)
    toggle(p_uv)
    toggle(p_heater1)
    toggle(p_heater2)
    toggle(p_heater3)
    toggle(p_heater4)

    def getpinstates(p):
        print('Performing state test on pin #'+str(p))
        s=''
        st=time.time()
        while time.time()<st+.01: s+=str(GPIO.input(p))
        s=s.replace('0000000000000000000000000000000000000000000000000000000000000000','0~')
        s=s.replace('1111111111111111111111111111111111111111111111111111111111111111','1~')
        print(s)
    
    lightToggle=GPIO.input(p_user)
    alertToggle=GPIO.input(p_alert)

    print('\n-----------------------')
    getpinstates(p_user)
    print('press the light toggle...')
    while GPIO.input(p_user)==lightToggle: continue
    getpinstates(p_user)

    print('\n-----------------------')
    getpinstates(p_alert)
    print('press the alert toggle...')
    while GPIO.input(p_alert)==alertToggle: continue
    getpinstates(p_alert)    
                

#--------------------------------------------------------
music=0
def musicThread():
    global music
    amp = MAX9744() #amp = MAX9744(busnum=2, address=0x4C)
    amp.set_volume(0)

    music=vlc.MediaPlayer("file://"+abspath+"default.mp3")
    music.play()
    mstate=str(music.get_state())
    while mstate == "State.Opening": mstate=str(music.get_state())
    for v in range(0,63):
        amp.set_volume(v)
        time.sleep(.1)
    for v in range(62,0,-1):
        amp.set_volume(v)
        time.sleep(.1)

    
#--------------------------------------------------------
def setLED(l,v):
    print('setLED === lum:'+str(l)+", vel:"+str(v))
    printer.fout('targ_lum',str(l))
    printer.fout('targ_lum_vel',str(v))
    

def stop():
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

#--------------------------------------------------------
#                      SERVER STUFF
#--------------------------------------------------------
"""
def getserverupdates():
    global init
    #global sleepMode,
    global new_max_vol,lightMode
    global alive

    try:
        while alive:
            if server.data!='':
                if server.data=='reboot': os.system('reboot')
                if "reinit" not in server.data: print('unabstractor === serverdata:'+str(server.data))
                
                try: j=json.loads(server.data)
                except: print('json exception@getserverupdates')
                
                server.data='' #used it up ;)
                jk=j.keys()
                
                if 'colvals' in jk: printer.fout('colvals',str(j['colvals']))
                if 'phase' in jk:
                    if glb.phase!=int(j['phase']):                    
                        glb.phase=int(j['phase'])
                        if glb.phase==glb.PHASE_NONE: setLED(100,quickLight)
                        if glb.phase==glb.PHASE_FADE1: setLED(0,fade1Light)
                        if glb.phase==glb.PHASE_FLOAT: setLED(0,quickLight)
                        if glb.phase==glb.PHASE_FADE2: setLED(100,fade2Light)
                        if glb.phase>glb.PHASE_FADE2: setLED(100,quickLight)        
                if 'h2o2' in jk: glb.manualh2o2=bool(j['h2o2'])
                if 'filter' in jk: glb.manualfilter=bool(j['filter'])
                if 'targ_temp' in jk: glb.targ_temp=float(j['targ_temp'])
                if 't_offset' in jk: glb.t_offset=float(j['t_offset'])                            
                if 'fade1' in jk: fade1Light=fade1Music=60*float(j['fade1'])                                           
                if 'fade2' in jk: fade2Light=fade1Music=60*float(j['fade2'])
                if 'max_vol' in jk:
                    glb.max_vol=float(j['max_vol'])
                    printer.fout('max_vol',str(glb.max_vol))
                    new_max_vol=True
                if 'lightMode' in jk:                           
                    #lightMode_=bool(j['lightMode'])
                    #if lightMode!=lightMode_:
                    #    lightMode=lightMode_
                    #    if lightMode: setLED(100,quickLight)
                    #    else: setLED(0,quickLight)
                    #    #elif glb.phase!=glb.PHASE_FLOAT: setLED(100,quickLight)
                    lightMode=bool(j['lightMode'])
                    if lightMode: setLED(100,quickLight)
                    else: setLED(0,quickLight)
                    
            time.sleep(.1)
    except: print('serverupdate reboot')
"""        
#--------------------------------------------------------
timeout=time.time()
#Thread(target = getserverupdates).start()

###################################
print('=========================')
print('-------TEMPERATURE-------')
temperatureThread()
###################################
print('========================')
print('-------GPIO TESTS-------')
actionThread()
###################################
print('========================')
print('-------MUSIC TEST-------')
musicThread()
###################################
                  
        
#=============================================================================================================================================================#
