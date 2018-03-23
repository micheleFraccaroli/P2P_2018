from Config import Config
from time import *
from Vicini import Vicini
import Util

Util.define_g()

print('carico configurazione file')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(2)

c=Config()
print('root 1: ',c.listNode[0][0],' ',c.listNode[0][1],' ',c.listNode[0][2])
print('root 2: ',c.listNode[1][0],' ',c.listNode[1][1],' ',c.listNode[1][2])
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
near=Vicini(c)
print(near.pack)
pissi=Util.ip_packet16()
pissi2=Util.ip_packet16()

Util.ipPacket16[pissi]=int(time())
response=Util.ip_packet16_validation(pissi,c.timeIdPacket)
print('\n\n\n')
print(response)
response=Util.ip_packet16_validation(pissi2,c.timeIdPacket)
print(response)
response=Util.ip_packet16_validation(pissi2,c.timeIdPacket)
print(response)
print(Util.ipPacket16)
print(Util.ipPacket16)
#near.cercaVicini(c)