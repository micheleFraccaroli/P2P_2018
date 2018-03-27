import socket
from pathlib import Path
import glob
import Util
import time
import datetime
import re
import os
import ipaddress as ipaddr
import hashlib
import multiprocessing as mp
from dataBase import dataBase
from Config import Config

class Receive():
	def __init__(self, my_ip, my_door):
		self.my_ip = my_ip
		self.my_door = int(my_door)
		#self.pktid_list = pktid_list
		self.bytes_read = 0

	
	#insersce un nuovo lecord nella lista dei packet id

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
			dict_list[file] = FileHash.hexdigest()
		return dict_list

	#risponde al peer che ha effettuato una ricerca

	def answer(self, file_list, pktid, ip, door, other_peersocket):
		dict_list = self.convert_md5(file_list)
		for file in dict_list:
			file_complete = file.ljust(100,' ')
			answer = "AQUE"+pktid+ip+door+dict_list[file]+file_complete
			other_peersocket.send(answer.encode())

	def listen_other(self):
		if(str(ipaddr.ip_address(self.my_ip)).find('.') != -1): #ha trovato il punto, quindi ipv4
			peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			peersocket.bind((self.my_ip, self.my_door))
			print('Uso ipv4\n')
		else:
		    peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		    peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		    peersocket.bind((str(ipaddr.ip_address(self.my_ip)), self.my_door))
		    print('Uso ipv6\n')

		peersocket.listen(5)

		while True:
			other_peersocket, addr = peersocket.accept()
			self.from_peer = other_peersocket.recv(102)
			self.bytes_read = len(self.from_peer)

			while (self.bytes_read < 102):
				self.from_peer += other_peersocket.recv(102 - self.bytes_read)
				self.bytes_read = len(self.from_peer)

			if(self.from_peer[0:4].decode() == "QUER"):

				self.pktid = self.from_peer[4:16].decode()
				self.ip  = self.from_peer[16:75].decode()
				self.door = self.from_peer[75:80].decode()
				self.ttl = self.from_peer[80:82].decode()
				self.string = self.from_peer[82:].decode().rstrip()

				db = dataBase()
				res = db.retrivenSearch(self.pktid, self.ip)

				if(res == 0):
					print("vado a verificare se possiedo il file indicato nella ricerca\n")

					file_found = []

					for file in os.listdir("img"):
						if re.search(self.string, file, re.IGNORECASE):
							file_found.append(file)

					if(len(file_found) != 0):
						self.answer(file_found, self.pktid, self.ip, self.door, other_peersocket)

					print("vado ad aggiungere un nuovo record al dizzionario\n")
					self.timestamp = time.time()
					db.insertSearch(self.pktid, self.ip, self.timestamp)
					#andrò ad eseguire l'inoltro ai vicini della richiesta
					del db								
				else:
					print("E' già presente un pacchetto con questo pktid\n")
					#vado a controllare se il timestamp è > o < di 300s e
					before = db.retriveSearch(self.pktid, self.ip)
					now = time.time()
					if((now - before) < 300):
						print('non faccio nulla perchè ho già elaborato la richiesta\n')
					else:
						print('andrò ad aggiornare nel db il timestamp\n')
					del db 


if __name__ == '__main__':

	db = dataBase()
	conf = Config()
	db.create(conf)
	del db

	Receive_4 = Receive('127.0.0.1','50004')
	Re_4 = mp.Process(target=Receive_4.listen_other)
	Re_4.start()

	Receive_6 = Receive('::1','50004')
	Re_6 = mp.Process(target=Receive_6.listen_other)
	Re_6.start()