import socket
import Util
import time
import datetime
import ipaddress as ipaddr
import multiprocessing as mp
from dataBase import dataBase

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

	#mette in ascolto una socket in ipv4 e in ipv6, pronta per ricevere le richieste
	#quando arriva una richiesta, viene controllato se il pachet id è già stato salvato nel dizzionario
	#nel caso positivo verifico se sono trascorsi 300s
	#se sono trascorsi, cancello la voce dal dizzionario e invio le richieste ai peer vicini, 
	#in caso contrario non faccio nulla, evitando così la presenza di richieste rindondanti nella rete

	def listen_other(self):
		global pktid_list
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
			print('sono in ascolto\n')
			other_peersocket, addr = peersocket.accept()
			self.from_peer = other_peersocket.recv(102)
			self.bytes_read = len(self.from_peer)

			while (self.bytes_read < 102):
				self.from_peer += other_peersocket.recv(102 - self.bytes_read)
				self.bytes_read = len(self.from_peer)

			if(self.from_peer[0:4].decode() == "QUER"):
				self.pktid = self.from_peer[4:16].decode()
				self.ip  = self.from_peer[16:75].decode()

				db = dataBase()
				res = db.retrivenSearch(self.pktid, self.ip)

				if(res == 0):
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
						print('non faccio nulla\n')
					else:
						print('andrò ad aggiornare nel db il timestamp\n')
					del db 

'''
def answer(self):

'''
if __name__ == '__main__':

	db = dataBase()
	db.create()
	del db

	Receive_4 = Receive('127.0.0.1','50004')
	Re_4 = mp.Process(target=Receive_4.listen_other)
	Re_4.start()

	Receive_6 = Receive('::1','50004')
	Re_6 = mp.Process(target=Receive_6.listen_other)
	Re_6.start()