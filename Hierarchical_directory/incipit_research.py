import socket
import os
import sys
import Util
from Conn import Conn
import ipaddress as ipad
from dataBase import dataBase
from Recv_Afin import Recv_Afin

class incipit_research:
	def __init__(self, search):
		self.sid = Util.sessionId
		self.search = search

	def research(self):
		db = dataBase()
		#generating packet
		search_extended = self.search + (' '*(20 - len(self.search)))
		pack = "FIND" + self.sid + search_extended

		#retreive address of superpeer
		if(Util.mode in ["normal","logged"]):
			super_ip = db.retrieveSuperPeers()
			sIpv4, sIpv6, sPort = Util.ip_deformatting(super_ip[0][0], super_ip[0][1])
			#connection to superpeer
			con = Conn(sIpv4, sIpv6, sPort)

		else:
			config = db.retrieveConfig(("selfV4", "selfV6"))
			#connection to superpeer
			con = Conn(config.selfV4, config.selfV6, 3000)
		
		if con.connection():

			Util.printLog('Incipit corretto')
			con.s.send(pack.encode())
			

			recv_type = con.s.recv(4)
			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					recv_type += con.s.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)

			if(recv_type.decode() == "AFIN"):
				recv_packet = con.s.recv(3) # numero di md5 ottenuti
				self.bytes_read = len(recv_packet)
				Util.printLog("RICEVUTO AFIN")
				while (self.bytes_read < 3):
					recv_packet += con.s.recv(3 - self.bytes_read)
					self.bytes_read = len(recv_packet)

				recv_afin = Recv_Afin(int(recv_packet.decode()), con.s)
				recv_afin.start()		
		else:
			Util.printLog('Incipit fallito')
