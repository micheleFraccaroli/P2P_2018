from threading import *
from Conn import Conn

class Upload(Thread):

	def __init__(self, ipv4, ipv6, port):

		Thread.__init__(self)
		self.ipv4 = ipv4
		self.ipv6 = ipv6
		self.port = port

	def run(self):

		c = Conn(port=self.port)

		peer = c.initializeSocket()

		while True: # Ciclo di connessioni

			other_peer, addr = peer.accept()

			# Lettura della richiesta

			download = other_peer.recv(44)
			readB = len(download)
	        while (readB < 44):
	            download += other_peer.recv(44 - readB)
	            readB = len(download)

	        md5 = download[4:36].decode()
	        part = download[36:].decode()

	        #dal database devo estrarre i chunk relativi alla parte (e i dati per l'invio)





	        # Ho i dati

	        packet = 'AREP' + # Preparo il pacchetto AREP

	        # Invio i dati