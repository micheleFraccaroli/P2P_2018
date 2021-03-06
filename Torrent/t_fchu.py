import socket
import threading as th
import math
import partList_gen as pL
import Util
from dataBase import dataBase
from plot_net import plot_net

class t_fchu(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		interested_sid = []
		resp_list = []
		interested_peer = {}
		ip_part_dict = {}

		recv_packet = self.other_peersocket.recv(48)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 48):
			recv_packet += other_peersocket.recv(48 - self.bytes_read)
			self.bytes_read = len(recv_packet)

		# retrieving from database
		hitpeer = db.getHitpeer(recv_packet[16:].decode(), recv_packet[:16].decode())
		#Util.printLog("\n→ HITPEER " + str(hitpeer))
		interested_sid = db.getInterestedPeers(recv_packet[16:].decode())
		#Util.printLog("\n→ INTERESTED SID " + str(interested_sid))
		
		for isid in interested_sid:
			#Util.printLog("ISID → " + str(isid[0]))
			peer = db.getPeerBySid(isid[0])
			addr = peer[0] + peer[1]
			interested_peer[isid[0]] = addr

		# insert into db all 0 
		infoFile = db.retrieveInfoFile(recv_packet[16:].decode())
		
		#print(infoFile)
		bits = pL.partList_gen(infoFile[0], 0)
		db.insertBitmapping(recv_packet[16:].decode(), recv_packet[:16].decode(), bits)

		packet_resp = "AFCH" + str(hitpeer).zfill(3)
		self.other_peersocket.send(packet_resp.encode())
		#Util.printLog("fchun → " + str(interested_peer))
		for sid in interested_peer.keys():
			if(sid != recv_packet[:16].decode()):
				resp_list.append(interested_peer[sid])
				#Util.printLog("interessato inviato ---> " + str(interested_peer[sid]))

				bits = db.getBitmapping(sid, recv_packet[16:].decode())
				if(bits):
					self.other_peersocket.send(interested_peer[sid].encode())
					#Util.printLog("bit dell'interessato ---> " + str(bits))
				for b in bits:
					#Util.printLog(bytes([b[0]]))
					self.other_peersocket.send(bytes([b[0]]))

		if(not recv_packet.decode() in Util.globalDict.keys()):
			# se non c'è creo il dizionario d'appoggio per bufferizzare l'rpad
			Util.globalDict[recv_packet.decode()] = {}
			for i in range(math.ceil(infoFile[0]/8)):
				Util.globalDict[recv_packet.decode()][i] = 0
			
		self.other_peersocket.close()