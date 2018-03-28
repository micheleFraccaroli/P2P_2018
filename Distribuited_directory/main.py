import Util
import time
from Config import Config
from time import *
from Vicini import Vicini
from Ricerca import Ricerca
from Retr import Retr
from dataBase import dataBase
from tqdm import tqdm

print('carico configurazione file')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(1)
print('.')
sleep(2)

c=Config() #istanza delle configurazioni
db = dataBase()
db.create(c)
#del db

print("\n--- configurazioni ---\n")
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
#near=Vicini(c)

while True:
    name_search = input("Insert file to search into net: ")
    search = Ricerca(c.selfV4, c.selfV6, c.selfP, c.ttl, c.timeResearch, name_search)
    print("\n--- New research launched ---> pid: " + pktid + "\n")
    pktid = search.query(c)

    for i in tqdm(range(35), desc="Loading: "):
    	time.sleep(1)

	# choice
	print("--- Result for " + pktid + " ---")
	print("[select with the number the file to download")
	res = db.retrieveResponses(pktid)
	i = 1
	for row in res:
		print(i + ") " + "ip: " + row[1] + "  port: " + row[2] + "  md5: " + row[3] + "  file: " + row[4])
		i = i + 1

	choice = input("> ")
	if(choice)