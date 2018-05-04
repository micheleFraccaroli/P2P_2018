import socket
import sys
import threading as th
from dataBase import *
from Util import Util
from Conn import Conn

class ThreadALGI():
	def __init__(self, ip, port, other_peersocket):
		self.ip = ip
		self.port = port
		self.other_peersocket = other_peersocket

	def ALGI(self):
		db = dataBaseSuper()

		found = db.retrieveLOGINwithIP(self.ip,self.port)
		if(found):
			Util.printLog("UTENTE GIA' TROVATO NEL DB... REINVIO IL SESSION ID")
			
			packet = "ALGI" + found[2]

			self.other_peersocket.send(packet.encode())
			Util.printLog("PACCHETTO ALGI REINVIATO "+str(packet))
			#ipv4,ipv6,port = Util.ip_deformatting(self.ip, self.port)

		else:
			try:
				self.sid = Util.ip_packet16() #generation SessionID
				#signup on db new user
				db.insertID(self.ip, self.port, self.sid)

				#generation ALGI packet
				packet = "ALGI" + str(self.sid)
				
				self.other_peersocket.send(packet.encode())

				Util.printLog("PACCHETTO ALGI "+str(packet))
				#ipv4,ipv6,port = Util.ip_deformatting(self.ip, self.port)
			
			except:
				packet = "ALGI" + '0000000000000000'
				#ipv4,ipv6,port = Util.ip_deformatting(self.ip, self.port)
				self.other_peersocket.send(packet.encode())