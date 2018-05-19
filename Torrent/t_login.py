import socket
import sys
import Util
import threading as th
from dataBase import dataBase

class t_login(th.Thread):
	def  __init__(self,other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		sid = Util.ip_packet16() # generazione sid

		recv_packet = self.other_peersocket.recv(60)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 60):
			recv_packet += other_peersocket.recv(60 - self.bytes_read)
			self.bytes_read = len(recv_packet)

		packet = "ALGI" + str(sid)

		self.other_peersocket.send(packet.encode())

		ip = recv_packet[:55].decode()
		port = recv_packet[55:].decode()

		db.login(ip, port, sid)

		self.other_peersocket.close()