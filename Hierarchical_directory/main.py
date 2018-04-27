import sys
import Util
import time
import ipaddress as ipad
import random as ra
import threading as th
from Config import Config
from dataBase import *
from tqdm import tqdm
from Download import Download
from Central_Thread import Central_Thread
from Conn import Conn
from Add_Remove import *
from incipit_research import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class optionsNormal:

	def __init__(self):
		
		self.options = {1:['Login to supernode', self.login],2:['Exit', self.exit]}

	def login(self):

		Util.updatePeers()

		db = dataBase()

		Util.lock.acquire()

		config = db.retrieveConfig(('selfV4','selfV6','selfP'))
		ip = Util.ip_formatting(config.selfV4, config.selfV6, config.selfP)

		listPeers = db.retrieveSuperPeers()
		Util.printLog('Nella lock')
		Util.lock.release()

		ipv4, ipv6, port, ttl = Util.ip_deformatting(listPeers[0][0],listPeers[0][1],None)
		con = Conn(ipv4, ipv6, port)

		if con.connection():
		
			packet = 'LOGI' + ip
			Util.printLog('Richiesta LOGI a vicino ::: ' + ipv4)
			con.s.send(packet.encode())
			con.deconnection()

		else:

			Util.printLog('Richiesta LOGI fallita per ::: ' + ipv4)
	
		time.sleep(1)

	def exit(self):

		db = dataBase()
		
		Util.lock.acquire()
		
		config = db.retrieveConfig(('selfV4','selfV6','selfP'))

		db.destroy()
		Util.lock.release()

		con = Conn(config.selfV4, config.selfV6, config.selfP)
		con.connection()
		con.s.send('EXIT'.encode())
		con.deconnection()
		
		
		print('\nBye\n')
		time.sleep(1)

		exit()

class optionsLogged:

	def __init__(self):

		self.options = {1:['Search a File', self.search],2:['Add a file to connected supernode', self.add],3:['Remove a file from connected supernode', self.remove],4:['Logout from supernode', self.logout],5:['Exit', self.exit]}

	def search(self):

		research = input('>> ')

		search = incipit_research(research)
		search.research()

		waitMenu.acquire()
		waitMenu.wait()
		waitMenu.release()

	def add(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port, ttl = Util.ip_deformatting(listPeers[0][0],listPeers[0][1],None)

		nameFile = input('Insert name file for add operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.aggiunta(nameFile)

		print('Added file ' + nameFile + 'to directory')

		time.sleep(1)

	def remove(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port, ttl = Util.ip_deformatting(listPeers[0][0],listPeers[0][1],None)

		nameFile = input('Insert name file for remove operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.rimuovi('./share/' + nameFile)

		print('Removed file ' + nameFile + 'from directory')

		time.sleep(1)

	def logout(self):

		db = dataBase()

		Util.lock.acquire()

		listPeers = db.retrieveSuperPeers()
		Util.printLog(listPeers[0][0])
		Util.printLog(listPeers[0][1])
		dirV4, dirV6, dirP , ttl = Util.ip_deformatting(listPeers[0][0],listPeers[0][1],None)

		Util.lock.release()

		packet = 'LOGO' + Util.sessionId

		con = Conn(dirV4, dirV6, dirP)

		if con.connection():
		
			Util.printLog('Richiesta LOGO a vicino ::: ' + dirV4)
			con.s.send(packet.encode())
			con.deconnection()

			Util.loggedOut.acquire()
			Util.loggedOut.wait()
			Util.loggedOut.release()

		else:

			Util.printLog('Richiesta LOGO fallita per ::: ' + dirV4)

	def exit(self):

		print("### Logout implicito da implementare ###")

		db = dataBase()
		
		Util.lock.acquire()
		
		config = db.retrieveConfig(('selfV4','selfV6','selfP'))

		con = Conn(config.selfV4, config.selfV6, config.selfP)
		con.connection()
		con.s.send('EXIT'.encode())
		con.deconnection()
		
		db.destroy()
		Util.lock.release()

		print('\nBye\n')
		time.sleep(1)

		exit()

class optionsSuper:

	def __init__(self):

		self.options = {1:['Update peers', Util.updatePeers],2:['Search a File', self.search],3:['Add a file to connected supernode', self.add],4:['Remove a file from connected supernode', self.remove],5:['Exit', self.exit]}

	def update(self):

		print('UPDATE')
		time.sleep(1)

	def search(self):

		print('SEARCH')
		time.sleep(1)

	def add(self):

		print('ADD')
		time.sleep(1)

	def remove(self):

		print('REMOVE')
		time.sleep(1)

	def exit(self):

		db = dataBaseSuper()
		
		if db.existsLogged() > 0:

			print(bcolors.FAIL + '\nUnable to exit. There are peers still connected to you.\n' + bcolors.ENDC)
			time.sleep(4)

		else:
			Util.lock.acquire()
		
			config = db.retrieveConfig(('selfV4','selfV6','selfP'))
			
			db.destroy()
			Util.lock.release()

			con = Conn(config.selfV4, config.selfV6, config.selfP)
			con.connection()
			con.s.send('EXIT'.encode())
			con.deconnection()

			con = Conn(config.selfV4, config.selfV6, 3000)
			con.connection()
			con.s.send('EXIT'.encode())
			con.deconnection()
			
		
			print('\nBye\n')
			time.sleep(1)

			exit()

if len(sys.argv) > 2:
	
	print(bcolors.WARNING + 'Syntax: python3 main.py [super]' + bcolors.ENDC)
	exit()

elif len(sys.argv) == 2:

	if sys.argv[1] != 'super':

		print(bcolors.FAIL + 'Argument \"' + sys.argv[1] + '\" undefined' + 'bcolors.ENDC')
		exit()

	else:
		Util.mode = 'super'

else:
	Util.mode = 'normal'

menuMode = {'normal': optionsNormal,'super': optionsSuper,'logged': optionsLogged}

Util.initializeFiles() # Inizializzo i file di log ed errors

print(bcolors.MAGENTA + "____________________________      ________   ______   " + bcolors.ENDC)
print(bcolors.MAGENTA + "\______   \_____  \______   \    /  _____/  /  __  \  " + bcolors.ENDC)
print(bcolors.OKBLUE  + " |     ___//  ____/|     ___/   /   \  ___  >      <  " + bcolors.ENDC)
print(bcolors.OKBLUE  + " |    |   /       \|    |       \    \_\  \/   --   \ " + bcolors.ENDC)
print(bcolors.CYAN    + " |____|   \_______ \____|        \______  /\______  / " + bcolors.ENDC)
print(bcolors.CYAN    + "                  \/                    \/        \/  " + bcolors.ENDC)

time.sleep(2)

db = dataBase()
code,dbMode = db.create(Util.mode)

if code != 'OK':
	print(bcolors.WARNING + '\nWarning: switching from mode \"'+ Util.mode + '\" to mode \"' + dbMode + '\" due previous session.\n' + bcolors.ENDC)
else:
	print(bcolors.OKGREEN + '\nMode accepted\n' + bcolors.ENDC)
	time.sleep(2)

Util.mode = dbMode

c = db.retrieveConfig(('maxNear', 'timeResearch', 'timeIdPacket'))
config = db.retrieveConfig(('selfV4', 'selfV6', 'ttl', 'selfP'))

print("--- Configurations ---\n")
print('ttl: ',config.ttl)
print('maxNear: ',c.maxNear)
print('timeResearch: ',c.timeResearch)
print('timeIdPacket: ',c.timeIdPacket)
print('mode: ',Util.mode)
print("\n----------------------\n")

# background thread for requests
if Util.mode == 'super':
	
	central_threadS = Central_Thread(config,3000)
	central_threadS.start()

central_threadN = Central_Thread(config,config.selfP)
central_threadN.start()

while True:

	op = menuMode[Util.mode]()

	print('Select an option:\n\n')
	i=1
	for option in op.options:
		print('['+str(i)+'] '+op.options[option][0]+'\n')
		i+=1
	try:
		s = int(input(bcolors.OKBLUE + ">> " + bcolors.ENDC))
	except ValueError:
		print('\nInput error...\n')
		time.sleep(2)
	else:
		if s > 0 and s <= len(op.options):
			op.options[s][1]()
		else:
			print('\nInput error...\n')
			time.sleep(2)

	'''
	name_search = input('Select an option:\n\n[1]Login\n[2]Search peers\n[3]Search a file\n[]')
	
	name_search = input(bcolors.OKBLUE + "Search >> " + bcolors.ENDC)
	print("...peers searching...")
	search = Ricerca(c.selfV4, c.selfV6, c.selfP, c.ttl, c.timeResearch, name_search, lock)
	pktid = search.query(c)
	print("\n------| New research launched |------\n")

	for i in tqdm(range(c.timeResearch), desc="\033[94mLoading\033[0m"):
		time.sleep(1)

	print("Research terminateded\nResult for " + pktid)
	print("[select the file to download using numbers]")
	
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
	'''