import socket
from pathlib import Path
import glob
import Util
import time
import datetime
import re
import sys
import os
import ipaddress as ipad
import hashlib
from dataBase import dataBase
from dataBase import dataBaseSuper
from Conn import Conn
from Vicini import Vicini
from Config import Config
import threading as th
import random as ra
from File_system import File_system

#inizializzo il thread

class ThreadQUER(th.Thread):
	def __init__(self, quer_pkt, ip_request):
		th.Thread.__init__(self)
		self.from_peer = quer_pkt
		self.ip_request = ip_request

	#risponde al superpeer che ha effettuato una ricerca

	def answer(self, db, file_list, pktid, ip, portB):
		addr = Util.ip_deformatting(ip, portB)
		ip6 = ipad.ip_address(ip[16:])
		self.con = Conn(addr[0], str(ip6), addr[2])

		if(self.con.connection()):
			for file in file_list:
				peer_info = db.retrieveLOGIN(file[0])
				answer = "AQUE"+pktid+peer_info[0]+peer_info[1]+file[1]+file[2]
				self.con.s.send(answer.encode())
				Util.printLog(answer)
			self.con.deconnection()
		else:
			Util.printLog("[AQUE] Errore invio risposta al peer "+addr[0])

	#ricerca dei vicini

	def search_neighbors(self, db, ip_request, new_quer):
		self.neighbors = db.retrieveSuperPeers() #mi tiro giù i vicini super
		for n in self.neighbors:
			addr = Util.ip_deformatting(n[0], n[1])
			ip6 = ipad.ip_address(n[0][16:])
			self.con = Conn(addr[0], str(ip6), addr[2])

			if((addr[0] != ip_request) and (str(ip6) != ip_request) and (new_quer[20:35] != addr[0])):
				if(self.con.connection()):
					self.con.s.send(new_quer.encode())
					Util.printLog(new_quer)
					self.con.deconnection()
				else:
					Util.printLog("[QUER] Errore inoltro al superpeer "+addr[0])

	#vado a calcolare il nuovo ttl

	def new_ttl(self, ttl):
		new_ttl = ttl - 1
		if(new_ttl>9):
			c = str(new_ttl)
		else:
			c = str(new_ttl).rjust(2, '0')
		return c

	#funzione principale

	def do(self, db, pktid, ip, timestamp, lock, string, peer_port, ttl, last_part_pkt, ip_request):

		lock.acquire()
		file_found = db.searchFILEquer(string)
		lock.release()
		if(file_found):
			#rispondo
			self.answer(db, file_found, pktid, ip, peer_port)
		if(ttl>1):
			Util.printLog("[QUER]: eseguo l'inoltro ai vicini della richiesta")
			#vado a decrementare il ttl di uno e costruisco la nuova query da inviare ai vicini
			self.ttl_new = self.new_ttl(ttl)
			self.new_quer = "QUER"+pktid+ip+peer_port+self.ttl_new+last_part_pkt
			lock.acquire()
			self.search_neighbors(db, ip_request, self.new_quer)
			lock.release()
		del db

	def run(self):

		self.pktid = self.from_peer[4:20]
		self.ip  = self.from_peer[20:75]
		self.peer_port = self.from_peer[75:80]
		self.ttl = int(self.from_peer[80:82])
		self.string = self.from_peer[82:].rstrip()

		db = dataBaseSuper()
		Util.lock.acquire()
		res = db.retrieveCounterRequest(self.pktid, self.ip)

		if(res == 0):
			self.timestamp = time.time()
			db.insertRequest(self.pktid, self.ip, self.timestamp)
			Util.lock.release()
			self.do(db, self.pktid, self.ip, self.timestamp, Util.lock, self.string, self.peer_port, self.ttl, self.from_peer[82:], self.ip_request)
		else:
			before = db.retrieveRequestTimestamp(self.pktid, self.ip)
			Util.lock.release()
			now = time.time()
			if((now - before) < 20):
				Util.printLog('[QUER]: non faccio nulla perchè ho già elaborato la richiesta\n')
				del db
			else:
				self.timestamp = time.time()
				Util.lock.acquire()
				db.updateTimestamp(self.pktid, self.ip)
				Util.lock.release()
				self.do(db, self.pktid, self.ip, self.timestamp, Util.lock, self.string, self.peer_port, self.ttl, self.from_peer[82:], self.ip_request)
