from threading import *
from Conn import Conn
import codecs
import Util
from time import sleep
from math import log
from random import shuffle
from operator import itemgetter # Per il sorting
from queue import * # Passaggio parametri tra socket
from D import D

class RF(Thread):
	def __init__(self, byt, t_ipv4, t_ipv6, t_port):

		Thread.__init__(self)
		self.byt = byt.zfill(8)
		self.search = ""
		self.t_ipv4 = t_ipv4
		self.t_ipv6 = t_ipv6
		self.t_port = t_port

	def run(self):
		#invio del pacchetto look, inizio ricerca
		while((self.search == "") and (len(self.search)>20)):
			self.search = input("input non corretto per iniziare una ricerca")

		self.sessionid = "1234567890123456"
		self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)
		if(self.con.connection()):
			self.pkt_look = "LOOK"+self.sessionid+self.search.ljust(20)
			self.con.s.send(self.pkt_look.encode())

			self.ack_look = self.con.s.recv(7)
			self.bytes_read = len(self.ack_look)

			while(self.bytes_read < 7):
				self.ack_look += self.con.s.recv(7 - self.bytes_read)
				self.bytes_read = len(self.ack_look)

			self.nanswer = int(self.ack_look[4:7].decode())
			n = 0
			self.pkt_look = ""
			while(n < self.nanswer and self.nanswer > 0):
				self.answer = self.con.s.recv(148)
				self.bytes_read = len(self.answer)
				while(self.bytes_read < 148):
					self.answer += self.con.s.recv(148 - self.bytes_read)
					self.bytes_read = len(self.answer)
					self.pkt_look += self.answer.decode()+"\n"
				n+=1
			print(self.pkt_look)
			self.con.deconnection()
		else:
			print("Errore durante la connessione...")

		queue = LifoQueue() #Coda LIFO
		controllerIsAlive = False # Stato del controller di download

		for _ in range(1):

			c = Conn('127.0.0.1','::1',3000)

			if not c.connection():

				print('Errore di connessione')

			else:

				# Ricezione dati ACHU

				c.s.send(self.byt.encode())

				byte = []

				nBlock = int(c.s.recv(8).decode())
				nBit = int(c.s.recv(8).decode())
				nPeers = int(c.s.recv(8).decode())

				statusParts = [] # Dizionario delle parti inizializzato
				for i in range(nBit):
					statusParts.append([i,0])

				by = 0
				var = ''
				print('blocchi: ',nBlock,'parti: ',nBit,'peers: ',nPeers)

				while by < nBlock * nPeers:
					var += codecs.decode(c.s.recv(nBlock * nPeers - by),'iso-8859-1')

					by = len(var)
				print('fatto')
				c.deconnection()
				######### CREO LA GRAFICA INIZIALE

				Util.lockGraphics.acquire()

				rowNumber = len(Util.rows) # Numero di file attualmente visualizzati

				descriptor = 'File' + str(Util.uniqueIdRow)
				Util.uniqueIdRow += 1
				Util.rows.append(descriptor)	# Salvo il tag che identifica il file in download

				y1 = Util.offset + Util.nameFileHeight + (Util.heightRow * rowNumber)
				y2 = y1 + Util.heightPart
				for i in range(0, nBit):

					x1 = Util.offset + (Util.widthPart * i)
					x2 = Util.offset + (Util.widthPart * (i + 1))
					idRec = Util.w.create_rectangle(x1, y1, x2, y2, fill="red", width=1, tags=(descriptor))	# Rettangoli

				# Ridefinizione delle coordinate basate su quelle precedenti
				y1 = y1 + Util.heightPart	# Coordinata Y in alto
				y2 = y2 + Util.heightLine	# Coordinata Y in basso
				for i in range(0, nBit, 10):

					x = Util.offset + Util.widthPart * i
					Util.w.create_line(x, y1, x, y2, tags=(descriptor))
					Util.w.create_text(x + Util.LeftPaddingText, y2, anchor="sw", text=str(i + 1), tags=(descriptor))	# Labels

				Util.w.create_text(Util.offset, Util.offset + (Util.heightRow * rowNumber), anchor="nw", text=descriptor, tags=(descriptor))

				Util.lockGraphics.release()
				# Ultima riga
				'''
				if i == nBit:

					x = x + Util.widthPart * (nBit - i - 1)
					Util.w.create_line(x, y1, x, y2, tags=(descriptor))
					Util.w.create_text(x + Util.LeftPaddingText, y2, anchor="sw", text=str(nBit), tags=(descriptor))
				'''

				#########

				# Creazione dello stato del file su tutti i peer

				for peer in range(nPeers): # Ciclo per ogni peer

					byte.append([])

					for block in range(nBlock): # Ciclo per ogni blocco di un singolo peer

						offset = peer * nBlock

						byte[peer].append(ord(var[block + offset])) # Blocchi trasformati in interi

				# Creazione di una lista di parti pesata

				for peer in range(nPeers):

					for block in range(nBlock):

						bit = int('{:08b}'.format(byte[peer][block])[::-1], 2) # Inverto i bit

						while bit > 0:

							maxBit = int(log(bit,2)) # Indice del più alto bit impostato ad 1
							offset = 8 * block

							statusParts[maxBit + offset][1] += 1

							bit = bit ^ (1 << maxBit) # Elimino il bit utilizzato

				shuffle(statusParts) # Mescolo la lista (scelta random delle parti col medesimo peso)

				statusParts = [part[0] for part in sorted(statusParts,key=itemgetter(1))] # Riordino della lista dalla parte più rara (rerest first)

				if not controllerIsAlive:
					print('DOWNLOAD ATTIVATO')
					t = D(statusParts, queue, descriptor, idRec - (nBit - 1))
					t.start()
					t.join()

				print('Terminato')
