import socket
import sys
import threading as th
import Util
from Conn import Conn
from dataBase import dataBase


class ThreadFIND(th.Thread):
	def __init__(self, packets, sid, lock):
		th.Thread.__init__(self)
		self.packet = packet
		self.lock = lock
		self.sid = sid

	def run(self):
		db = dataBase()
		superpeers = db.retrieveSuperPeers()

		Util.globalLock.acquire()
		Util.statusRequest[self.packet[4:20]] = True
		Util.printLog("DIZIONARIO GLOBALE SETTATO ---> " + str(Util.statusRequest[self.packet[4:20]]))
		self.globalLock.release()

		for sp in superpeers:
			ipv4, ipv6, port = Util.ip_deformatting(sp[0][:15],sp[0][17:],sp[1])
			conn = Conn(ipv4, ipv6, port)
			if(!conn.connection()):
				Util.printLog("INVIO QUER FALLITO VERSO IL SUPER... PROBABILMENTE " + str(ipv4) + " E' OFFLINE")
				continue
			conn.s.send(self.packet.encode())
			conn.deconnection()
			Util.printLog("INVIO QUER VERSO " + str(ipv4) + " RIUSCITO")

		th.wait(20)

		self.globalLock.acquire()
		Util.statusRequest[self.packet[4:20]] = False
		Util.printLog("PASSATI 20 SECONDI.. DIZIONARIO ---> " + str(Util.statusRequest[self.packet[4:20]]))
		self.globalLock.release()

		addrPeer = db.retrievePeerSid(self.sid)
		resp = db.retrieveResponse(self.packet[4:20])
		ipv4, ipv6, port = Util.ip_deformatting(addrPeer[0][:15], addrPeer[0][:17], addrPeer[1])
		toPeer = "AFIN" + str(len(resp)).zfill(3)
		connP = Conn(ipv4, ipv6, port)
		if(!connP.connection()):
			sys.exit(1)
		connP.s.send(toPeer.encode())

		#creazione pacchetto di AFIN
		buffer_md5 = ''
		for i in resp:
			count = 0
			ll = []
			md5 = i[3]
			if(md5 == buffer_md5):
				continue
			for j in resp:
				if(md5 in j):
					count = count + 1
					add = j[1] + j[2]
					ll.append(add)
			if(count == 1):
				toPeer = md5 + i[4] + str(count).zfill(3) + i[1] + i[2]
				connP.connection()
				connP.s.send(toPeer.encode())
			elif(count > 1):
				buffer_md5 = md5
				toPeer = md5 + i[4] + str(count)
				for l in ll:
					toPeer = toPeer + l
				connP.connection()
				connP.s.send(toPeer.encode())
		
		connP.deconnection()