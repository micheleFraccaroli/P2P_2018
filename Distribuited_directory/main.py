import Util
import time
import random as ra
from Config import Config
from Vicini import Vicini
from Ricerca import Ricerca
from Retr import Retr
from dataBase import dataBase
from tqdm import tqdm
from Download import Download
from Central_Thread import Central_Thread

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
print("\n\n")

#for i in tqdm(range(4), desc="Loading: "):
time.sleep(2)
c=Config() #istanza delle configurazioni
db = dataBase()
#db.create(c)
#del db

print("\n--- Configurations ---\n")
print('ttl: ',c.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
print("\n------------------------\n")
#near=Vicini(c)

while True:
    # background thread
    central_thread = Central_Thread(c)
    central_thread.start()

    name_search = input("Insert file to search into net: ")
    port = ra.randint(50000, 59999)
    search = Ricerca(c.selfV4, c.selfV6, port, c.ttl, c.timeResearch, name_search)
    pktid = search.query(c)
    print("\nNew research launched |------\n")

    for i in tqdm(range(35), desc="\033[94mLoading\033[0m"):
        time.sleep(1)

    print("Research termined\nResult for " + pktid + " |------")
    print("[select with the number the file to download")
    res = db.retrieveResponses(pktid)
    choice_list = []
    i = 1
    for row in res:
        print(i + ") " + "ip: " + row[1] + "  port: " + row[2] + "  md5: " + row[3] + "  file: " + row[4])
        choice_list.append(row)
        i = i + 1

    choice = input("\033[1;35m> \033[0m")
    peer = choice_list[choice-1]
    ipv4,ipv6 = peer[1].split('|')
    download = Download(ipv4,ipv6,peer[2],peer[2],peer[4])
    download.download()

del db