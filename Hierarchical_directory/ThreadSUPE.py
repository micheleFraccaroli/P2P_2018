import time
import socket
import threading as th
from dataBase import dataBase
import Util
from Conn import Conn

class ThreadSUPE(th.Thread):

	def __init__(self, pack, ipv4, ipv6, port, ipRequest, lock, config):

		th.Thread.__init__(self)
		self.myIPP     = Util.ip_formatting(ipv4,ipv6,port)
		info           = Util.ip_deformatting(pack[20:75],pack[75:80],pack[80:])
		self.pack      = pack
		self.pid       = pack[4:20]
		self.ipv4      = info[0]
		self.ipv6      = info[1]
		self.port      = info[2]
		self.ttl       = info[3]
		self.ipRequest = ipRequest
		self.lock      = lock
		self.config    = config

	def run(self):
		Util.printLog('\n\nApertura thread SUPE\n\n')
		db = dataBase()

		self.lock.acquire()

		res = db.retrieveCounterRequest(self.pid,self.pack[20:75])
		if( res == 0): # Richiesta già conosciuta
			Util.printLog("Eseguo SUPE per: "+self.ipRequest)
			
			db.insertRequest(self.pid,self.pack[20:75],time.time())
			
			if self.ttl > 1: # Inoltro richiesta ai vicini

				neighborhood = db.retrieveSuperPeers(self.config.maxNear) # Dati sulla tabella anche se c'è un aggiornamento in corso
				
				mode = Util.mode # Prelevo la modalità attuale

				self.lock.release()

				self.ttl = str(self.ttl-1).zfill(2)
				self.pack=''.join((self.pack[:80],self.ttl))

				for neighbor in neighborhood:

					params = Util.ip_deformatting(neighbor[0],neighbor[1],None)
					
					if params[0] != self.ipRequest and params[1] != self.ipRequest and params[0] != self.ipv4:
						self.con = Conn(params[0],params[1],params[2])
						try:
							self.con.connection()
							self.con.s.send(self.pack.encode())
							self.con.deconnection()
							Util.printLog("vicino inoltro SUPE: "+params[0])
						except IOError as e:
							print("Inoltro vicino fallito")
			else:

				self.lock.release() # Non devo inoltrare, ma devo comunque rilasciare la lock
							
			self.pack = 'ASUP'+self.pid+self.myIPP
			Util.printLog('ASUP ::: '+str(self.pack))
			Util.printLog('ASUP CONN ::: '+self.ipv4+self.ipv6+str(self.port))
			self.con = Conn(self.ipv4,self.ipv6,self.port)
			#print('Con ASUP ', self.ipv4, self.ipv6, self.port)
			try:
				self.con.connection()
				self.con.s.send(self.pack.encode())
				self.con.deconnection()
			except IOError as e:
				print("Risposta diretta fallita")
				
		else:
			self.lock.release()
			Util.printLog("SUPE per: "+self.ipRequest+". Già eseguita")
		Util.printLog('\n\nChiusura thread SUPE\n\n')