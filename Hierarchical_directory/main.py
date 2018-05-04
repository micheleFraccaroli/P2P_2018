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
from curses import *

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

		#self.options = {0:['Login to supernode', self.login],1:['Exit', self.exit]}
		self.options = [
							'Login to supernode', self.login,
							'Exit', self.exit
					   ]

	def login(self, flag = None):

		db = dataBase()

		Util.lock.acquire()

		config = db.retrieveConfig(('selfV4','selfV6','selfP'))
		ip = Util.ip_formatting(config.selfV4, config.selfV6, config.selfP)
		Util.lock.release()

		if flag == None:
			
			Util.updatePeers()

		else: # Io sono super peer, quindi uso me stesso
			db.insertSuperPeers(ip[:55],'03000')

		Util.lock.acquire()
		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		Util.lock.release()

		con = Conn(ipv4, ipv6, port)

		if con.connection():

			packet = 'LOGI' + ip
			Util.printLog('Richiesta LOGI a vicino ::: ' + ipv4)
			con.s.send(packet.encode())

			#####################################################
			recv_type = con.s.recv(4)
			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					recv_type += con.s.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)

			if(recv_type.decode() == "ALGI"):
				recv_packet = con.s.recv(16)
				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 16):
					recv_packet += con.s.recv(16 - self.bytes_read)
					self.bytes_read = len(recv_packet)

				Util.printLog('ALGI pre lock')
				Util.globalLock.acquire()
				Util.sessionId = recv_packet.decode()
				if Util.mode != 'super':
					Util.mode = 'logged'
				Util.globalLock.release()
				Util.printLog('ALGI post lock')

				if Util.mode != 'super':
					Util.lock.acquire()
					db.updateConfig('mode','logged')
					db.updateConfig('sessionId',Util.sessionId)
					Util.lock.release()
			#####################################################

			con.deconnection()

		else:

			Util.printLog('Richiesta LOGI fallita per ::: ' + ipv4)

		if(flag == None):
			Util.mode = 'logged'
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

		#self.options = {0:['Search a File', self.search],1:['Add a file to connected supernode', self.add],2:['Remove a file from connected supernode', self.remove],3:['Logout from supernode', self.logout],4:['Exit', self.exit]}
		self.options = [
							'Search a File', self.search,
							'Add a file to connected supernode', self.add,
							'Remove a file from connected supernode', self.remove,
							'Show network status', Util.statusNetwork,
							'Logout from supernode', self.logout,
							'Exit', self.exit
					   ]
	def search(self):

		research = input('Insert file name >> ')

		search = incipit_research(research)
		search.research()

		Util.waitMenu.acquire()
		Util.waitMenu.wait()
		Util.waitMenu.release()

	def add(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		nameFile = input('Insert name file for add operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.aggiunta(nameFile)

		print('Added file ' + nameFile + 'to directory')

		time.sleep(1)

	def remove(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		nameFile = input('Insert name file for remove operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.rimuovi('share/' + nameFile)

		print('Removed file ' + nameFile + 'from directory')

		time.sleep(1)

	def logout(self):

		file = open('File_System.txt','w')
		file.close()

		db = dataBase()

		Util.lock.acquire()

		listPeers = db.retrieveSuperPeers()
		Util.printLog(listPeers[0][0])
		Util.printLog(listPeers[0][1])
		dirV4, dirV6, dirP = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		Util.lock.release()

		packet = 'LOGO' + Util.sessionId

		con = Conn(dirV4, dirV6, dirP)

		if con.connection():

			Util.printLog('Richiesta LOGO a vicino ::: ' + dirV4)
			con.s.send(packet.encode())

			#################################################
			recv_type = con.s.recv(4)
			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					recv_type += con.s.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)

			if(recv_type.decode() == "ALGO"):
				recv_packet = con.s.recv(3) # 7 - 4
				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 3):
					recv_packet += con.s.recv(3 - self.bytes_read)
					self.bytes_read = len(recv_packet)
				recv_packet = recv_type + recv_packet

				Util.printLog("LOGOUT da te stesso")
				Util.printLog('Logout done. Eliminated ' + recv_packet.decode() + ' from directory')

				Util.lock.acquire()
				db.updateConfig('mode','normal')
				Util.lock.release()
				Util.printLog('mode normal?')
				Util.loggedOut.acquire()
				Util.loggedOut.notify()
				Util.loggedOut.release()

			#################################################

			con.deconnection()

			# Attendo una risposta al logout
			Util.loggedOut.acquire()
			Util.loggedOut.wait()
			Util.loggedOut.release()

			# Ripristino la modalità a 'normal'
			Util.globalLock.acquire()
			Util.mode = 'normal'
			Util.globalLock.release()

		else:

			Util.printLog('Richiesta LOGO fallita per ::: ' + dirV4)

	def exit(self):

		self.logout()

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

		self.options = {0:['Update peers', Util.updatePeers],1:['Search a File', self.search],2:['Add a file to connected supernode', self.add],3:['Remove a file from connected supernode', self.remove],4:['Exit', self.exit]}
		self.options = [
							'Update peers', Util.updatePeers,
							'Search a File', self.search,
							'Add a file to connected supernode', self.add,
							'Remove a file from connected supernode', self.remove,
							'Show network status', Util.statusNetwork,
							'Exit', self.exit
					   ]
	def search(self):

		research = input('Insert file name >> ')

		search = incipit_research(research)
		search.research()

		Util.waitMenu.acquire()
		Util.waitMenu.wait()
		Util.waitMenu.release()

	def add(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		nameFile = input('Insert name file for add operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.aggiunta(nameFile)

		print('Added file ' + nameFile + 'to directory')

		time.sleep(1)

	def remove(self):

		db = dataBase()

		listPeers = db.retrieveSuperPeers()

		ipv4, ipv6, port = Util.ip_deformatting(listPeers[0][0],listPeers[0][1])

		nameFile = input('Insert name file for remove operation: ')

		addf = AddRm(ipv4, ipv6, port, Util.sessionId)

		addf.rimuovi('share/' + nameFile)

		print('Removed file ' + nameFile + 'from directory')

		time.sleep(1)

	def exit(self):

		db = dataBaseSuper()

		if db.existsLogged() > 1:

			print(bcolors.FAIL + '\nUnable to exit. There are peers still connected to you.\n' + bcolors.ENDC)
			time.sleep(4)

		else:

			op = optionsLogged()
			op.logout()
			
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

menuMode = {'normal': optionsNormal,'super': optionsSuper,'logged': optionsLogged} # Associazione tra modalità di utilizzo e classe associata per il menu

Util.initializeFiles() # Inizializzo i file di log ed errors

print(bcolors.MAGENTA + "____________________________      ________   ______   " + bcolors.ENDC)
print(bcolors.MAGENTA + "\______   \_____  \______   \    /  _____/  /  __  \  " + bcolors.ENDC)
print(bcolors.OKBLUE  + " |     ___//  ____/|     ___/   /   \  ___  >      <  " + bcolors.ENDC)
print(bcolors.OKBLUE  + " |    |   /       \|    |       \    \_\  \/   --   \ " + bcolors.ENDC)
print(bcolors.CYAN    + " |____|   \_______ \____|        \______  /\______  / " + bcolors.ENDC)
print(bcolors.CYAN    + "                  \/                    \/        \/  " + bcolors.ENDC)

time.sleep(2)

# Cerco di creare il database

db = dataBase()
code,dbMode = db.create(Util.mode)

if code != 'OK': # C'è ancora una sessione salvata
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
central_threadN = Central_Thread(config,config.selfP)
central_threadN.start()
if Util.mode == 'super':

	central_threadS = Central_Thread(config,3000)
	central_threadS.start()

	op = optionsNormal()
	op.login(True) # Valore non importante, basta sia diverso da None


while True: # Menu principale

	op = menuMode[Util.mode]()

	fun = wrapper(Util.menu,op.options,['Select an option:'])
	fun()
