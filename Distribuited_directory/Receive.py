import socket
import time
import datetime
import ipaddress as ipaddr


class Receive():
	def __init__(self, my_ip, my_door):
		self.my_ip = my_ip
		self.my_door = int(my_door)
		self.pktid_dict = {}
		self.bytes_read = 0

	
	#insersce un nuovo lecord nella lista dei packet id

	def insert_record(self, pktid_dict, key):
		del pktid_dict[str(key)]
		return pktid_list

	#rimuove un record dalla lista dei packet id

	def remove_record(self, pktid_dict, key):
		pktid_dict[str(key)] = time.time()
		return pktid_list

	#mette in ascolto una socket in ipv4 e in ipv6, pronta per ricevere le richieste
	#quando arriva una richiesta, viene controllato se il pachet id è già stato salvato nel dizzionario
	#nel caso positivo verifico se sono trascorsi 300s
	#se sono trascorsi, cancello la voce dal dizzionario e invio le richieste ai peer vicini, 
	#in caso contrario non faccio nulla, evitando così la presenza di richieste rindondanti nella rete

	def listen_other(self):
		if(str(ipaddr.ip_address(self.my_ip)).find('.') != -1): #ha trovato il punto, quindi ipv4
			peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			peersocket.bind((self.my_ip, self.my_door))
		else:
		    peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		    peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		    peersocket.bind((str(ipaddr.ip_address(self.my_ip)), self.my_door))

		peersocket.listen(5)

		while True:
			other_peersocket, addr = peersocket.accept()
			self.from_peer = other_peersocket.recv(102)
			self.bytes_read = len(self.from_peer)

			while (self.bytes_read < 102):
				self.from_peer += other_peersocket.recv(102 - self.bytes_read)
				self.bytes_read = len(self.from_peer)

			if (self.from_peer[:4].decode() == "QUER"):
				self.pktid = self.from_peer[4:15].decode()

				if(self.pktid in self.pktid_list):
					now = datetime.datetime.fromtimestamp(ts)
					before = self.pktid_list[str(self.pktid)]
					diff = (now-before).total_seconds()

					if(diff>300):
						self.pktid_list = remove_record(self.pktid_list, self.pktid)
						print("ho eliminato un record dal dizzionario\n")
						print(self.pktid_list)
				else:
					self.pktid_list = insert_record(self.pktid_list, self.pktid)
					print("ho aggiunto un nuovo record al dizzionario\n")
					print(self.pktid_list)

'''
def answer(self):

'''
if __name__ == '__main__':

	R = Receive('127.0.0.1','50004')
	R.listen_other()