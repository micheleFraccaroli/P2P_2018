import socket
import os
import Util
import threading as th
from  ThreadNEAR import ThreadNEAR
from ThreadQUER import ThreadQUER

class Central_Thread(th.Thread):
	def __init__(self, config, lock):
		th.Thread.__init__(self)
		self.port = config.selfP
		self.ipv4 = config.selfV4
		self.ipv6 = config.selfV6
		self.bytes_read = 0
		self.lock = lock
		self.config = config

	def run(self):
		peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		peersocket.bind(('', self.port))

		peersocket.listen(20)

		while True:
			Util.printLog("IN ATTESA DI UNA RICHISTA")

			other_peersocket, addr = peersocket.accept()
			if addr[0][:2] == "::":
				addrPack = addr[0][7:]
				Util.printLog("Richiesta in arrivo da: "+addrPack)
			else:
				addrPack=addr[0]
				Util.printLog("Richiesta in arrivo da: "+addrPack)

			recv_type = other_peersocket.recv(4)
			Util.printLog(str(recv_type))
			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					Util.printLog(str(self.bytes_read))
					recv_type += other_peersocket.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)

				# NEAR ------
				if(recv_type.decode() == "NEAR"):
					Util.printLog('Ricevo NEAR da: '+addrPack)
					recv_packet = other_peersocket.recv(78) # 82 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 78):
						recv_packet += other_peersocket.recv(78 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					Util.printLog("FINITO LETTURA NEAR, AVVIO THREAD NEAR")
					# lancio il thread per l'ascolto delle richieste di near
					pkt = recv_type+recv_packet
					th_NEAR =  ThreadNEAR(pkt.decode(),self.ipv4,self.ipv6,self.port,addrPack,self.lock,self.config)
					th_NEAR.start()

				# QUER ------
				elif(recv_type.decode() == "QUER"):
					Util.printLog('Ricevo QUER da: '+addrPack)
					recv_packet = other_peersocket.recv(98)# 102 - 4

					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 98):
						recv_packet += other_peersocket.recv(98 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					#Util.printLog("FINITO LETTURA QUER, AVVIO THREAD QUER")
					# lancio il thread per l'ascolto delle richieste di contenuti
					pkt = recv_type+recv_packet
					
					th_QUER = ThreadQUER(self.port,pkt.decode(), addrPack, self.ipv4, self.ipv6, self.lock,self.config, self.port+10)
					th_QUER.start()
				other_peersocket.close()