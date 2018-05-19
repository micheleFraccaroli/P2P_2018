from threading import *
from Conn import Conn
import codecs
import Util
import math
from time import sleep
from dataBase import dataBase
from math import log
from random import shuffle
from operator import itemgetter # Per il sorting
from queue import * # Passaggio parametri tra socket
from D import D
import curses

class RF(Thread):
	def __init__(self, t_ipv4, t_ipv6, t_port):
		Thread.__init__(self)
		self.search = ""
		self.t_ipv4 = t_ipv4
		self.t_ipv6 = t_ipv6
		self.t_port = t_port
		self.list_answers = []
		self.md5_lfile_lpart = ()

	def run(self):
		#LOOK
		while((self.search == "") or (len(self.search)>20)):
			self.search = input("input non corretto per iniziare una ricerca: ")
		db = dataBase()
		self.sessionid = db.retrieveConfig(('sessionId',))
		self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)
		if(self.con.connection()):
			print('connesso')
			self.pkt_look = 'LOOK'+self.sessionid+self.search.ljust(20)
			self.con.s.send(self.pkt_look.encode())

			self.ack_look = self.con.s.recv(7)
			self.bytes_read = len(self.ack_look)

			while(self.bytes_read < 7):
				self.ack_look += self.con.s.recv(7 - self.bytes_read)
				self.bytes_read = len(self.ack_look)

			self.nanswer = int(self.ack_look[4:7].decode())
			n = 0
			while(n < self.nanswer):
				self.answer = self.con.s.recv(148)
				self.bytes_read = len(self.answer)
				while(self.bytes_read < 148):
					self.answer += self.con.s.recv(148 - self.bytes_read)
					self.bytes_read = len(self.answer)
				self.md5_lfile_lpart = (self.answer[:32].decode(), self.answer[132:142].decode(), self.answer[142:148].decode())
				self.list_answers.extend((self.answer[32:132].decode().strip(),self.md5_lfile_lpart))
				self.pkt_look += self.answer.decode()+"\n"
				n+=1
			self.list_answers.extend(("Abort",None))
			md5 = curses.wrapper(Util.menu, self.list_answers, ['Select a file:'])

			if(md5 != None):
				self.pkt_fchu = "FCHU"+self.sessionid+md5[0]
				lenfile = int(md5[1])
				lenpart = int(md5[2])
				nBit = int(math.ceil(lenfile/lenpart))

				#self.con.s.send(self.pkt_fchu.encode())
			else:
				print("Non faccio nulla...")
			self.con.deconnection()
		else:
			print("Errore durante la connessione...")
		#FINE LOOK
		print('fine look')
		queue = LifoQueue() #Coda LIFO
		controllerIsAlive = False # Stato del controller di download

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

		#########

		while True:

			c = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

			if not c.connection():

				print('Errore di connessione')

			else:

				# Ricezione dati FCHU

				c.s.send(self.pkt_fchu.encode())

				byte = []

				hitPeers = c.s.recv(7)
				readB = len(hitPeers)

				while(readB < 7):
					hitPeers += c.s.recv(7 - readB)
					readB = len(hitPeers)

				nBlock = math.ceil(nBit/8)
				nPeers = int(hitPeers[4:7].decode())

				c.deconnection()

				# Creazione dello stato del file su tutti i peer

				for peer in range(nPeers): # Ciclo per ogni peer

					byte.append([])

					for block in range(nBlock): # Ciclo per ogni blocco di un singolo peer

						offset = peer * nBlock

						byte[peer].append(ord(var[block + offset])) # Blocchi trasformati in interi

				# Creazione di una lista di parti pesata

				statusParts = [] # Dizionario delle parti inizializzato

				for i in range(nBit):
					statusParts.append([i,0])

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
				sleep(60)
				print('Terminato')
