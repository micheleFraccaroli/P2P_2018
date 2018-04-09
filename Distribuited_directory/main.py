import sys
import Util
import time
import ipaddress as ipad
import random as ra
import threading as th
from Config import Config
from Vicini import Vicini
from Ricerca import Ricerca
from Retr import Retr
from dataBase import dataBase
from tqdm import tqdm
from Download import Download
from Central_Thread import Central_Thread
from Upload import Upload

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


print(bcolors.MAGENTA + "____________________________      ________   ______   " + bcolors.ENDC)
print(bcolors.MAGENTA + "\______   \_____  \______   \    /  _____/  /  __  \  " + bcolors.ENDC)
print(bcolors.OKBLUE + " |     ___//  ____/|     ___/   /   \  ___  >      <  " + bcolors.ENDC)
print(bcolors.OKBLUE + " |    |   /       \|    |       \    \_\  \/   --   \ " + bcolors.ENDC)
print(bcolors.CYAN + " |____|   \_______ \____|        \______  /\______  / " + bcolors.ENDC)
print(bcolors.CYAN + "                  \/                    \/        \/  " + bcolors.ENDC)


#for i in tqdm(range(4), desc="Loading: "):
#time.sleep(2)
c=Config() #istanza delle configurazioni
db = dataBase()
db.destroy()
db.create(c)
#del db

print("--- Configurations ---\n")
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
print("\n----------------------\n")
#near=Vicini(c)

lock = th.Lock()

# background thread for NEAR and QUER
central_thread = Central_Thread(c, lock)
central_thread.start()

upl = Upload(c.selfP+10)
upl.start()

while True:
	name_search = input(bcolors.OKBLUE + "Search >> " + bcolors.ENDC)
	print("...peers searching...")
	port = ra.randint(50010, 60000)
	search = Ricerca(c.selfV4, c.selfV6, port, c.ttl, c.timeResearch, name_search, lock)
	pktid = search.query(c)
	print("\n------| New research launched |------\n")

	for i in tqdm(range(c.timeResearch), desc="\033[94mLoading\033[0m"):
		time.sleep(1)

	print("Research termined\nResult for " + pktid)
	print("[select with the number the file to download]")
	
	res = db.retrieveResponses(pktid)
	
	if(len(res) == 0):
		print("File not found")
		
	else:
		choice_list = []
		i = 1
		for row in res:
			print(str(i) + ") " + "ip: " + row[1] + "  port: " + row[2] + "  md5: " + row[3] + "  file: " + row[4])
			choice_list.append(row)
			i = i + 1

		choice = input(bcolors.OKBLUE + ">> " + bcolors.ENDC)
		
		peer = choice_list[int(choice)-1]
		
		addr = Util.ip_deformatting(peer[1], peer[2], None)
		ip6 = ipad.ip_address(peer[1][16:])

		down = Download(str(addr[0]),str(ip6),peer[2],peer[3],peer[4].rstrip())
		down.download()
		print("\n--- FILE DOWNLOADED ---\n")