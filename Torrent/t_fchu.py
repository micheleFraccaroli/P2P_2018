import socket
import threading as th
import math

class t_fchu(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		id_list = []
		ip_part_dict = {}

		recv_packet = self.other_peersocket.recv(48)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 48):
			recv_packet += other_peersocket.recv(48 - self.bytes_read)
			self.bytes_read = len(recv_packet)

		hitpeer,id_list = db.getIDf_in(recv_packet[16:].decode())

		ip_part_dict = db.getInterestedPartList(id_list)

		packet_resp = "AFCH" + str(hitpeer).zfill(3)

		for k in ip_part_dict.keys():
			packet_resp = packet_resp + str(k) + str(ip_part_dict[k])

		self.other_peersocket.s.send(packet_resp.encode())
		self.other_peersocket.close()