import time
import socket
import threading as th
from dataBase import dataBase
import Util
from Conn import Conn

class ThreadNEAR(th.Thread):

	def __init__(self,pack,ipv4,ipv6,port,ipRequest,lock,config):

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

		db = dataBase()

		if(db.retrivenSearch(self.pid,self.pack[20:75]) == 0): # Richiesta già conosciuta
			Util.printLog("Eseguo NEAR per: "+self.ipRequest)
			self.lock.acquire()
			db.insertRequest(self.pid,self.pack[20:75],time.time())
			self.lock.release()
			if self.ttl > 1: # Inoltro richiesta ai vicini

				self.ttl = str(self.ttl-1).zfill(2)
				self.pack=''.join((self.pack[:80],self.ttl))

				neighborhood = db.retrieveNeighborhood(self.config)

				for neighbor in neighborhood:

					params = Util.ip_deformatting(neighbor[0],neighbor[1],None)
					
					if params[0] != self.ipRequest and params[1] != self.ipRequest and params[0] != self.ipv4:
						self.con = Conn(params[0],params[1],params[2])
						try:
							self.con.connection()
							self.con.s.send(self.pack.encode())
							self.con.deconnection()
							Util.printLog("vicino inoltro NEAR: "+params[0])
						except IOError as e:
							print("Inoltro vicino fallito")
							
							
			self.pack = 'ANEA'+self.pid+self.myIPP
			Util.printLog('ANEA a: '+str(self.pack))
			Util.printLog('ANEA CONN: '+self.ipv4+self.ipv6+str(self.port))
			self.con = Conn(self.ipv4,self.ipv6,self.port)
			#print('Con ANEA ', self.ipv4, self.ipv6, self.port)
			try:
				self.con.connection()
				self.con.s.send(self.pack.encode())
				self.con.deconnection()
			except IOError as e:
				print("Risposta diretta fallita")
				
		else:
			Util.printLog("NEAR per: "+self.ipRequest+". Già eseguita")