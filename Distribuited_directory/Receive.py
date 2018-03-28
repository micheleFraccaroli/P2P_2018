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
from Vicini import Vicini
from Vicini_res import Vicini_res
from Config import Config
from Upload import Upload

class Receive():
	def __init__(self, my_ip, my_door, config):
		self.my_ip = my_ip
		self.my_door = int(my_door)
		#self.pktid_list = pktid_list
		self.bytes_read = 0
		self.config = config

	
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

			#Controllo il tipo di richiesta

			while (self.bytes_read < 4):
				self.from_peer += other_peersocket.recv(4 - self.bytes_read)
				self.bytes_read = len(self.from_peer)
				print(self.from_peer)

			if(self.from_peer[:4].decode() == "QUER"):

				while (self.bytes_read < 102):
					self.from_peer += other_peersocket.recv(102 - self.bytes_read)
					self.bytes_read = len(self.from_peer)
					print(self.from_peer)

				self.pktid = self.from_peer[4:16].decode()
				self.ip  = self.from_peer[16:75].decode()
				self.door = self.from_peer[75:80].decode()
				self.ttl = self.from_peer[80:82].decode()
				self.string = self.from_peer[82:].decode().rstrip()

				db = dataBase()
				res = db.retrivenSearch(self.pktid, self.ip)

				if(res == 0):

					file_found = []

					for file in os.listdir("img"):
						if re.search(self.string, file, re.IGNORECASE):
							file_found.append(file)

					if(len(file_found) != 0):
						self.answer(file_found, self.pktid, self.ip, self.door, other_peersocket)
					else:
						print("andrò ad eseguire l'inoltro ai vicini della richiesta\n")
						near = Vicini(self.config)

						# thread per ascolto di riposta dei vicini
						th_near = Vicini_res(self.port)
						th_near.start()
						
						near.searchNeighborhood() #invia la richiesta ai vicini
						th_near.join() #viene chiuso il thread e il db è aggiornato con i nuovi vicini

						self.neighbors = db.retrieveNeighborhood() #mi tiro giù i vicini
						for n in self.neighbors:
							addr = Util.ip_deformatting(n[0], n[1], self.ttl)
								
							#ip4 = ipad.ip_address(n[0][:15])
							ip6 = ipad.ip_address(n[0][16:])

							self.con = Conn(addr[0], str(ip6), addr[2])
							try:
								self.con.connection()
								self.con.s.send(self.from_peer.encode())
								self.con.deconnection()
							except IOError as expt:
								print("Errore di connessione")
								print(expt)
								sys.exit(0)

					self.timestamp = time.time()
					db.insertSearch(self.pktid, self.ip, self.timestamp)

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

						for file in os.listdir("img"):
							if re.search(self.string, file, re.IGNORECASE):
								file_found.append(file)

						if(len(file_found) != 0):
							self.answer(file_found, self.pktid, self.ip, self.door, other_peersocket)
						else:
							print("andrò ad eseguire l'inoltro ai vicini della richiesta\n")
							near = Vicini(self.config)

							# thread per ascolto di riposta dei vicini
							th_near = Vicini_res(self.port)
							th_near.start()
							
							near.searchNeighborhood() #invia la richiesta ai vicini
							th_near.join() #viene chiuso il thread e il db è aggiornato con i nuovi vicini

							self.neighbors = db.retrieveNeighborhood() #mi tiro giù i vicini
							for n in self.neighbors:
								addr = Util.ip_deformatting(n[0], n[1], self.ttl)
									
								#ip4 = ipad.ip_address(n[0][:15])
								ip6 = ipad.ip_address(n[0][16:])

								self.con = Conn(addr[0], str(ip6), addr[2])
								try:
									self.con.connection()
									self.con.s.send(self.from_peer.encode())
									self.con.deconnection()
								except IOError as expt:
									print("Errore di connessione")
									print(expt)
									sys.exit(0)

							db.updateTimestamp(self.pktid, self.ip)

						del db				

			elif(self.from_peer[0:4].decode() == "RETR"):
				while (self.bytes_read < 36):
					self.from_peer += other_peersocket.recv(102 - self.bytes_read)
					self.bytes_read = len(self.from_peer)
					print(self.from_peer)
					up = Upload(self, ip, port)
					up.Upload()


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