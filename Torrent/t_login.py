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

		ip = self.packet[:55]
		port = self.packet[55:]
		
		sid = db.login(ip, port)

		packet = "ALGI" + str(sid)
		self.other_peersocket.send(packet.encode())
		self.other_peersocket.close()