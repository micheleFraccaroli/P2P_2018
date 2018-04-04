import socket
import threading as th
from dataBase import dataBase
import Util
from Conn import Conn

class ThreadNEAR(th.Thread):

	def __init__(self,pack,ipv4,ipv6,port,ipRequest):

		th.Thread.__init__(self)
		self.myIPP     = Util.ip_formatting(ipv4,ipv6,port)
		info           = Util.ip_deformatting(pack[20:75],pack[75:80],pack[80:])
		self.pack      = pack
		self.pid       = pack[4:20]
		self.ipv4      = info[0]
		self.ipv6      = info[1]
		self.port      = info[2]
		self.ttl       = info[3]
		self.ipRequest = str(ipRequest)

	def run(self):

		db = dataBase()

		if self.ttl > 0: # Inoltro richiesta ai vicini

			self.ttl = str(self.ttl-1).zfill(2)
			self.pack=''.join((self.pack[:80],self.ttl))

			neighborhood = db.retrieveNeighborhood()

			for neighbor in neighborhood:

				params = Util.ip_deformatting(neighbor[0],neighbor[1],None)
				
				if params[0] != self.ipRequest and params[1] != self.ipRequest:
					self.con = Conn(params[0],params[1],params[2])
					try:
						self.con.connection()
						self.con.s.send(self.pack.encode())
						self.con.deconnection()
					except IOError as e:
						print(e)
						exit()

		self.pack = 'ANEA'+self.pid+self.myIPP
		self.con = Conn(self.ipv4,self.ipv6,self.port)
		try:
			self.con.connection()
			self.con.s.send(self.pack.encode())
			self.con.deconnection()
		except IOError as e:
			print('Connection error. '+e)
			exit()