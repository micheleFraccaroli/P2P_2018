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

				ipv4, ipv6, port = Util.ip_deformatting(sp[0],sp[1])

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
		localFile = dbS.findInLocalSP(self.packet[82:])
		Util.printLog("LOCALFILE " + str(localFile))
		#creazione pacchetto di AFIN passati i 20 secondi
		addrPeer = db.retrievePeerSid(self.sid)
		Util.printLog("ADDRPEER " + str(addrPeer))
		resp = db.retrieveResponse(self.packet[4:20])
		ipv4, ipv6, port = Util.ip_deformatting(addrPeer[0][0], addrPeer[0][1])
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
				Util.printLog("localfile in for " + str(lf))
				addrLocalPeer = db.retrievePeerSid(lf[0])
				Util.printLog("addrLocalPeer " + str(addrLocalPeer))
				toPeer = lf[1] + lf[2] + str(1).zfill(3) + addrLocalPeer[0][0] + addrLocalPeer[0][1]
				k = k + 1
				connP.s.send(toPeer.encode())

		connP.deconnection()