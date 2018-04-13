import socket
import os
from Util import Util
import threading as th
from  ThreadSUPE import ThreadSUPE
from ThreadQUER import ThreadQUER
from Retr import retr
from Recv_Afin import Recv_Afin
from dataBase import dataBase

'''
mode = 0 ----> peer
mode = 1 ----> superpeer
'''

class Central_Thread(th.Thread):
	def __init__(self, config, lock, mode):
		th.Thread.__init__(self)
		self.port = config.selfP
		self.ipv4 = config.selfV4
		self.ipv6 = config.selfV6
		self.ttl = config.ttl
		self.bytes_read = 0
		self.lock = lock
		self.config = config
		self.mode = mode

	def run(self):
		db = dataBase()
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

				# SUPE ------
				if(recv_type.decode() == "SUPE"):
					if(self.mode == 1):
						Util.printLog('Ricevo SUPE da: '+addrPack)
						recv_packet = other_peersocket.recv(78) # 82 - 4
						self.bytes_read = len(recv_packet)
						while (self.bytes_read < 78):
							recv_packet += other_peersocket.recv(78 - self.bytes_read)
							self.bytes_read = len(recv_packet)
						Util.printLog("FINITO LETTURA SUPE, AVVIO THREAD SUPE")

						pkt = recv_type+recv_packet
						th_SUPE =  ThreadSUPE(pkt.decode(),self.ipv4,self.ipv6,self.port,addrPack,self.lock,self.config, self.mode)
						th_SUPE.start()

				# ASUP ------
				elif(recv_type.decode() == "ASUP"):
					if(self.mode == 1):
						Util.printLog("Ricevuto ASUP da: " + addrPack)
						recv_packet = other_peersocket.recv(76) # 80 - 4
						self.bytes_read = len(recv_packet)
						while(self.bytes_read < 76):
							recv_packet += other_peersocket.recv(76 - self.bytes_read)
							self.bytes_read = len(recv_packet)

						self.lock.acquire()
						db.insertSuperPeers(recv_packet[16:71], recv_packet[71:])
						db.insertResponse(recv_packet[:16],recv_packet[16:71], recv_packet[71:],"null","null")
						self.lock.release()

				# QUER ------
				elif(recv_type.decode() == "QUER"):
					if(self.mode == 1):
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

				# AFIN ---
				elif(recv_type.decode() == "AFIN"):
					if(self.mode == 0):
						numMd5 = int(other_peersocket.recv(3)) # numero di md5 ottenuti
						recv_afin = Recv_Afin(numMd5, other_peersocket)
						recv_afin.start()
						

            	# FIND ---
            	elif(recv_type.decode() == "FIND"):
            		if(self.mode == 1):
            			recv_packet = other_peersocket.recv(36) # 40 - 4
            			pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
            			addr = ip_formatting(self.ipv4, self.ipv6, self.port)

            			new_packet = "QUER" + pktid + addr + self.ttl + recv_packet[16:]

            			pkt = recv_type + new_packet

            			th_QUER = ThreadQUER(self.port, pkt.decode(), addrPack, self.ipv4, self.ipv6, self.lock, self.config, self.port+10)
            			th_QUER.start()

        				retr = Retr(self.port, self.config, self.lock)
        				retr.start()

				other_peersocket.close()