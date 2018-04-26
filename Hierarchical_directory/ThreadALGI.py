import socket
import sys
import threading as th
from dataBase import *
from Util import Util
from Conn import Conn

class ThreadALGI(th.Thread):
	def __init__(self, ip, port):
		th.Thread.__init__(self)
		self.ip = ip
		self.port = port

	def run(self):
		db = dataBaseSuper()

		found = db.retrieveLOGINwithIP(self.ip,self.port)
		if(found):
			Util.printLog("UTENTE GIA' TROVATO NEL DB... REINVIO IL SESSION ID")
			print("User already logged! Login failed!")
			
			packet = "ALGI" + found[2]

			ipv4,ipv6,port,ttl = Util.ip_deformatting(self.ip, self.port, None)
			
			conn = Conn(ipv4,ipv6,port)
			conn.connection()
			conn.s.send(packet.encode())
			conn.deconnection()
			sys.exit()
		else:
			try:
				self.sid = Util.ip_packet16() #generation SessionID
				#signup on db new user
				db.insertID(self.ip, self.port, self.sid)

				#generation ALGI packet
				packet = "ALGI" + str(sid)

				ipv4,ipv6,port,ttl = Util.ip_deformatting(self.ip, self.port, None)

				conn = Conn(ipv4,ipv6,port)
				conn.connection()
				conn.s.send(packet.encode())
				conn.deconnection()
			except:
				packet = "ALGI" + '0000000000000000'
				ipv4,ipv6,port,ttl = Util.ip_deformatting(self.ip, self.port, None)

				conn = Conn(ipv4,ipv6,port)
				conn.connection()
				conn.s.send(packet.encode())
				conn.deconnection()
				sys.exit()