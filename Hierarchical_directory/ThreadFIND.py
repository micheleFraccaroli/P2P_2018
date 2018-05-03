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
		file_find = []
		#ricavo i superpeer a cui sono collegato e inoltro la richiesta nella rete
		superpeers = db.retrieveSuperPeers()
		config = db.retrieveConfig(('selfV4','selfV6'))

		Util.globalLock.acquire()
		Util.statusRequest[self.packet[4:20]] = True
		Util.printLog("DIZIONARIO GLOBALE SETTATO ---> " + str(Util.statusRequest[self.packet[4:20]]))
		Util.globalLock.release()

		if(superpeers):
			for sp in superpeers:

				ipv4, ipv6, port = Util.ip_deformatting(sp[0],sp[1])

				if(ipv4 != config.selfV4):
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
		for f in resp:
			file_find.append(f[3])
		for ff in localFile:
			file_find.append(ff[1])
		
		seen = set()
		uniq = []
		for x in file_find:
			if x not in seen:
			    uniq.append(x)
			    seen.add(x)
		
		toPeer = "AFIN" + str(len(seen)).zfill(3)
		
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
				Util.printLog("PACCHETTO AFIN 1-----> " + str(toPeer))
			elif(count > 1):
				buffer_md5 = md5
				toPeer = md5 + i[4] + str(count)
				for l in ll:
					toPeer = toPeer + l
				connP.s.send(toPeer.encode())
				Util.printLog("PACCHETTO AFIN 2+-----> " + str(toPeer))

		buffer_md5_l = ''
		if(localFile): # se la lista non è vuota entro nel ciclo
			k = 0
			for lf in localFile:
				count = 0
				ll2 = []
				md5 = lf[1]
				Util.printLog("localfile in for " + str(lf))
				addrLocalPeer = db.retrievePeerSid(lf[0])
				
				if(md5 == buffer_md5_l):
					continue
				for j in localFile:
					if(md5 in j):
						addrLocalPeer_dub = db.retrievePeerSid(j[0])
						count = count + 1
						add = addrLocalPeer_dub[0][0] + addrLocalPeer_dub[0][1]
						ll2.append(add)
				Util.printLog("addrLocalPeer " + str(addrLocalPeer))
				if(count == 1):
					toPeer = lf[1] + lf[2] + str(1).zfill(3) + addrLocalPeer[0][0] + addrLocalPeer[0][1]
					k = k + 1
					connP.s.send(toPeer.encode())
					Util.printLog("PACCHETTO AFIN 1 LOCAL-----> " + str(toPeer))
				elif(count > 1):
					buffer_md5_l = md5
					toPeer = lf[1] + lf[2] + str(count).zfill(3)
					for l2 in ll2:
						toPeer = toPeer + l2
					connP.s.send(toPeer.encode())
					Util.printLog("PACCHETTO AFIN 1+ LOCAL-----> " + str(toPeer))

		connP.deconnection()