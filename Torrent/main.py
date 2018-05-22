import sys
import Util
import time
import ipaddress as ipad
import random as ra
import threading as th
from Config import Config
from dataBase import *
from tqdm import tqdm
from Conn import Conn
from Add import Add
from RF import RF
from curses import *
from login import login
from logout import logout
from threading import *

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
            'Login to tracker', self.login_to_tracker,
            'Exit', self.exit
        ]

    def login_to_tracker(self):

        db = dataBase()
        config = db.retrieveConfig(('selfV4','selfV6','selfP','trackerV4','trackerV6','trackerP'))
        login_tracker = login(config)
        login_tracker.send_login()
        del db
        time.sleep(1)

    def exit(self):

        print('\nBye\n')
        time.sleep(1)

        exit()

class optionsLogged:

    def __init__(self):

        #self.options = {0:['Search a File', self.search],1:['Add a file to connected supernode', self.add],2:['Remove a file from connected supernode', self.remove],3:['Logout from supernode', self.logout],4:['Exit', self.exit]}
        self.options = [
            'Search a File', self.search,
            'Add a file to tracker', self.add,
            'Logout from tracker', self.logout_from_tracker,
            'Exit', self.exit
        ]

    def search(self):

        db = dataBase()

        config = db.retrieveConfig(('trackerV4','trackerV6','trackerP'))

        del db

        research = input('Insert file name >> ')

        search = RF(config, research)
        search.start()

    def add(self):

        db = dataBase()

        config = db.retrieveConfig(('trackerV4','trackerV6','trackerP'))

        del db

        nameFile = input('Insert name file for add operation >> ')

        add = Add(config, Util.sessionId)

        add.add_file()

    def logout_from_tracker(self):

        db = dataBase()

        config = db.retrieveConfig(('trackerV4','trackerV6','trackerP'))

        logout_tracker = logout(config)

        logout_tracker.send_logout()

    def exit(self):

        print('\nBye\n')
        time.sleep(1)

        exit()

menuMode = {'normal': optionsNormal,'logged': optionsLogged} # Associazione tra modalità di utilizzo e classe associata per il menu

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
Util.mode = 'normal'
print(Util.mode)
code,dbMode = db.create(Util.mode)

if code != 'OK': # C'è ancora una sessione salvata
	print(bcolors.WARNING + '\nWarning: switching from mode \"'+ Util.mode + '\" to mode \"' + dbMode + '\" due previous session.\n' + bcolors.ENDC)
else:
	print(bcolors.OKGREEN + '\nMode accepted\n' + bcolors.ENDC)
	time.sleep(2)

Util.mode = dbMode

c = db.retrieveConfig(('timeResearch',))

print("--- Configurations ---\n")
print('timeResearch: ', c)
print('mode: ',Util.mode)
print("\n----------------------\n")

while True: # Menu principale

	op = menuMode[Util.mode]()

	Util.searchLock.acquire()
	while Util.activeSearch > 0:

		Util.searchLock.release()

		Util.searchIncoming.acquire()
		Util.searchIncoming.wait()
		Util.searchIncoming.release()

		Util.searchLock.acquire()

	Util.searchLock.release()
	Util.menuLock.acquire()
	fun = wrapper(Util.menu,op.options,['Select an option:'])
	Util.menuLock.release()

	if fun != None:
		fun()
