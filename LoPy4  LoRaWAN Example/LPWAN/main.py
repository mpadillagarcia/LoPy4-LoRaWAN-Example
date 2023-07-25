from network import LoRa
import socket
import ubinascii
import struct
import time
import pycom
from pycoproc_1 import Pycoproc


from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

lora = LoRa(mode=LoRa.LORAWAN,region=LoRa.EU868)

# create an ABP authentication parameters
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260... dev address'))[0]
nwk_swkey = ubinascii.unhexlify('49EB... nwk key')
app_swkey = ubinascii.unhexlify('ECF8... app key')
    
lora.add_channel(0, frequency=916800000, dr_min=0, dr_max=4)


# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# wait until the module has joined the network
join_wait = 0
while True:
    time.sleep(2.5)
    if not lora.has_joined():
        print('Not joined yet...')
        join_wait += 1
        if join_wait == 5:
            print("Trying again...")
            lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
            join_wait = 0
    else:
        print("Joined!")
        break

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

# make the socket non-blocking
s.setblocking(False)

time.sleep(5.0)
print(lora.stats())
input()

pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

py = Pycoproc(Pycoproc.PYSENSE)

mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
print("MPL3115A2 temperature: " + str(mp.temperature()))
print("Altitude: " + str(mp.altitude()))
mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
print("Pressure: " + str(mpp.pressure()))


si = SI7006A20(py)
print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")

temp = round(si.temperature(), 2)
humidity = round(si.humidity(), 2)

print("Dew point: "+ str(si.dew_point()) + " deg C")
t_ambient = 24.4
print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")


lt = LTR329ALS01(py)
print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))

li = LIS2HH12(py)
print("Acceleration: " + str(li.acceleration()))
print("Roll: " + str(li.roll()))
print("Pitch: " + str(li.pitch()))

print("Battery voltage: " + str(py.read_battery_voltage()))


tempAndHumidity = int(temp*1000000+humidity*100)
bytes_to_send = tempAndHumidity.to_bytes(4, 'big')
s.send(bytes_to_send)

time.sleep(3)
py.setup_sleep(10)
py.go_to_sleep()
