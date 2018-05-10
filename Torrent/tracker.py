import socket
import sys
import os
import threading as th
from t_login import t_login

class tracker:
	def __init__(self):
		# 
		# some parameters
		#
	def body(self):
		peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		peersocket.bind(('', 3000))

		peersocket.listen(20)

		while True:
			Util.printLog("###### IN ATTESA DI UNA RICHIESTA #######")

			other_peersocket, addr = peersocket.accept()

			if addr[0][:2] == "::":
				addrPack = addr[0][7:]
				Util.printLog("Richiesta in arrivo da: "+addrPack)
			else:
				addrPack=addr[0]
				Util.printLog("Richiesta in arrivo da: "+addrPack)

			recv_type = other_peersocket.recv(4)

			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					recv_type += other_peersocket.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)

				# LOGIN ---
				if(recv_type.decode() == "LOGI"):
					th_LOGIN = t_login(other_peersocket)
					th_LOGIN.start()

				