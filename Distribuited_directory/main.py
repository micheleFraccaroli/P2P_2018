from Config import Config
from time import sleep

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
c.pissi()