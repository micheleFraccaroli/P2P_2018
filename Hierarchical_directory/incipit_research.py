import socket
import os
import sys
import Util
from Conn import Conn
import ipaddress as ipad
from dataBase import dataBase

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
			sIpv4, sIpv6, sPort, ttl = Util.ip_deformatting(super_ip[0][0], super_ip[0][1], None)
			#connection to superpeer
			con = Conn(sIpv4, sIpv6, sPort)

		else:
			config = db.retreiveConfig(("selfV4", "selfV6"))
			#connection to superpeer
			con = Conn(config.selfV4, config.selfV6, 3000)

		try:
			con.connection()
			con.s.send(pack.encode())
			con.deconnection()
		except IOError as e:
			print(e)
			sys.exit(0)