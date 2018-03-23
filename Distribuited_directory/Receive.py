import socket
import ipaddress as ipaddr

class Receive():
	def __init__(self, my_ip, my_door):
		self.my_ip = my_ip
		self.my_door = my_door
		self.pktid_list = []
		self.bytes_read = 0

	
	#insersce un nuovo lecord nella lista dei packet id
	def inser_record(self):


	#rimuove un record dalla lista dei packet id
	def remove_record(self):

	def listen(self):
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

            while (self.bytes_read < 36):
                self.from_peer += other_peersocket.recv(36 - self.bytes_read)
                self.bytes_read = len(self.from_peer)

            if (self.from_peer[:4].decode() == "QUER"):
            	self.pktid = self.from_peer[4:15]
            	if(self.pktid in self.pktid_list)
            		#skip
            	else:
            		#aggiungi elemento alla lista
            		#invio pacchetto ai peer limitrofi
            		#funzione di invio di fracca



	def answer(self):
