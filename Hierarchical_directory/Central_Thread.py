import socket
import os
import threading as th
from Util import Util
from ThreadSUPE import ThreadSUPE
#from ThreadQUER import ThreadQUER
#from Retr import retr
from Recv_Afin import Recv_Afin
from dataBase import dataBase
from ThreadINS import ThreadINS
from ThreadDEL import ThreadDEL
from ThreadLOGO import ThreadLOGO
from Response import thread_Response
from ThreadFIND import ThreadFIND
from Upload import Upload

class Central_Thread(th.Thread):
	def __init__(self, config, port):
		th.Thread.__init__(self)
		self.port = port
		self.ipv4 = config.selfV4
		self.ipv6 = config.selfV6
		self.ttl = config.ttl
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		self.config = db.retrieveAllConfig()
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

				# SUPE ---
				if(recv_type.decode() == "SUPE"):
<<<<<<< HEAD
					if(Util.mode == "super"):
						Util.printLog('Ricevo SUPE da: ' + addrPack)
						recv_packet = other_peersocket.recv(78) # 82 - 4
=======
					Util.printLog('Ricevo SUPE da: '+addrPack)
					recv_packet = other_peersocket.recv(78) # 82 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 78):
						recv_packet += other_peersocket.recv(78 - self.bytes_read)
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1
						self.bytes_read = len(recv_packet)
					Util.printLog("FINITO LETTURA SUPE, AVVIO THREAD SUPE")

<<<<<<< HEAD
						pkt = recv_type+recv_packet
						th_SUPE =  ThreadSUPE(pkt.decode(),self.ipv4,self.ipv6,self.port,addrPack, self.config, Util.mode)
						th_SUPE.start()
=======
					pkt = recv_type+recv_packet
					th_SUPE =  ThreadSUPE(pkt.decode(),self.ipv4,self.ipv6,self.port,addrPack,self.lock,self.config, Util.mode)
					th_SUPE.start()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# ASUP ---
				elif(recv_type.decode() == "ASUP"):
					Util.printLog("Ricevuto ASUP da: " + addrPack)
					recv_packet = other_peersocket.recv(76) # 80 - 4
					self.bytes_read = len(recv_packet)
					while(self.bytes_read < 76):
						recv_packet += other_peersocket.recv(76 - self.bytes_read)
						self.bytes_read = len(recv_packet)

<<<<<<< HEAD
						Util.lock.acquire()
						db.insertSuperPeers(recv_packet[16:71], recv_packet[71:])
						db.insertResponse(recv_packet[:16],recv_packet[16:71], recv_packet[71:],"null","null")
						Util.lock.release()
=======
					self.lock.acquire()
					db.insertSuperPeers(recv_packet[16:71].decode(), recv_packet[71:].decode())
					db.insertResponse(recv_packet[:16].decode(),recv_packet[16:71].decode(), recv_packet[71:].decode(),"null","null")
					self.lock.release()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# QUER ---
				elif(recv_type.decode() == "QUER"):
					Util.printLog('Ricevo QUER da: '+addrPack)
					recv_packet = other_peersocket.recv(98)# 102 - 4

					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 98):
						recv_packet += other_peersocket.recv(98 - self.bytes_read)
						self.bytes_read = len(recv_packet)

<<<<<<< HEAD
						pkt = recv_type+recv_packet
						
						th_QUER = ThreadQUER(self.port,pkt.decode(), addrPack, self.ipv4, self.ipv6, self.config, self.port+10)
						th_QUER.start()
=======
					pkt = recv_type+recv_packet

					th_QUER = ThreadQUER(self.port,pkt.decode(), addrPack, self.ipv4, self.ipv6, self.lock,self.config, self.port+10)
					th_QUER.start()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# AFIN ---
				elif(recv_type.decode() == "AFIN"):
					recv_packet = other_peersocket.recv(3) # numero di md5 ottenuti
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 3):
						recv_packet += other_peersocket.recv(3 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					Util.printLog("RICEVUTO AFIN")
					recv_afin = Recv_Afin(int(recv_packet..decode()), other_peersocket)
					recv_afin.start()

            	# FIND ---
<<<<<<< HEAD
				elif(recv_type.decode() == "FIND"):
					if(Util.mode == "super"):
						recv_packet = other_peersocket.recv(36) # 40 - 4
						self.bytes_read = len(recv_packet)
						while (self.bytes_read < 36):
							recv_packet += other_peersocket.recv(36 - self.bytes_read)
							self.bytes_read = len(recv_packet)
						pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
						addr = ip_formatting(self.ipv4, self.ipv6, self.port)

						new_packet = "QUER" + pktid + addr + self.ttl + recv_packet[16:]
						th_FIND = ThreadFIND(new_packet,recv_packet[4:20])
						th_FIND.start()
=======
            	elif(recv_type.decode() == "FIND"):
        			recv_packet = other_peersocket.recv(36) # 40 - 4
        			self.bytes_read = len(recv_packet)
					while (self.bytes_read < 36):
						recv_packet += other_peersocket.recv(36 - self.bytes_read)
						self.bytes_read = len(recv_packet)
        			pktid = Util.ip_packet16()
        			addr = ip_formatting(self.ipv4, self.ipv6, self.port)

					Util.printLog("RICEVUTO FIND E TRASFORMO IN QUER")
        			new_packet = "QUER" + pktid + addr + self.ttl + recv_packet[16:].decode()
					Util.printLog("====> PACCHETTO DI QUER <====")
					Util.printLog(str(new_packet))
					Util.printLog("=============================")
        			th_FIND = ThreadFIND(new_packet,recv_packet[4:20].decode(),self.lock)
        			th_FIND.start()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# AQUE ---
				elif(recv_type.decode() == "AQUE"):
					recv_packet = other_peersocket.recv(208) # 212 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 208):
						recv_packet += other_peersocket.recv(208 - self.bytes_read)
						self.bytes_read = len(recv_packet)
<<<<<<< HEAD
						while (self.bytes_read < 208):
							recv_packet += other_peersocket.recv(208 - self.bytes_read)
							self.bytes_read = len(recv_packet)

						recv_packet = recv_type + recv_packet
						t_RESP = thread_Response(recv_packet)
						t_RESP.start()
=======
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

					Util.printLog("RICEVO GLI AQUE DALLA RETE")
					recv_packet = recv_type + recv_packet
					t_RESP = thread_Response(recv_packet.decode(), self.lock)
					t_RESP.start()

				# ADFF ---
				elif(recv_type.decode() == "ADFF"):
					recv_packet = other_peersocket.recv(148) # 152 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 148):
						recv_packet += other_peersocket.recv(148 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

<<<<<<< HEAD
						th_INS = ThreadINS(recv_packet)
						th_INS.start()
=======
					Util.printLog("AGGIUNTO FILE AL SUPERPEER")
					th_INS = ThreadINS(recv_packet.decode(), self.lock)
					th_INS.start()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# DEFF ---
				elif(recv_type.decode() == "DEFF"):
					recv_packet = other_peersocket.recv(48) # 52 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 48):
						recv_packet += other_peersocket.recv(48 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

<<<<<<< HEAD
						th_DEL = ThreadDEL(recv_packet)
						th_DEL.start()
=======
					Util.printLog("ELIMINATO FILE AL SUPERPEER")
					th_DEL = ThreadDEL(recv_packet.decode(), self.lock)
					th_DEL.start()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				# LOGI ---
				elif(recv_type.decode() == "LOGI"):
					recv_packet = other_peersocket.recv(60) # 64 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 60):
						recv_packet += other_peersocket.recv(60 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					'''
					Chiama classe che gestisce il login
					'''
					Util.printLog("LOGGATO AL SUPERPEER")

				# LOGO ---
				elif(recv_type.decode() == "LOGO"):
					recv_packet = other_peersocket.recv(3) # 7 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 3):
						recv_packet += other_peersocket.recv(3 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

					Util.printLog("LOGOUT DAL SUPERPEER")
					th_LOGO = ThreadLOGO(recv_packet.decode(), self.lock)
					th_LOGO.start()

				# UPLOAD ---
				elif(recv_type.decode() == "RETR"):
					recv_packet = other_peersocket.recv(32) # 36 - 4
					Util.printLog("RICEVUTA RICHIESTA DI DOWNLOAD DI " + recv_packet.decode() + "DALLA RETE")
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 32):
						recv_packet += other_peersocket.recv(32 - self.bytes_read)
						self.bytes_read = len(recv_packet)

<<<<<<< HEAD
						th_LOGO = ThreadLOGO(recv_packet)
						th_LOGO.start() 
=======
					th_UPLOAD = Upload(self.port, recv_packet.decode(), other_peersocket)
					th_UPLOAD.start()
					th_UPLOAD.join()
>>>>>>> 0d81011ae14cc60bb0f28311e8cf89e3105d43c1

				other_peersocket.close()
