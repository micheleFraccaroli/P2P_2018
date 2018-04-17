import socket
import os
import sys
import Util
import Conn
import ipaddress as ipad
from dataBase import dataBase

class incipit_research:
	def __init__(self, sid, search):
		self.sid = sid
		self.search = search

	def research(self, config):
		#generating packet
		search_extended = self.search + (' '*(20 - len(self.search)))
		pack = "FIND" + self.sid + search_extended

		#retreive address of superpeer
		db = dataBase()
		super_ip, super_port = db.retrieveNeighborhood(config)
		addr = ip_deformatting(super_ip, super_port, None)

		sIpv4 = addr[0]
		sIpv6 = str(ipad.ip_address(super_ip[16:]))
		sPort = addr[2]

		#connection to superpeer
		con = Conn(sIpv4, sIpv6, sPort)

		try:
			con.connection()
			con.send(pack.encode())
			con.deconnection()
		except IOError as e:
			print(e)
			sys.exit(0)