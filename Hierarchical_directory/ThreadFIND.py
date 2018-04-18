import socket
import sys
import threading as th
import Util
from Conn import Conn
from dataBase import dataBase


class ThreadFIND(th.Thread):
	def __init__(self, packets, lock):
		th.Thread.__init__(self)
		self.packet = packet
		self.lock = lock

	def run(self):
		superpeers = db.retrieveSuperPeers()

		self.lock.acquire()
		Util.statusRequest[self.packet[4:20]] = True
		self.lock.release()

		for sp in superpeers:
			ipv4, ipv6, port = Util.ip_deformatting(sp[0][:15],sp[0][17:],sp[1])
			conn = Conn(ipv4, ipv6, port)
			conn.connection()
			conn.s.send(self.packet.encode())
			conn.deconnection()

		th.wait(20)

		self.lock.acquire()
		Util.statusRequest[self.packet[4:20]] = False
		self.lock.release()