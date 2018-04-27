import socket
import sys
import threading as th
import Util
from Conn import Conn
from dataBase import dataBase
from dataBase import dataBaseSuper


class ThreadFIND(th.Thread):
	def __init__(self, packet, sid):
		th.Thread.__init__(self)
		self.packet = packet
		self.sid = sid

	def run(self):
		db = dataBase()

		#ricavo i superpeer a cui sono collegato e inoltro la richiesta nella rete
		superpeers = db.retrieveSuperPeers()

		Util.globalLock.acquire()
		Util.statusRequest[self.packet[4:20]] = True
		Util.printLog("DIZIONARIO GLOBALE SETTATO ---> " + str(Util.statusRequest[self.packet[4:20]]))
		Util.globalLock.release()

		if(superpeers):
			for sp in superpeers:
				ipv4, ipv6, port = Util.ip_deformatting(sp[0][:15],sp[0][16:],sp[1])
				conn = Conn(ipv4, ipv6, port)
				if(conn.connection()):
					conn.s.send(self.packet.encode())
					conn.deconnection()
					Util.printLog("INVIO QUER VERSO " + str(ipv4) + " RIUSCITO")
				else:
					Util.printLog("INVIO QUER FALLITO VERSO IL SUPER... PROBABILMENTE " + str(ipv4) + " E' OFFLINE")
					continue

		cond = th.Condition()
		cond.acquire()
		cond.wait(20)
		cond.release()

		Util.globalLock.acquire()
		Util.statusRequest[self.packet[4:20]] = False
		Util.printLog("PASSATI 20 SECONDI.. DIZIONARIO ---> " + str(Util.statusRequest[self.packet[4:20]]))
		Util.globalLock.release()

		#controllo tra i peer loggati a me prima di inoltrare la quer nella rete
		dbS = dataBaseSuper()
		Util.printLog("CERCATO ----> " + str(self.packet[82:]))
		localFile = dbS.findInLocalSP(self.packet[82:])

		#creazione pacchetto di AFIN passati i 20 secondi
		addrPeer = db.retrievePeerSid(self.sid)
		Util.printLog(str(addrPeer))
		resp = db.retrieveResponse(self.packet[4:20])
		ipv4, ipv6, port, ttl = Util.ip_deformatting(addrPeer[0], addrPeer[1], None)
		toPeer = "AFIN" + str(len(resp)+len(localFile)).zfill(3)
		connP = Conn(ipv4, ipv6, port)
		if(connP.connection()):
			connP.s.send(toPeer.encode())

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
				connP.s.send(toPeer.encode())
			elif(count > 1):
				buffer_md5 = md5
				toPeer = md5 + i[4] + str(count)
				for l in ll:
					toPeer = toPeer + l
				connP.s.send(toPeer.encode())

		if(localFile): # se la lista non è vuota entro nel ciclo
			k = 0
			for lf in localFile:
				research = lf[k][1] + (' '*(100 - len(self.search)))
				config = db.retrieveConfig(("selfV4", "selfV6"))
				toPeer = lf[k][0] + lf[k][1] + str(1).zfill(3) + config.selfV4+"|"+config.selfV6 + '03000'
				k = k + 1
				connP.s.send(toPeer.encode())

		connP.deconnection()