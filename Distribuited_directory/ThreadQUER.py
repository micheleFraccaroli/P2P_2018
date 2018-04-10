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
	def __init__(self, my_door, quer_pkt, ip_request, ipv4, ipv6, lock, config, up_port):
		th.Thread.__init__(self)
		self.my_door = int(my_door)
		self.bytes_read = 0
		self.from_peer = quer_pkt
		self.ip_request = ip_request
		self.ipv4 = ipv4
		self.ipv6 = ipv6
		self.lock = lock
		self.config = config
		self.new_port = up_port
	
	#insersce un nuovo record nella lista dei packet id

	def remove_record(self, pktid_dict, key):
		del pktid_dict[str(key)]
		Util.printLog(pktid_dict[str(key)])
		return pktid_dict


	#rimuove un record dalla lista dei packet id

	def insert_record(self, pktid_dict, key):
		pktid_dict[str(key)] = datetime.datetime.fromtimestamp(time.time())
		Util.printLog(pktid_dict[str(key)])
		return pktid_dict

	#calcolo l'md5 dei file della ricerca

	def convert_md5(self, file_list):
		dict_list = {}
		index = 0
		for file in file_list:
			#index = ra.randint(50000, 59999)
			open_file = open('img/'+file, 'rb')
			contenuto = open_file.read()
			FileHash = hashlib.md5()
			FileHash.update(contenuto)
			dict_list[index] = FileHash.hexdigest()+file
			#il file File_System viene utilizzato come appoggio alla funzione di upload
			file_write = File_system(FileHash.hexdigest(), file)
			file_write.write()
			open_file.close()
			index = index +1
		return dict_list

	#risponde al peer che ha effettuato una ricerca, incompleta
	def answer(self, file_list, pktid, ip, my_ipv4, my_ipv6, my_port, portB):
		dict_list = self.convert_md5(file_list)
		#stabilisco una connessione con il peer che ha iniziato
		addr = Util.ip_deformatting(ip, portB, None)
	
		ip6 = ipad.ip_address(ip[16:])

		self.con = Conn(addr[0], str(ip6), addr[2])
		
		my_ip_port = Util.ip_formatting(my_ipv4, my_ipv6, my_port)

		try:
			self.con.connection()
			for index in dict_list:
				md5_file_name = dict_list[index].ljust(132,' ')
				answer = "AQUE"+pktid+my_ip_port+md5_file_name
				#print(answer)
				self.con.s.send(answer.encode())
				#print(str(answer.encode())+"\n")
				#print(str(len(answer.encode()))+"\n")
			self.con.deconnection()
		except IOError as expt:
			print("Errore di connessione")
			print(expt)
			sys.exit(0)

	#ricerca dei vicini
	def search_neighbors(self, db, ip_request, new_quer):
		self.neighbors = db.retrieveNeighborhood(self.config) #mi tiro giù i vicini
		Util.printLog("------------------------- Sono tornato nel threadQuer ------------------------")
		for n in self.neighbors:
			addr = Util.ip_deformatting(n[0], n[1], None)
			Util.printLog("------------- Dentro al for di threadQUER -----------------------")
			#ip4 = ipad.ip_address(n[0][:15])
			ip6 = ipad.ip_address(n[0][16:])
			self.con = Conn(addr[0], str(ip6), addr[2])
			try:
				self.con.connection()
				Util.printLog("-----------------Dentro alla connection threadQUER --------------")
				if((addr[0] != ip_request) and (str(ip6) != ip_request) and (new_quer[20:35] != addr[0])):
					self.con.s.send(new_quer.encode())
					Util.printLog('QUER: inoltro richiesta a : ' + str(addr[0]))
					#Util.printLog(str(addr[0]))
				self.con.deconnection()
			except IOError as expt:
				print("Errore di connessione")
				print(expt)
				sys.exit(0)

	#vado a calcolare il nuovo ttl

	def new_ttl(self, ttl):
		new_ttl = ttl - 1
		if(new_ttl>9):
			c = str(new_ttl)
		else:
			c = str(new_ttl).rjust(2, '0')
		return c

	#funzione principale

	def run(self):

		self.pktid = self.from_peer[4:20]
		self.ip  = self.from_peer[20:75]
		self.door = self.from_peer[75:80]
		self.ttl = int(self.from_peer[80:82])
		self.string = self.from_peer[82:].rstrip()
		db = dataBase()
		self.lock.acquire()
		res = db.retrivenSearch(self.pktid, self.ip)
		#self.my_ip = str(self.ipv4)+"|"+str(self.ipv6)
		Util.printLog('Avvio il thread QUER')

		if(res == 0):

			file_found = []
			self.timestamp = time.time()

			db.insertSearch(self.pktid, self.ip, self.timestamp)
			self.lock.release()
			for file in os.listdir("img"):
				if re.search(self.string, file, re.IGNORECASE):
					file_found.append(file)

			if(len(file_found) != 0):
				#rispondo
				
				self.answer(file_found, self.pktid, self.ip, self.ipv4, self.ipv6, str(self.new_port), self.door)
				if(self.ttl>1):
					self.ttl_new = self.new_ttl(self.ttl)
					self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.from_peer[82:]
					self.lock.acquire()
					self.search_neighbors(db, self.ip_request, self.new_quer)
					self.lock.release()
				#del db
				#up = Upload(self.new_port)
				#up.upload()
				
			elif(self.ttl>1):
				Util.printLog("QUER: eseguo l'inoltro ai vicini della richiesta\n")
				#vado a decrementare il ttl di uno e costruisco la nuova query da inviare ai vicini
				self.ttl_new = self.new_ttl(self.ttl)
				self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.from_peer[82:]
				self.lock.acquire()
				self.search_neighbors(db, self.ip_request, self.new_quer)
				self.lock.release()
			del db

		else:
			Util.printLog("QUER: già presente un pacchetto con questo pktid\n")
			
			before = db.retriveSearch(self.pktid, self.ip)
			self.lock.release()
			now = time.time()

			if((now - before) < 30):
				Util.printLog('QUER: non faccio nulla perchè ho già elaborato la richiesta\n')
				del db
			else:
				file_found = []
				self.timestamp = time.time()
				self.lock.acquire()
				db.updateTimestamp(self.pktid, self.ip)
				self.lock.release()
				for file in os.listdir("img"):
					if re.search(self.string, file, re.IGNORECASE):
						file_found.append(file)

				if(len(file_found) != 0):
					#rispondo e apro l'upload
					
					self.answer(file_found, self.pktid, self.ip, self.ipv4, self.ipv6, str(self.new_port), self.door)
					if(self.ttl>1):
						self.ttl_new = self.new_ttl(self.ttl)
						self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.from_peer[82:]
						self.lock.acquire()
						self.search_neighbors(db, self.ip_request, self.new_quer)
						self.lock.release()
					#del db
					#up = Upload(self.new_port)
					#up.upload()
					
				elif(self.ttl>1):
					Util.printLog("QUER: eseguo l'inoltro ai vicini della richiesta 2\n")
					#vado a decrementare il ttl di uno e costruisco la nuova query da inviare ai vicini
					self.ttl_new = self.new_ttl(self.ttl)
					self.new_quer = "QUER"+self.pktid+self.ip+self.door+self.ttl_new+self.from_peer[82:]
					self.lock.acquire()
					self.search_neighbors(db, self.ip_request, self.new_quer)
					self.lock.release()
				del db

'''
if __name__ == '__main__':

	#db = dataBase()
	#conf = Config()
	#db.create(conf)
	#del db
	
	#Receive_4 = Receive('127.0.0.1','50004', conf)
	#Re_4 = mp.Process(target=Receive_4.listen_other)
	#Re_4.start()

	#Receive_6 = Receive('::1','50004', conf)
	#Re_6 = mp.Process(target=Receive_6.listen_other)
	#Re_6.start()
	lock = th.Lock()
	pktid = 'COR3BEWPI98CHFOP'
	ip = '172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004'
	door = '50004'
	ttl = '02'
	ricerca = 'bu'
	ricerca_20 = ricerca.ljust(20,' ')
	string_request = "QUER"+pktid+ip+door+ttl+ricerca_20

	th_QUER = ThreadQUER('50003', string_request, "172.16.8.2", "172.16.8.5", "fc00::8:5", lock, "config")
	th_QUER.start()
'''