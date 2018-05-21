import socket
import sys
import Util
import threading as th
from dataBase import dataBase
from plot_net import plot_net
from matplotlib.pyplot import pause

class t_login(th.Thread):
	def  __init__(self,other_peersocket, packet):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.packet = packet

	def run(self):
		db = dataBase()
		sid = Util.ip_packet16() # generazione sid
		'''
		recv_packet = self.other_peersocket.recv(60)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 60):
			recv_packet += other_peersocket.recv(60 - self.bytes_read)
			self.bytes_read = len(recv_packet)
		'''

		packet = "ALGI" + str(sid)

		self.other_peersocket.send(packet.encode())

		ip = self.packet[:55]
		port = self.packet[55:]

		db.login(ip, port, sid)

		self.other_peersocket.close()