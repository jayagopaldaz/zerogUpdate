# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

mypi='gui'
myname="mdns_hmi.py"
version="v.a.1.00"
abspath='/home/pi/Desktop/'

#=============================================================================================================================================================#
import printer
import netifaces as ni
import time
import socket
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

printer.hello(myname,version)

ip=''
while ip=='':
    try:
        ni.ifaddresses('eth0')
        ip=ni.ifaddresses('eth0')[2][0]['addr']
    except:
        time.sleep(1)
#print('\nmy ip: '+str(ip)+"\n")

class MyListener(object):
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        #print("Service %s added, service info: %s\n-----\n" % (name, info))


desc={'eth0': ip}
info=ServiceInfo("_http._tcp.local.",
                 "zerog hmi._http._tcp.local.",
                 socket.inet_aton("127.0.0.1"),0,0,0,desc)
                 
zeroconf = Zeroconf()
zeroconf.register_service(info)
listener = MyListener()

gotten=False
while not gotten:                   
    sb = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    try:
        info=zeroconf.get_service_info("_http._tcp.local.","zerog control._http._tcp.local.")
        test=info.properties
        gotten=True
    except:
        print("waiting for zerog control service's ip address")        
        time.sleep(3)

