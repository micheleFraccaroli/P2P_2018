import socket
import threading as th
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
		num = 0

		recv_packet = self.other_peersocket.recv(56)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 56):
			recv_packet += other_peersocket.recv(56 - self.bytes_read)
			self.bytes_read = len(recv_packet)
		
		# retrieving part for update
		part_recv = recv_packet[48:].decode()
		part = int(part_recv)//8
		toUpdateBits = db.retrieveBits(recv_packet[16:48].decode(), recv_packet[:16].decode(), int(part))
		specificBit = int(part_recv) % 8

		#print("part --> " + str(part))
		#print("toUpdateBits --> " + str(toUpdateBits))
		#print("specific bit --> " + str(specificBit))

		up = uB.updateBits(toUpdateBits, specificBit)
		
		# updating database
		db.updatePart(part, recv_packet[16:48].decode(), recv_packet[:16].decode(), up)

		# return status of md5 for peer
		statusMd5 = db.getBitmapping(recv_packet[:16].decode(), recv_packet[16:48].decode())
		
		for sM in statusMd5:
			num = num + bin(sM[0])[2:].count('1')
		
		packet = "APAD" + str(num).zfill(8)
		self.other_peersocket.send(packet.encode())

		self.other_peersocket.close()