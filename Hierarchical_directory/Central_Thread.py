import sys
import socket
import os
import threading as th
from Util import Util
from pathlib import Path
from ThreadSUPE import ThreadSUPE
from ThreadQUER import ThreadQUER
from Recv_Afin import Recv_Afin
from dataBase import dataBase
from dataBase import dataBaseSuper
from ThreadINS import ThreadINS
from ThreadDEL import ThreadDEL
from ThreadLOGO import ThreadLOGO
from Response import thread_Response
from ThreadFIND import ThreadFIND
from Upload import Upload
from ThreadALGI import ThreadALGI
import toPlotNetwork

class Central_Thread(th.Thread):
	def __init__(self, config, port):
		th.Thread.__init__(self)
		self.port = int(port)
		self.ipv4 = config.selfV4
		self.ipv6 = config.selfV6
		self.ttl = config.ttl
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		dbs = dataBaseSuper()
		self.config = db.retrieveAllConfig()
		peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		peersocket.bind(('', self.port))

		peersocket.listen(20)

		while True:
			Util.printLog("IN ATTESA DI UNA RICHIESTA ")

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

				# SUPE ---
				if(recv_type.decode() == "SUPE"):

					Util.printLog('Ricevo SUPE da: '+addrPack)
					recv_packet = other_peersocket.recv(78) # 82 - 4
					self.bytes_read = len(recv_packet)

					while (self.bytes_read < 78):

						recv_packet += other_peersocket.recv(78 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					Util.printLog("FINITO LETTURA SUPE, AVVIO THREAD SUPE")

					pkt = recv_type+recv_packet
					th_SUPE =  ThreadSUPE(pkt.decode(),self.ipv4,self.ipv6,addrPack)
					th_SUPE.start()

				# ASUP ---
				elif(recv_type.decode() == "ASUP"):
					Util.printLog("Ricevuto ASUP da: " + addrPack)
					recv_packet = other_peersocket.recv(76) # 80 - 4
					self.bytes_read = len(recv_packet)
					while(self.bytes_read < 76):
						recv_packet += other_peersocket.recv(76 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					Util.lock.acquire()
					db.insertSuperPeers(recv_packet[16:71].decode(), recv_packet[71:].decode())
					db.insertResponse(recv_packet[:16].decode(),recv_packet[16:71].decode(), recv_packet[71:].decode(),"null","null")
					Util.lock.release()

				# QUER ---
				elif(recv_type.decode() == "QUER"):
					Util.printLog('Ricevo QUER da: '+addrPack)
					recv_packet = other_peersocket.recv(98)# 102 - 4

					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 98):
						Util.printLog(str(self.bytes_read))
						recv_packet += other_peersocket.recv(98 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					Util.printLog("NUMERO LETTO : " + str(len(recv_packet)))
					pkt = recv_type+recv_packet
					Util.printLog("QUER RICEVUTO: " + pkt.decode())
					th_QUER = ThreadQUER(pkt.decode(),addrPack)
					th_QUER.start()

				# AFIN ---
				elif(recv_type.decode() == "AFIN"):
					recv_packet = other_peersocket.recv(3) # numero di md5 ottenuti
					self.bytes_read = len(recv_packet)
					Util.printLog("RICEVUTO AFIN")
					while (self.bytes_read < 3):
						recv_packet += other_peersocket.recv(3 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					recv_afin = Recv_Afin(int(recv_packet.decode()), other_peersocket)
					recv_afin.start()

				# FIND ---
				elif(recv_type.decode() == "FIND"):
					recv_packet = other_peersocket.recv(36) # 40 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 36):
						recv_packet += other_peersocket.recv(36 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					pktid = Util.ip_packet16()
					addr = Util.ip_formatting(self.ipv4, self.ipv6, self.port)

					Util.printLog("RICEVUTO FIND E TRASFORMO IN QUER " + str(recv_packet[16:].decode()))
					new_packet = "QUER" + pktid + addr + str(self.ttl).zfill(2) + recv_packet[16:].decode().ljust(20)
					Util.printLog("====> PACCHETTO DI QUER <====")
					Util.printLog(str(new_packet))
					Util.printLog("=============================")
					th_FIND = ThreadFIND(new_packet,recv_packet[:16].decode())
					th_FIND.start()

				# AQUE ---
				elif(recv_type.decode() == "AQUE"):
					recv_packet = other_peersocket.recv(208) # 212 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 208):
						recv_packet += other_peersocket.recv(208 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					Util.printLog("RICEVO GLI AQUE DALLA RETE")
					recv_packet = recv_type + recv_packet
					t_RESP = thread_Response(recv_packet.decode())
					t_RESP.start()

				# ADFF ---
				elif(recv_type.decode() == "ADFF"):
					recv_packet = other_peersocket.recv(148) # 152 - 4
					self.bytes_read = len(recv_packet)
					Util.printLog("LUNGHEZZA LETTURA AGG FILE " + str(self.bytes_read))
					while (self.bytes_read < 148):
						Util.printLog("I'M HERE")
						recv_packet += other_peersocket.recv(148 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

					Util.printLog("AGGIUNTO FILE AL SUPERPEER")
					th_INS = ThreadINS(recv_packet.decode())
					th_INS.start()

				# DEFF ---
				elif(recv_type.decode() == "DEFF"):
					recv_packet = other_peersocket.recv(48) # 52 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 48):
						recv_packet += other_peersocket.recv(48 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

					Util.printLog("ELIMINATO FILE AL SUPERPEER")
					th_DEL = ThreadDEL(recv_packet.decode())
					th_DEL.start()

				# LOGI ---
				elif(recv_type.decode() == "LOGI"):
					recv_packet = other_peersocket.recv(60) # 64 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 60):
						recv_packet += other_peersocket.recv(60 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					th_ALGI = ThreadALGI(recv_packet[:55].decode(),recv_packet[55:].decode(), other_peersocket)
					th_ALGI.ALGI()

					Util.printLog("FINE LOGIN NEL CENTRAL THREAD")

				# LOGO ---
				elif(recv_type.decode() == "LOGO"):
					recv_packet = other_peersocket.recv(16) # 20 - 4
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 16):
						recv_packet += other_peersocket.recv(16 - self.bytes_read)
						self.bytes_read = len(recv_packet)
					recv_packet = recv_type + recv_packet

					Util.printLog("LOGOUT DAL SUPERPEER")
					th_LOGO = ThreadLOGO(recv_packet.decode(), other_peersocket)
					th_LOGO.LOGO()

				# UPLOAD ---
				elif(recv_type.decode() == "RETR"):
					recv_packet = other_peersocket.recv(32) # 36 - 4
					Util.printLog("RICEVUTA RICHIESTA DI DOWNLOAD DI " + recv_packet.decode() + " DALLA RETE")
					self.bytes_read = len(recv_packet)
					while (self.bytes_read < 32):
						Util.printLog("DENTRO AL CICLO DEL RETR")
						recv_packet += other_peersocket.recv(32 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					th_UPLOAD = Upload(self.port, recv_packet.decode(), other_peersocket)
					th_UPLOAD.start()
					th_UPLOAD.join()

				# EXIT ---
				elif(recv_type.decode() == "EXIT"):
					sys.exit()

			if(recv_type.decode() not in ['AFIN','FIND']):
				other_peersocket.close()
