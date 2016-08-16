6#=============================================================================================================================================================#

myname="LED.py"
version="v1.01"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import sys
sys.path.insert(0, abspath)
import printer
printer.hello(myname,version)
#printer.silent=True

import time
import math
import _rpi_ws281x as ws
import random
import RPi.GPIO as GPIO
from threading import Thread

b=10
lum=0
tlum=0
vel=1
timer=0
thresh=.5
luma=0
f=1
alive=True
OOO="       "
r_cv=1
g_cv=.7
b_cv=1
w_cv=1

def getupdates():
    global plum,tlum,vel,alive,timer
    while alive:
        tlum_s = printer.fin('targ_lum')
        vel_s  = printer.fin('targ_lum_vel')
        timer_s= printer.fin('targ_lum_time')

        if   tlum_s=='alert': alert=True
        elif tlum_s=='safe' : alert=False
        elif tlum_s=="end"  : alive=False
        else:
            try: tlum=float(tlum_s)                     
            except: printer.p('tlum float exception')                    
                
        try: vel=float(vel_s)
        except: printer.p('vel float exception')

        try: timer=float(timer_s)
        except: printer.p('timer float exception')

        time.sleep(.25)
                
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(21,GPIO.OUT)
pwm=GPIO.PWM(21,30)
pwm.start(10) #9 to 100

# LED configuration.
LED_CHANNEL    = 0
LED_COUNT      = 64         # How many LEDs to light.
LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM    = 5          # DMA channel to use, can be 0-14.
LED_GPIO       = 18         # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN

leds = ws.new_ws2811_t()

# Initialize all channels to off
for channum in range(2):
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

def byteclamp(n):
    n=int(n)
    if n<0: n=0
    if n>255: n=255
    return n

def wave(y,a,m,wl,f):
    if alert: return luma*(.1+2*a*math.sin(m/wl+time.time()*f*2))        
    else:     return luma*(y+a*math.sin(m/wl+time.time()*f))
    
def lumar(l): return wave(.95,.05,l,.200,800000)    
def lumag(l): return wave(.95,.05,l,.200,800000)
def lumab(l): return wave(.95,.05,l,.200,800000)
def lumaw(l): return wave(.95,.05,l,.200,800000)              

def rcol(k): return byteclamp(r_cv*8  *lumar(k)+.25*math.sin(k/20+time.time()*8000000)-1)
def gcol(k): return byteclamp(g_cv*16 *lumag(k)+.25*math.sin(k/20+time.time()*8000000)-1)
def bcol(k): return byteclamp(w_cv*254*lumab(k)+luma*.25+.25*math.sin(k/20+time.time()))+f
def wcol(k): return byteclamp(b_cv*255*lumaw(k)+.25*math.sin(k/20+time.time()*8000000)-2)

def col(j):
    if j%4==0: return gcol(j+0)*65536+rcol(j+0)*256+bcol(j+0)
    if j%4==1: return wcol(j+0)*65536+gcol(j+1)*256+rcol(j+1)
    if j%4==2: return bcol(j+1)*65536+wcol(j+1)*256+gcol(j+2)
    if j%4==3: return rcol(j+2)*65536+bcol(j+2)*256+wcol(j+2)


######################
thresh=.5
thresh_hi=.25
pwmCap=9
poly=6
polyb=3
plum=0
tlum=0
#printer.fout('targ_lum_time',str(time.time()+5))
#printer.fout('targ_lum_vel', '10')
#printer.fout('targ_lum', '0')
######################
Thread(target=getupdates).start()

alert=False
lastlog=time.time()
printer.p(OOO+"LED === checking in...")

def getlumb(x):
    #x=(time.time()-timer)/vel
    x_lo=x/thresh
    x_hi=(x-thresh_hi)/(1-thresh_hi)
    
    if x<thresh: y2=pwmCap+(100-pwmCap)*x_lo**polyb
    else: y2=100
    
    if x>thresh_hi: y1=100*x_hi**poly
    elif x>0: y1=.001
    else: y1=0

    if y1<0: y1=0
    if y1>100: y1=100    
    if y2<pwmCap: y2=pwmCap
    if y2>99:     y2=100    
        
    return (y1,y2)

#curve_pos = progress as el from the previous lum to the current lum
#return x from 0 to 1
def get_x_from_y(y):
    for x in range(0,100):
        if getlumb(x/100)[0]>y: return x/100
    return 1
    
def get_curve_pos(prog):
    xlum1=plum/100
    xlum2=tlum/100
    return xlum1+(xlum2-xlum1)*prog

try:
#for asdf in range(0,1):
    tlum_=tlum=plum=0
    while alive:
        if tlum_!=tlum:
            plum=tlum_
            tlum_=tlum

        if time.time()>lastlog+1:
            lastlog=time.time()
            printer.p(OOO+"LED === lum:"+str(lum)+" | b:"+str(b))
            print("time: "+str(int(time.time()-timer)))
            #print("lum : "+str(lum))
            #print("vel : "+str(vel))
            print("tlum: "+str(tlum))
            print("plum: "+str(plum))
            #print("b   : "+str(int(b)))
            print("----------------------------------")
            #print(str(getlumb(get_curve_pos(el))))
            #print(str(get_curve_pos(el)))
        ob=int(b)

        el=(time.time()-timer)/vel
        if el>1: el=1
        if el<0: el=0
        (lum,b)=getlumb(get_curve_pos(el))

        if el==1: plum=tlum
        if int(b)!=ob: pwm.ChangeDutyCycle(int(b))            
        luma=lum/100
        
        if lum==0: f=0
        else: f=1
        
        for i in range(LED_COUNT): ws.ws2811_led_set(ws.ws2811_channel_get(leds,0),i,col(i))
        ws.ws2811_render(leds)        
        
except: printer.p(OOO+"LED === SOME KIND OF EXCEPTION!!!")
            
printer.p(OOO+"LED === checking out...")    
for i in range(61): ws.ws2811_led_set(ws.ws2811_channel_get(leds,0),i,0x000000)
ws.ws2811_render(leds)
ws.ws2811_fini(leds)
ws.delete_ws2811_t(leds)
pwm.stop()
printer.fout('targ_lum','end')
printer.goodbye(myname,version)
print('ended')
