from Config import Config
from time import *
from Vicini import Vicini
import Util
from Ricerca import Ricerca
from Retr import Retr
from dataBase import dataBase

db = dataBase()
db.destroy()
db.create()

print('carico configurazione file')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(2)

c=Config() #istanza delle configurazioni

print('root 1: ',c.listNode[0][0],' ',c.listNode[0][1],' ',c.listNode[0][2])
print('root 2: ',c.listNode[1][0],' ',c.listNode[1][1],' ',c.listNode[1][2])
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
near=Vicini(c)

name_search = input("Insert file to search into net: ")
search = Ricerca(c.selfV4, c.selfV6, c.selfP, c.ttl, c.timeResearch, name_search)
pktid = search.query()
print("\n--- New research launched ---> pid: " + pktid + " ---\n")

listen_response = Retr() # chiamo la funzione che lancia un thread per ogni ricerca inviata