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

		NEARlock = th.Lock()

		while True:
			other_peersocket, addr = peersocket.accept()
			if addr[0][:2] == "::":
				addrPack = addr[0][7:]
				print("\n\nEcco l'IP: ",addrPack,"\n\n")
			else:
				addrPack=addr[0]
				print("\n\nEcco l'IP: ",addr[0],"\n\n")
			recv_type = other_peersocket.recv(4)

			self.bytes_read = len(recv_type)
			while (self.bytes_read < 4):
				recv_type += other_peersocket.recv(4 - self.bytes_read)
				self.bytes_read = len(recv_type)

			# NEAR ------
			if(recv_type.decode() == "NEAR"):
				print('NEAR')
				recv_packet = other_peersocket.recv(78) # 82 - 4
				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 78):
					recv_packet += other_peersocket.recv(78 - self.bytes_read)
					self.bytes_read = len(recv_packet)
				print('\nFINITO LETTURA NEAR, AVVIO THREAD NEAR\n')
				# lancio il thread per l'ascolto delle richieste di near
				pkt = recv_type+recv_packet
				th_NEAR =  ThreadNEAR(pkt.decode(),self.ipv4,self.ipv6,self.port,addrPack,NEARlock)
				th_NEAR.start()

			# QUER ------
			elif(recv_type.decode() == "QUER"):
				print('QUER')
				recv_packet = other_peersocket.recv(98)# 102 - 4

				self.bytes_read = len(recv_packet)
				while (self.bytes_read < 98):
					recv_packet += other_peersocket.recv(98 - self.bytes_read)
					self.bytes_read = len(recv_packet)

				print('\nFINITO LETTURA QUER, AVVIO THREAD QUER\n')
				# lancio il thread per l'ascolto delle richieste di contenuti
				pkt = recv_type+recv_packet
				
				th_QUER = ThreadQUER(self.port,pkt.decode(), addrPack, self.ipv4, self.ipv6)
				th_QUER.start()