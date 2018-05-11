import socket
import threadinig as th
import Util
from dataBase import dataBase

class t_rpad(th.Thread):
	def __init__(self, other_peersocket):
		th.Thread.__init__(self)
		self.other_peersocket = other_peersocket
		self.bytes:read = 0

	def run(self):
		db = dataBase()

		recv_packet = self.other_peersocket.recv(56)
		self.bytes_read = len(recv_packet)
		while(self.bytes_read < 56):
			recv_packet += other_peersocket.recv(56 - self.bytes_read)
			self.bytes_read = len(recv_packet)

		if(recv_packet[16:32].decode() in Util.globalDict[recv_packet[:16].decode()]):
			#
			# Call update metod
			#
		else:
			# Call insert medot
			peer = db.getPeerBySid(recv_packet[:16].decode())
			db.insertInterested(recv_packet[:16].decode(), peer[0], peer[1])
			db.insertBitmapping()