import smbus
import time

bus=smbus.SMBus(1)
bus.write_byte_data(0x20,0x00,0x00)

relays=[0,0,0,0,0,0,0,0]
def relay(i,val):
    #global bus
    if relays[i]==val: return
    relays[i]=val
    data=0
    for b in range(0,8): data+=relays[b]*2**b
    bus.write_byte_data(0x20,0x09,data)
    print(str(relays))

if __name__ == '__main__':
    for i in range(0,8): relay(i,1)
    for i in range(0,8): relay(i,0)
