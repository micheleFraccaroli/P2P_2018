import time
import socket
import threading as th
from dataBase import dataBase
import Util
from Conn import Conn

class ThreadSUPE(th.Thread):

	def __init__(self, pack, ipv4, ipv6, ipRequest):

		th.Thread.__init__(self)
		
		self.myIPP     = Util.ip_formatting(ipv4,ipv6,3000) # Porta 3000 visto che devo rispondere da super peer
		info           = Util.ip_deformatting(pack[20:75],pack[75:80],pack[80:])
		self.pack      = pack
		self.pid       = pack[4:20]
		self.ipv4      = info[0]
		self.ipv6      = info[1]
		self.port      = info[2]
		self.ttl       = info[3]
		self.ipRequest = ipRequest

	def run(self):
		Util.printLog('\n\nApertura thread SUPE\n\n')
		db = dataBase()

		Util.lock.acquire()

		res = db.retrieveCounterRequest(self.pid,self.pack[20:75])
		if( res == 0): # Richiesta già conosciuta
			Util.printLog("Eseguo SUPE per: "+self.ipRequest)

			db.insertRequest(self.pid,self.pack[20:75],time.time())

			Util.globalLock.acquire()
			mode = Util.mode # Prelevo la modalità attuale
			Util.globalLock.release()

			if self.ttl > 1: # Inoltro richiesta ai vicini


				if mode == 'update':

					Util.printLog('Update. Prendo vicini da lista')
					neighborhood = Util.listPeers
				
				if mode == 'normal':

					Util.printLog('Invio SUPE da modalità ::: ' + mode)
					neighborhood = db.retrievePeers()
				else:

					
					Util.printLog('Invio SUPE da modalità ::: ' + mode)
					neighborhood = db.retrieveSuperPeers()

				Util.lock.release()

				self.ttl = str(self.ttl-1).zfill(2)
				self.pack=''.join((self.pack[:80],self.ttl))

				for neighbor in neighborhood:

					ipv4, ipv6, port, ttl = Util.ip_deformatting(neighbor[0],neighbor[1],None)

					if ipv4 != self.ipRequest and ipv6 != self.ipRequest and ipv4 != self.ipv4:
						con = Conn(ipv4, ipv6, port)

						if con.connection():

							con.s.send(self.pack.encode())
							Util.printLog("Inoltro SUPE a vicino ::: " + ipv4)
							con.deconnection()
						else:

							Util.printLog("Inoltro SUPE fallita per ::: " + ipv4)
			else:

				Util.lock.release() # Non devo inoltrare, ma devo comunque rilasciare la lock

			if mode in ['update','super']: # Sono superpeer e rispondo

				self.pack = 'ASUP'+self.pid+self.myIPP
				Util.printLog('ASUP pacchetto ::: '+str(self.pack))
				Util.printLog('ASUP verso ::: '+self.ipv4+self.ipv6+str(self.port))

				con = Conn(self.ipv4,self.ipv6,self.port)

				if con.connection():

					con.s.send(self.pack.encode())
					Util.printLog('Risposta ASUP a ::: ' + self.ipv4)
					con.deconnection()
				else:

					Util.printLog('Risposta ASUP fallita per ::: ' + self.ipv4)

		else:
			Util.lock.release()
			Util.printLog("SUPE per: "+self.ipRequest+". Già eseguita")
		Util.printLog('\n\nChiusura thread SUPE\n\n')
