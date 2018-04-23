import socket
import sys
import threading as th
from dataBase import dataBase
from Util import Util
from Conn import Conn

class ThreadALGI(th.Thread):
	def __init__(self, ip, port):
		th.Thread.__init__(self)
		self.ip = ip
		self.port = port

	def run(self):
		db = dataBaseSuper()

		found = db.retriveLOGINwithIP(self.ip,self.port)
		if(found):
			Util.printLog("UTENTE GIA' TROVATO NEL DB... LOGIN FALLITO")
			print("User already logged! Login failed!")
			
			packet = "ALGI" + '0000000000000000'
			
			conn = Conn(self.ip[:15], self.ip[16:], self.port)
			conn.connection()
			conn.s.send(packet.encode())
			conn.deconnection()
			sys.exit()
		else:
			try:
				self.sid = Util.ip_packet16() #generation SessionID
				#signup on db new user
				db.insertID(self.ip, self.port, sid)

				#generation ALGI packet
				packet = "ALGI" + str(sid)

				conn = Conn(self.ip[:15], self.ip[16:], self.port)
				conn.connection()
				conn.s.send(packet.encode())
				conn.deconnection()
			except:
				packet = "ALGI" + '0000000000000000'
				conn = Conn(self.ip[:15], self.ip[16:], self.port)
				conn.connection()
				conn.s.send(packet.encode())
				conn.deconnection()
				sys.exit()