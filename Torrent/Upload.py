from threading import *
from Conn import Conn
from dataBase import dataBase
from math import ceil
import Util
import os

class Worker(Thread):

	def __init__(self, sock):

		Thread.__init__(self)
		self.sock = sock

	def run(self):

		# Lettura della richiesta

		download = self.sock.recv(44)
		readB = len(download)
		while (readB < 44):
			download += self.sock.recv(44 - readB)
			readB = len(download)

		md5 = download[4:36].decode()
		part = int(download[36:].decode())

		#dal database devo estrarre i chunk relativi alla parte
		db = dataBase()

		lenPart = db.retrieveInfoFile(md5)
		Util.printLog(lenPart)
		nameFile = lenPart[3] 	# Nome del file 
		lenPart = lenPart[2] 	# Lunghezza della parte

		lenFile = os.stat('Files/' + nameFile).st_size
		seekPosition = lenPart * (part - 1) # Posiziono la testina sulla parte interessata

		if lenPart > 1024:

			lenChunk = int(db.retrieveConfig(('lenChunk',)))
			nChunk = ceil(lenPart/lenChunk)

		elif lenPart < 4:

			lenChunk = 1
			nChunk = lenPart

		else:
			lenChunk = ceil(lenPart/4) # Prevedo 4 chunk per parte
			nChunk = 4
			
		nparts = ceil(lenFile/lenPart)

		# Preparo ed invio il pacchetto

		self.sock.send(('AREP' + str(nChunk).zfill(6)).encode()) # Intestazione pacchetto AREP

		f = open('Files/' + nameFile, 'rb')

		f.seek(seekPosition, 0)

		for _ in range(nChunk - 1): # Ciclo dei chunk completi

			r = f.read(lenChunk)
			self.sock.send(str(len(r)).zfill(5).encode() + r)

		remainder = lenPart % lenChunk
		
		if remainder == 0: # Se non ho resto significa che l'ultimo chunk è completamente pieno
			remainder = lenChunk

		r = f.read(remainder)
		
		self.sock.send(str(len(r)).zfill(5).encode() + r)

		f.close()

class Upload(Thread):

	def __init__(self, ipv4, ipv6, port):

		Thread.__init__(self)
		self.ipv4 = ipv4
		self.ipv6 = ipv6
		self.port = int(port)

	def run(self):

		c = Conn(port=self.port)

		peer = c.initializeSocket()

		while True: # Ciclo di connessioni

			other_peer, addr = peer.accept()

			t = Worker(other_peer)
			t.start()