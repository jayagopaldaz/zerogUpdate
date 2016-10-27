# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='control'
myname="test.py"
version="v.a.3.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import time
import math
import subprocess
import os
import vlc
import RPi.GPIO as GPIO
import tkinter
import i2crelay as relay
from functools import partial
from tkinter import *
from threading import Thread
from Adafruit_MAX9744 import MAX9744

print(myname+', '+version)

alive=True
OFF=1
ON=0
fthermo=0
amperr=False

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

#-----------------------------------------------
def temperatureThread():
    global fthermo
    thermo_sensor=-1
    st=time.time()
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
                        #print('thermo: '+ str(fthermo))

            except:
                print('thermo exception@171')
                thermo_sensor=-1
        else:
            fthermo='Thermo Error'
            if thermo_sensor!=-1: client.send(json.dumps({'fthermo':fthermo}))
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
music=volume=32
def musicThread():
    global music,amperr
    try:
        amp = MAX9744()
        amp.set_volume(volume)
        music=vlc.MediaPlayer("file://"+abspath+"test.mp3")
        while alive:
            music.play()
            mstate=str(music.get_state())
            if mstate=="State.Ended": music.set_media(music.get_media())
            while alive and mstate == "State.Opening" or mstate == "State.Playing":
                mstate=str(music.get_state())
                amp.set_volume(volume)
        music.stop()

    except:
        amperr=True


#--------------------------------------------------------
def windowThread():
    global volume
    win=tkinter.Tk()
    win.title("ZeroG")
    win.protocol("WM_DELETE_WINDOW", exit)
    winW=798
    winH=408
    win.geometry("%dx%d+0+0" % (winW, winH))

    relayB=[0]*9
    relayV=[0]*9
    relayL=[0]*9
    relay_=[0]*3
    relays___=Frame(win)
    relay_[1]=Frame(relays___)
    relay_[2]=Frame(relays___)
    relays___.pack(side=LEFT, fill=Y)
    relay_[1].pack(side=TOP,    pady=10)
    relay_[2].pack(side=BOTTOM, pady=10)


    #RELAY BUTTONS
    on_off=['Off','On']
    parr=[0,  p_heater1,p_heater2,p_heater3,p_heater4,   p_plo,p_phi,p_h2o2,p_uv]
    def relaycallback(in_):
        GPIO.output(parr[in_], (not GPIO.input(parr[in_])) )
        print(str(in_))
        relay.relay(in_-1, (not relay.relays[in_-1]) )
        relayV[in_].set(on_off[1-GPIO.input(parr[in_])])
    for i in range(1,9):
        frame=Frame(relay_[1+(i>4)])
        if i>4: frame.pack(side=BOTTOM)
        else:   frame.pack(side=TOP)

        relayV[i]=StringVar()
        relayB[i]=Button(frame, text="Relay "+str(1+(i>4))+" in"+str(i-4*(i>4)), pady=12, command=partial(relaycallback, i))
        relayL[i]=Label (frame, textvariable=relayV[i])

        relayV[i].set("Off")
        relayB[i].pack(side=LEFT,padx=20,pady=1)
        relayL[i].pack(side=LEFT)

    #VOLUME
    frame=Frame(win)
    frame.pack(side=TOP, fill=X, padx=60,pady=40)
    volumeV=IntVar()
    volumeV.set(volume)
    volumeL=Label(frame, text="Volume: ")
    volumeS=Scale(frame, variable=volumeV, to=63, orient=HORIZONTAL, length=480, width=40)
    volumeL.pack(side=LEFT,ipady=0)
    volumeS.pack(side=LEFT,ipady=10)

    #TEMPERATURE
    frame=Frame(win)
    frame.pack(side=TOP, fill=X, padx=60,pady=40)
    thermoV=StringVar()
    thermoL=Label(frame, text="Temperature: ")
    thermoS=Label(frame, textvariable=thermoV)
    thermoL.pack(side=LEFT)
    thermoS.pack(side=LEFT)

    #LIGHT PUSHBUTTON
    frame_=Frame(win)
    frame_.pack(side=TOP, fill=X, padx=60,pady=40)
    frame=Frame(frame_)
    frame.pack(side=TOP, fill=X)
    lpushV=StringVar()
    lpushL=Label(frame, text="Light Pushbutton: ")
    lpushS=Label(frame, textvariable=lpushV)
    lpushL.pack(side=LEFT)
    lpushS.pack(side=LEFT)

    frame=Frame(frame_)
    frame.pack(side=TOP, fill=X)
    apushV=StringVar()
    apushL=Label(frame, text="Alert Pushbutton: ")
    apushS=Label(frame, textvariable=apushV)
    apushL.pack(side=LEFT)
    apushS.pack(side=LEFT)

    while alive:
        win.update()
        thermoV.set(str(fthermo)+"°F")
        l_=a_=''
        t=time.time()
        mp=['-','+']
        while time.time()<t+.0001: l_+=mp[GPIO.input(p_user)]
        t=time.time()
        while time.time()<t+.0001: a_+=mp[GPIO.input(p_alert)]
        lpushV.set(l_)
        apushV.set(a_)
        volume=volumeV.get()
        if amperr: volumeL['text']='Amp Error: '

    win.destroy()
    GPIO.output(p_plo, False)
    GPIO.output(p_phi, False)
    GPIO.output(p_h2o2, False)
    GPIO.output(p_uv, False)
    GPIO.output(p_heater1, False)
    GPIO.output(p_heater2, False)
    GPIO.output(p_heater3, False)
    GPIO.output(p_heater4, False)
    GPIO.cleanup()



def exit():
    global alive
    alive=False

#--------------------------------------------------------
f=open(abspath+'var/targ_lum','w')
f.write('alert')
f.close()
Thread(target = windowThread).start()
Thread(target = temperatureThread).start()
Thread(target = musicThread).start()