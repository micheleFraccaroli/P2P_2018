import socket
import threading as th
import Util
import updateBits as uB
from dataBase import dataBase

class t_rpad(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		statusMd5 = []
		num = 0

		recv_packet = self.other_peersocket.recv(56)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 56):
			recv_packet += other_peersocket.recv(56 - self.bytes_read)
			self.bytes_read = len(recv_packet)
		
		flag = True
		check = db.getInterestedPeers(recv_packet[16:48].decode())
		Util.printLog("CHECK → " + str(check))
		for c in check:
			Util.printLog("c → " + str(c[0]))
			if(c[0] == recv_packet[:16].decode()):
				flag = False

		if(flag):
			db.insertInterested(recv_packet[:16].decode(), recv_packet[16:48].decode())
			Util.printLog("INSERITO IN F_IN")
		else:
			Util.printLog("NON INSERITO IN F_IN")
			
		# retrieving part for update
		part_recv = recv_packet[48:].decode()
		part = (int(part_recv)-1)//8
		toUpdateBits = db.retrieveBits(recv_packet[16:48].decode(), recv_packet[:16].decode(), int(part))
		specificBit = int(part_recv) % 8
		if(specificBit == 0):
			specificBit = 8
		
		Util.printLog("part --> " + str(part))
		Util.printLog("toUpdateBits --> " + str(toUpdateBits))
		Util.printLog("specific bit --> " + str(specificBit))

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