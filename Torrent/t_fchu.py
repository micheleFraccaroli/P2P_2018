import socket
import threading as th
import math
import partList_gen as pL
import codecs
from dataBase import dataBase

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
		hitpeer = db.getHitpeer(recv_packet[16:].decode())
		interested_sid = db.getInterestedPeers(recv_packet[16:].decode())
		for isid in interested_sid:
			peer = db.getPeerBySid(isid[0])
			addr = peer[0] + peer[1]
			interested_peer[isid] = addr

		# insert into db all 0 
		infoFile = db.retrieveInfoFile(recv_packet[16:].decode())
		totalBit = math.ceil((infoFile[0] / infoFile[1]))
		bits = pL.partList_gen(totalBit, 0)
		db.insertBitmapping(recv_packet[16:].decode(), recv_packet[:16].decode(), bits)

		packet_resp = "AFCH" + str(hitpeer).zfill(3)
		self.other_peersocket.s.send(packet_resp.encode())

		for sid in interested_peer.keys():
			resp_list.append(interested_peer[sid])
			self.other_peersocket.s.send(packet_resp.encode())

			bits = db.getBitmapping(sid, recv_packet[16:].decode())
			for b in bits:
				self.other_peersocket.s.send(codecs.encode(chr(b[0],'iso-8859-1')))

		self.other_peersocket.close()