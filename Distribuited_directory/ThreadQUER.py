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
from Conn import Conn
from Vicini import Vicini
from Vicini_res import Vicini_res
from Config import Config
from Upload import Upload
import threading as th
import random as ra
from File_system import File_system

#inizializzo il thread
class ThreadQUER(th.Thread):
	def __init__(self, my_door, quer_pkt, ip_request, ipv4, ipv6):
		th.Thread.__init__(self)
		self.my_door = int(my_door)
		self.bytes_read = 0
		self.from_peer = quer_pkt
		self.ip_request = str(ip_request)
		self.ipv4 = ipv4
		self.ipv6 = ipv6
	
	#insersce un nuovo record nella lista dei packet id

	def remove_record(self, pktid_dict, key):
		del pktid_dict[str(key)]
		print(pktid_dict[str(key)])
		return pktid_dict


	#rimuove un record dalla lista dei packet id

	def insert_record(self, pktid_dict, key):
		pktid_dict[str(key)] = datetime.datetime.fromtimestamp(time.time())
		print(pktid_dict[str(key)])
		return pktid_dict

	#calcolo l'md5 dei file della ricerca

	def convert_md5(self, file_list):
		dict_list = {}
		for file in file_list:
			open_file = open('img/'+file, 'rb')
			contenuto = open_file.read()
			FileHash = hashlib.md5()
			FileHash.update(contenuto)
			dict_list[FileHash.hexdigest()] = file
			#il file File_System viene utilizzato come appoggio alla funzione di upload
			file_write = File_system(FileHash.hexdigest(), file)
			file_write.write()
			open_file.close()
		return dict_list

	#risponde al peer che ha effettuato una ricerca, incompleta
	def answer(self, file_list, pktid, ip, my_ip, my_port, portB):
		dict_list = self.convert_md5(file_list)
		#stabilisco una connessione con il peer che ha iniziato
		addr = Util.ip_deformatting(ip, portB, None)
	
		ip6 = ipad.ip_address(ip[16:])

		self.con = Conn(addr[0], str(ip6), addr[2])

		#self.con = Conn(addr[0], addr[1], addr[2])
		
		#my_ip = "172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004"

		try:
			self.con.connection()
			for md5 in dict_list:
				file_name = dict_list[md5].ljust(100,' ')
				answer = "AQUE"+pktid+my_ip+my_port+md5+file_name
				self.con.s.send(answer.encode())
			self.con.deconnection()
		except IOError as expt:
			print("Errore di connessione")
			print(expt)
			sys.exit(0)

	#ricerca dei vicini
	def search_neighbors(self, db, ip_request, new_quer):
		self.neighbors = db.retrieveNeighborhood() #mi tiro giù i vicini
		for n in self.neighbors:
			addr = Util.ip_deformatting(n[0], n[1], None)
				
			#ip4 = ipad.ip_address(n[0][:15])
			ip6 = ipad.ip_address(n[0][16:])

			self.con = Conn(addr[0], str(ip6), addr[2])
			try:
				self.con.connection()
				if((addr[0] != ip_request) and (ip6 != ip_request)):
					self.con.s.send(new_quer.encode())
				self.con.deconnection()
			except IOError as expt:
				print("Errore di connessione")
				print(expt)
				sys.exit(0)

	#vado a calcolare il nuovo ttl

	def new_ttl(self, ttl):
		new_ttl = ttl - 1
		if(new_ttl>9):
			str(new_ttl)
		else:
			str(new_ttl).rjust(2, '0')
		return str(new_ttl)

	#funzione principale

	def run(self):

		self.pktid = self.from_peer[4:20]
		self.ip  = self.from_peer[20:75]
		self.door = self.from_peer[75:80]
		self.ttl = int(self.from_peer[80:82])
		self.string = self.from_peer[82:].rstrip()
		db = dataBase()
		res = db.retrivenSearch(self.pktid, self.ip)
		self.my_ip = str(self.ipv4)+"|"+str(self.ipv6)

		if(res == 0):

			file_found = []
			self.timestamp = time.time()
			db.insertSearch(self.pktid, self.ip, self.timestamp)

			for file in os.listdir("img"):
				if re.search(self.string, file, re.IGNORECASE):
					file_found.append(file)

			if(len(file_found) != 0):
				#rispondo e apro l'upload
				self.new_port = ra.randint(50010, 59999)
				self.answer(file_found, self.pktid, self.ip, self.my_ip, str(self.new_port), self.door)
				if(self.ttl>1):
					self.ttl_new = self.new_ttl(self.ttl)
					self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.string
					self.search_neighbors(db, self.ip_request, self.new_quer)
				del db
				up = Upload(self.new_port)
				up.upload()
				
			elif(self.ttl>1):
				print("andrò ad eseguire l'inoltro ai vicini della richiesta\n")
				#vado a decrementare il ttl di uno e costruisco la nuova query da inviare ai vicini
				self.ttl_new = self.new_ttl(self.ttl)
				self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.string
				self.search_neighbors(db, self.ip_request, self.new_quer)

			del db

		else:
			print("E' già presente un pacchetto con questo pktid\n")

			before = db.retriveSearch(self.pktid, self.ip)
			now = time.time()

			if((now - before) < 30):
				print('non faccio nulla perchè ho già elaborato la richiesta\n')
				del db
			else:
				file_found = []
				self.timestamp = time.time()
				db.updateTimestamp(self.pktid, self.ip)

				for file in os.listdir("img"):
					if re.search(self.string, file, re.IGNORECASE):
						file_found.append(file)

				if(len(file_found) != 0):
					#rispondo e apro l'upload
					self.new_port = ra.randint(50010, 59999)
					self.answer(file_found, self.pktid, self.ip, self.my_ip, str(self.new_port), self.door)
					if(self.ttl>1):
						self.ttl_new = self.new_ttl(self.ttl)
						self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.string
						self.search_neighbors(db, self.ip_request, self.new_quer)
					del db
					up = Upload(self.new_port)
					up.upload()
					
				elif(self.ttl>1):
					print("andrò ad eseguire l'inoltro ai vicini della richiesta 2\n")
					#vado a decrementare il ttl di uno e costruisco la nuova query da inviare ai vicini
					self.ttl_new = self.new_ttl(self.ttl)
					self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.string
					self.search_neighbors(db, self.ip_request, self.new_quer)

				del db

'''
if __name__ == '__main__':

	db = dataBase()
	conf = Config()
	db.create(conf)
	del db
	
	Receive_4 = Receive('127.0.0.1','50004', conf)
	Re_4 = mp.Process(target=Receive_4.listen_other)
	Re_4.start()

	Receive_6 = Receive('::1','50004', conf)
	Re_6 = mp.Process(target=Receive_6.listen_other)
	Re_6.start()
	
	pktid = 'COR3BEWPI98CHFOP'
	ip = '172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004'
	door = '50004'
	ttl = '02'
	ricerca = 'CrAs'
	ricerca_20 = ricerca.ljust(20,' ')
	string_request = "QUER"+pktid+ip+door+ttl+ricerca_20

	th_QUER = Thread_quer('127.0.0.1', '::1', '50003', string_request)
	th_QUER.start()
'''