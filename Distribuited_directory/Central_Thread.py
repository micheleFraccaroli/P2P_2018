import socket
import os
import threading as th
from  ThreadNEAR import ThreadNEAR
from ThreadQUER import ThreadQUER

class Central_Thread(th.Thread):
	def __init__(self, config):
		th.Thread.__init__(self)
		self.port = config.selfP
		self.ipv4 = config.selfV4
		self.ipv6 = config.selfV6
		self.bytes_read = 0

	def run(self):
		peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		peersocket.bind(('', self.port))

		peersocket.listen(20)

		while True:
			print('\nIN ATTESA...\n')
			other_peersocket, addr = peersocket.accept()
			recv_type = other_peersocket.recv(4).decode()

			self.bytes_read = len(recv_type)
			while (self.bytes_read < 4):
				recv_type += other_peersocket.recv(4 - self.bytes_read).decode()
				self.bytes_read = len(recv_type)

				# NEAR ------
			if(recv_type == "NEAR"):
				recv_packet = other_peersocket.recv(78).decode() # 82 - 4
				print("\nRICHIESTA NEAR\n")
				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 78):
					recv_packet += other_peersocket.recv(78 - self.bytes_read).decode()
					self.bytes_read = len(recv_packet)
					print(self.bytes_read)
				print('\nAPRO IL THREAD\n')
				# lancio il thread per l'ascolto delle richieste di near
				th_NEAR =  ThreadNEAR(recv_type+recv_packet,self.ipv4,self.ipv6,self.port,addr[0])
				th_NEAR.start()

			# QUER ------
			elif(recv_type == "QUER"):
				recv_packet = other_peersocket.recv(98).decode() # 102 - 4
				print("\nRICHIESTA QUER\n")
				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 98):
					recv_packet += other_peersocket.recv(98 - self.bytes_read).decode()
					self.bytes_read = len(recv_packet)

				# lancio il thread per l'ascolto delle richieste di contenuti
				pkt = recv_type+recv_packet
				
				th_QUER = ThreadQUER(self.port,pkt, addr[0])
				th_QUER.start()