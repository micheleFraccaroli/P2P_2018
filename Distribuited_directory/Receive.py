import socket
import time
import datetime
import ipaddress as ipaddr
import multiprocessing as mp

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
			print(self.from_peer.decode(), "\n")
			self.bytes_read = len(self.from_peer)
			while (self.bytes_read < 102):
				self.from_peer += other_peersocket.recv(102 - self.bytes_read)
				self.bytes_read = len(self.from_peer)
			print(self.from_peer[0:4].decode(), "\n")
			if(self.from_peer[0:4].decode() == "QUER"):
				self.pktid = self.from_peer[4:15].decode()
				print(pktid_list.get(self.pktid,'False'),'\n')
				if((pktid_list.get(self.pktid,'False'))!="False"):
					print('già presente\n')
					now = datetime.datetime.fromtimestamp(time.time())
					before = pktid_list[str(self.pktid)]
					diff = (now-before).total_seconds()

					if(diff>300):
						print("Invio ai vicini\n")
						print(pktid_list)
				else:
					pktid_list = self.insert_record(pktid_list, self.pktid)
					print("ho aggiunto un nuovo record al dizzionario\n")
					print(pktid_list)

'''
def answer(self):

'''
if __name__ == '__main__':

	pktid_list = {}

	Receive_4 = Receive('127.0.0.1','50004')
	Re_4 = mp.Process(target=Receive_4.listen_other)
	Re_4.start()

	Receive_6 = Receive('::1','50004')
	Re_6 = mp.Process(target=Receive_6.listen_other)
	Re_6.start()