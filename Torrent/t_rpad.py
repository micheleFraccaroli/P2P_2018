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
		
		for c in check:
			if(c[0] == recv_packet[:16].decode()):
				flag = False

		lenFile = db.retrieveInfoFile(recv_packet[16:48].decode())
		if(flag):
			db.insertInterested(recv_packet[:16].decode(), recv_packet[16:48].decode())
			db.insert_file(recv_packet[:16].decode(), recv_packet[16:48].decode(), lenFile[3], lenFile[1], lenFile[2])
			
		# retrieving part for update
		part_recv = recv_packet[48:].decode()
		part = (int(part_recv))//8
		#toUpdateBits = db.retrieveBits(recv_packet[16:48].decode(), recv_packet[:16].decode(), int(part))

		Util.lockD.acquire()
		toUpdateBits = Util.globalDict[recv_packet[:48].decode()][part]

		specificBit = (int(part_recv)) % 8
		#if(specificBit == 0 and int(part_recv) != 0):
		#	specificBit = 8
		
		Util.count_dict += 1

		up = uB.updateBits(toUpdateBits, specificBit)

		Util.globalDict[recv_packet[:48].decode()][part] = up
		Util.globalDictStatus[recv_packet[:48].decode()] += 1

		Util.lockD.release()

		packet = "APAD" + str(Util.globalDictStatus[recv_packet[:48].decode()]).zfill(8)
		Util.printLog(str(packet))
		self.other_peersocket.send(packet.encode())
		self.other_peersocket.close()

		if(Util.count_dict < 500):
			up = uB.updateBits(toUpdateBits, specificBit)
		
			#lenFile = db.retrieveInfoFile(recv_packet[16:48].decode())
			Util.printLog("DIZIONARIO DICT STATUS ----------------------------> " + str(Util.globalDictStatus))
			Util.printLog("LENFILE -----------------------------------> " + str(lenFile))

			if lenFile[0] == Util.globalDictStatus[recv_packet[:48].decode()]: # File scaricato

				Util.globalDictStatus.pop(recv_packet[:48].decode(), None)

				t_RIFLE = rifleDict(Util.globalDict.copy(), recv_packet[:48].decode(), True)
				t_RIFLE.start()

		else:
			Util.count_dict = 0
			t_RIFLE = rifleDict(Util.globalDict.copy(), recv_packet[:48].decode(), False)
			t_RIFLE.start()