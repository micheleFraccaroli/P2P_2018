import Util
import time
from Config import Config
from Vicini import Vicini
from Ricerca import Ricerca
from Retr import Retr
from dataBase import dataBase
from tqdm import tqdm
from Download import Download


print("____________________________      ________   ______   ")
print("\______   \_____  \______   \    /  _____/  /  __  \  ")
print(" |     ___//  ____/|     ___/   /   \  ___  >      <  ")
print(" |    |   /       \|    |       \    \_\  \/   --   \ ")
print(" |____|   \_______ \____|        \______  /\______  / ")
print("                  \/                    \/        \/  ")
print("\n\n")

#for i in tqdm(range(4), desc="Loading: "):
time.sleep(2)
c=Config() #istanza delle configurazioni
#db = dataBase()
#db.create(c)
#del db

print("\n--- Configurations ---\n")
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
print("\n------------------------\n")
#near=Vicini(c)
'''
while True:
    name_search = input("Insert file to search into net: ")
    search = Ricerca(c.selfV4, c.selfV6, c.selfP, c.ttl, c.timeResearch, name_search)
    print("\n--- New research launched ---> pid: " + pktid + "\n")
    pktid = search.query(c)

    for i in tqdm(range(35), desc="Loading: "):
    	time.sleep(1)

	# choice section
	print("Research termined\n--- Result for " + pktid + " ---")
	print("[select with the number the file to download")
	res = db.retrieveResponses(pktid)
	choice_list = []
	i = 1
	for row in res:
		print(i + ") " + "ip: " + row[1] + "  port: " + row[2] + "  md5: " + row[3] + "  file: " + row[4])
		choice_list.append(row)
		i = i + 1

	choice = input("> ")
		peer = choice_list[choice-1]
		ipv4,ipv6 = peer[1].split('|')
		download = Download(ipv4,ipv6,peer[2],peer[2],peer[4])
		download.download()

del db
'''