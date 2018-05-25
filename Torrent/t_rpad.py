import socket
import threading as th
import Util
import updateBits as uB
import time
from dataBase import dataBase
from rifleDict import rifleDict

class t_rpad(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes_read = 0

	def run(self):
		db = dataBase()
		statusMd5 = []
		#num = 0

		recv_packet = self.other_peersocket.recv(56)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 56):
			recv_packet += other_peersocket.recv(56 - self.bytes_read)
			self.bytes_read = len(recv_packet)
		
		flag = True
		check = db.getInterestedPeers(recv_packet[16:48].decode())
		#Util.printLog("CHECK → " + str(check))
		for c in check:
			#Util.printLog("c → " + str(c[0]))
			if(c[0] == recv_packet[:16].decode()):
				flag = False

		if(flag):
			db.insertInterested(recv_packet[:16].decode(), recv_packet[16:48].decode())
			#Util.printLog("INSERITO IN F_IN")
		#else:
			#Util.printLog("NON INSERITO IN F_IN")
			
		# retrieving part for update
		part_recv = recv_packet[48:].decode()
		part = (int(part_recv)-1)//8
		#toUpdateBits = db.retrieveBits(recv_packet[16:48].decode(), recv_packet[:16].decode(), int(part))

		toUpdateBits = Util.globalDict[recv_packet[:48].decode()][part]

		specificBit = int(part_recv) % 8
		if(specificBit == 0):
			specificBit = 8
		
		#Util.printLog("part --> " + str(part))
		#Util.printLog("toUpdateBits --> " + str(toUpdateBits))
		#Util.printLog("specific bit --> " + str(specificBit))
		Util.count_dict += 1
		'''
		for i in Util.globalDict.keys():
			for j in Util.globalDict[i].keys():
				Util.count_dict += bin(Util.globalDict[i][j]).count('1')
		'''
		if(Util.count_dict <= 500):
			up = uB.updateBits(toUpdateBits, specificBit)
			
			# updating database
			Util.globalDict[recv_packet[:48].decode()][part] = up
			#ind = list(Util.globalDict.keys()).index(recv_packet[:48].decode())
			Util.globalDictStatus[recv_packet[:48].decode()] += 1
			# return status of md5 for peer
			#statusMd5 = db.getBitmapping(recv_packet[:16].decode(), recv_packet[16:48].decode())
			
			#for sM in statusMd5:
			#	num = num + bin(sM[0])[2:].count('1')
			
			#packet = "APAD" + str(num).zfill(8)
			packet = "APAD" + str(Util.count_dict).zfill(8)
			Util.printLog("CICLO N: " + str(Util.globalDictStatus[recv_packet[:48].decode()]))
			Util.printLog("→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→ INVIO APAD ←")
			self.other_peersocket.send(packet.encode())

			self.other_peersocket.close()
		
			lenFile = db.retrieveInfoFile(recv_packet[16:48].decode())

			if lenFile[1] == Util.globalDictStatus[recv_packet[:48].decode()]: # File scaricato

				Util.globalDictStatus.pop(recv_packet[:48].decode(), None)

				t_RIFLE = rifleDict()
				t_RIFLE.start()

		else:
			Util.count_dict = 0
			t_RIFLE = rifleDict()
			t_RIFLE.start()