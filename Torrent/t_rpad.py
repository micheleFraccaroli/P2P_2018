import socket
import threadinig as th
import Util
import updateBits as uB
from dataBase import dataBase

class t_rpad(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes:read = 0

	def run(self):
		db = dataBase()
		statusMd5 = []

		recv_packet = self.other_peersocket.recv(56)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 56):
			recv_packet += other_peersocket.recv(56 - self.bytes_read)
			self.bytes_read = len(recv_packet)
		
		# retrieving part for update
		part = recv_packet[48:].decode()
		toUpdateBits = db.retrieveBits(recv_packet[16:32].decode(), recv_packet[:16].decode(), part)
		specificBit = part % 8

		uB.updateBits(toUpdateBits, specificBit)

		# return status of md5 for peer
		statusMd5 = db.getBitmapping(recv_packet[:16].decode(), recv_packet[16:32].decode())

		for sM in statusMd5:
			num = num + bin(sM[1])[2:].count('1')
		
		packet = "APAD" + str(num).zfill(8)
		self.other_peersocket.s.send(packet.encode())

		self.other_peersocket.close()