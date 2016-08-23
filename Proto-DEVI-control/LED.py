#=============================================================================================================================================================#

mypi='control'
myname="LED.py"
version="v.a.1.20"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import printer
import json
import time
import math
import _rpi_ws281x as ws
import random
import RPi.GPIO as GPIO
from threading import Thread

printer.hello(myname,version)

b=10
lum=0
tlum=0
vel=1
timer=0
utimer=0
thresh=.5
luma=0
f=1
alive=True
alert=False
OOO="       "

r_cv_t_default=.8
g_cv_t_default=.7
b_cv_t_default=1
w_cv_t_default=1
r_cv_t=g_cv_t=b_cv_t=w_cv_t=0
r_cv=g_cv=b_cv=w_cv=0


def getupdates():
    global plum,tlum,vel,alive,utimer,alert
    global r_cv_t,g_cv_t,b_cv_t,w_cv_t
    tlum_s=''
    while alive:
        utimer=time.time()
        if lum==100:
            try:
                colvals_=printer.fin('colvals').replace("'",'"')
                cv=json.loads(colvals_)
                r_cv_t=float(cv['colval_r'])
                g_cv_t=float(cv['colval_g'])
                b_cv_t=float(cv['colval_b'])
                w_cv_t=float(cv['colval_w'])
            except: print('colval exception')
        else:
            r_cv_t=r_cv_t_default
            g_cv_t=g_cv_t_default
            b_cv_t=b_cv_t_default
            w_cv_t=w_cv_t_default

        try:
            tlum_s = printer.fin('targ_lum')
            vel_s  = printer.fin('targ_lum_vel')            
        except: print('l/v exception')
        
        if   tlum_s=='alert': alert=True
        elif tlum_s=='safe' : alert=False
        elif tlum_s=="end"  : alive=False
        elif not alert:
            try: tlum=float(tlum_s)                     
            except: print('tlum float exception')                    
                
        try: vel=float(vel_s)
        except: print('vel float exception')

        time.sleep(.25)
                
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(21,GPIO.OUT)
pwm=GPIO.PWM(21,30)

# LED configuration.
LED_CHANNEL    = 0
LED_COUNT      = 64         # How many LEDs to light.
LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM    = 5          # DMA channel to use, can be 0-14.
LED_GPIO       = 18 #(12)   # GPIO connected to the LED signal line.  Must support PWM!
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
    try:
        n=int(n)
        if n<0: n=0
        if n>255: n=255
        return n
    except: return 0

def pwm_shimmer():
    if int(b*1)<1: return 0
    elif b<pwmCap: return random.random()<b/pwmCap
    else: return 1

def shimmer(r): return random.random()<(luma*r - int(luma*r))
def rcol(k): return byteclamp(r_cv*8  *luma+shimmer(8)-1)
def gcol(k): return byteclamp(g_cv*16 *luma+shimmer(16)-1)
def bcol(k): return byteclamp(b_cv*254*luma+pwm_shimmer())
def wcol(k): return byteclamp(w_cv*255*luma+shimmer(255)-2)

def col(j):
    if alert: 
        wave=.5+.5*math.sin(j/20+time.time())
        r=byteclamp(8*wave)
        g=byteclamp(16*wave)
        b=byteclamp(256*wave)
        w=byteclamp(256*wave)
        if j%4==0: return g*65536+r*256+b
        if j%4==1: return w*65536+g*256+r
        if j%4==2: return b*65536+w*256+g
        if j%4==3: return r*65536+b*256+w

        
    if j%4==0: return gcol(j+0)*65536+rcol(j+0)*256+bcol(j+0)
    if j%4==1: return wcol(j+0)*65536+gcol(j+1)*256+rcol(j+1)
    if j%4==2: return bcol(j+1)*65536+wcol(j+1)*256+gcol(j+2)
    if j%4==3: return rcol(j+2)*65536+bcol(j+2)*256+wcol(j+2)


######################
thresh=.5
thresh_hi=.25
pwmCap=9         #9 to 100
poly=6
polyb=3
plumx=0
tlum=0
lum=0
######################
Thread(target=getupdates).start()

alert=False
lastlog=time.time()
printer.p(OOO+"LED === checking in...")

def getlumb(x):
    x_lo=x/thresh
    x_hi=(x-thresh_hi)/(1-thresh_hi)
    
    if x<thresh: y2=100*x_lo**polyb
    else: y2=100
    if x>thresh_hi: y1=100*x_hi**poly    
    else: y1=0

    if y1<0:  y1=0
    if y1>99: y1=100    
    if y2<0:  y2=0
    if y2>99: y2=100    
        
    return (y1,y2)

#curve_pos = progress as el from the previous lum to the current lum
#return x from 0 to 1
def get_x_from_lum(L):
    for x in range(1,100):
        if getlumb(x/100)[0]>=L: return (x-1)/100
    return 1

def get_x_from_b(B):
    for x in range(1,100):
        if getlumb(x/100)[1]>=B: return (x-1)/100
    return 1
    
def get_curve_pos(prog):
    return (plumx+(tlumx-plumx)*prog)

def report():
    msg=OOO+"LED === "
    msg+=(str(int(time.time()-utimer))+","+str(int(time.time()-timer)))
    msg+=(", !: "+str(alert))
    msg+=(", vel: "+str(vel))
    msg+=(", lum: "+str(int(100*lum)))+"/10000"
    msg+=(", tlum: "+str(tlum))
    #msg+=(", plumx: "+str(int(100*plumx)))
    #msg+=(", b: "+str(int(1*b)))        
    msg+=(", rgbw: "+str( (int(100*r_cv),int(100*g_cv),int(100*b_cv),int(100*w_cv)) ) )        
    msg+=(", rgbwt: "+str( (int(100*r_cv_t),int(100*g_cv_t),int(100*b_cv_t),int(100*w_cv_t)) ) )        
    #msg+=(", crv: "+str(int(100*get_curve_pos(el))))
    #msg+=(", el: "+str(int(100*el)))        
    printer.p(msg)

tlum_=tlum=tlumx=plumx=0
pwm.start(pwmCap) 
while alive:
    if lum<100:
        r_cv_t=r_cv_t_default
        g_cv_t=g_cv_t_default
        b_cv_t=b_cv_t_default
        w_cv_t=w_cv_t_default
        
    vv=.01/(1+(tlum<lum))
    r_cv=(1-vv)*r_cv+vv*r_cv_t*r_cv_t_default
    g_cv=(1-vv)*g_cv+vv*g_cv_t*g_cv_t_default
    b_cv=(1-vv)*b_cv+vv*b_cv_t*b_cv_t_default
    w_cv=(1-vv)*w_cv+vv*w_cv_t*w_cv_t_default
    
    if tlum_!=tlum:
        tlumx=get_x_from_lum(tlum)
        plumx=get_x_from_lum(lum)        
        plumxB=get_x_from_b(b)
        if plumxB<plumx and b<100: plumx=plumxB
        tlum_=tlum
        timer=time.time()

    el=(time.time()-timer)/vel
    if el>1: el=1
    if el<0: el=0

    #ob=int(1*b)        
    ob=b        
    (lum,b)=getlumb(get_curve_pos(el))
    if alert: b=100
    if b!=ob and b>=pwmCap: pwm.ChangeDutyCycle(b) 
    
    luma=lum/100
    
    for i in range(LED_COUNT): ws.ws2811_led_set(ws.ws2811_channel_get(leds,0),i,col(i))
    ws.ws2811_render(leds)        
     
    if time.time()>lastlog+5:
        lastlog=time.time()
        report()
     
printer.p(OOO+"LED === checking out...")    
for i in range(61): ws.ws2811_led_set(ws.ws2811_channel_get(leds,0),i,0x000000)
ws.ws2811_render(leds)
ws.ws2811_fini(leds)
ws.delete_ws2811_t(leds)
pwm.stop()
printer.fout('targ_lum','end')
printer.goodbye(myname,version)
print('ended')
