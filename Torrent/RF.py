from threading import *
from Conn import Conn
import codecs
import Util
import math
from time import sleep
from dataBase import dataBase
from math import log
from Config import Config
from random import shuffle
from operator import itemgetter # Per il sorting
from queue import * # Passaggio parametri tra socket
from D import D
import curses
from pathlib import Path
from tkinter import Button, PhotoImage

def pauseAndplay(b, cond, queue):

	if b['image'] == 'pyimage1': # Sono in play

		queue.put('pause')
		b['image'] = Util.play

	else: # Sono in pause

		b['image'] = Util.pause

		cond.acquire()
		cond.notify()
		cond.release()

def stop(cond, queue):

	queue.put('stop')

	cond.acquire()
	cond.notify()
	cond.release()

class RF(Thread):
	def __init__(self, config, search):
		Thread.__init__(self)
		self.t_ipv4 = config.trackerV4
		self.t_ipv6 = config.trackerV6
		self.t_port = config.trackerP
		self.search = search

	def run(self):

		# LOOK

		ers = [] # Lista per il menù

		db = dataBase()
		sessionid = db.retrieveConfig(('sessionId',))

		con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)
		if con.connection():

			pkt_look = 'LOOK' + sessionid + self.search.ljust(20)

			con.s.send(pkt_look.encode())

			ack_look = con.s.recv(7)	# Ricezione intestazione
			bytes_read = len(ack_look)

			while bytes_read < 7:

				ack_look += con.s.recv(7 - bytes_read)
				bytes_read = len(ack_look)

			nanswer = int(ack_look[4:7].decode())
			list_answers = []

			for _ in range(nanswer):	# Per ogni md5

				answer = con.s.recv(148)
				bytes_read = len(answer)

				while bytes_read < 148:

					answer += con.s.recv(148 - bytes_read)
					bytes_read = len(answer)

				md5_lfile_lpart = (answer[:32].decode(), answer[132:142].decode(), answer[142:148].decode(), answer[32:132].decode())
				list_answers.extend((answer[32:132].decode().strip(),md5_lfile_lpart))

			list_answers.extend(("Abort",None))

			con.deconnection()

			Util.searchLock.acquire()
			Util.activeSearch += 1
			Util.searchLock.release()
			Util.menuLock.acquire()
			# Menù
			md5 = curses.wrapper(Util.menu, list_answers, ['Select a file:'])

			# md5[0] -> md5, md5[1] -> lenFile, md5[2] -> lenPart
			if md5 != None:

				if Path('Files/' + md5[3]).is_file():

					res = curses.wrapper(Util.menu,['Yes',True,'No',False],['The file requested already exists. Override it?'])

					if not res:

						print('Overwrite? Nop')
						exit()

				pkt_fchu = "FCHU" + sessionid + md5[0]

				lenfile = int(md5[1])
				lenpart = int(md5[2])
				md5 = md5[0]
				nBit = int(math.ceil(lenfile/lenpart))
				infoFile = md5[3] # Mi tengo solo il nome del file

			else:

				Util.printLog("Download aborted...")
				Util.menuLock.release()

				Util.searchLock.acquire()
				Util.activeSearch -= 1
				if Util.activeSearch == 0:

					Util.searchIncoming.acquire()
					Util.searchIncoming.notify()
					Util.searchIncoming.release()

				Util.searchLock.release()

				exit()
		else:

			Util.printLog("Error. Unable to connect to the tracker")
			exit()

		Util.menuLock.release()
		
		Util.searchLock.acquire()
		Util.activeSearch -= 1
		
		if Util.activeSearch == 0:

			Util.searchIncoming.acquire()
			Util.searchIncoming.notify()
			Util.searchIncoming.release()

		Util.searchLock.release()

		#FINE LOOK

		queue = LifoQueue() #Coda LIFO
		controllerIsAlive = False # Stato del controller di download

		######### CREO LA GRAFICA INIZIALE

		Util.lockGraphics.acquire()

		rowNumber = len(Util.rows) # Numero di file attualmente visualizzati

		descriptor = 'File' + str(Util.uniqueIdRow)
		Util.uniqueIdRow += 1
		Util.rows.append(descriptor)	# Salvo il tag che identifica il file in download

		y1 = Util.offsety + Util.nameFileHeight + (Util.heightRow * rowNumber)
		y2 = y1 + Util.heightPart
		for i in range(0, nBit):

			x1 = Util.offsetx + (Util.widthPart * i)
			x2 = Util.offsetx + (Util.widthPart * (i + 1))
			idRec = Util.w.create_rectangle(x1, y1, x2, y2, fill="red", width=1, tags=(descriptor))	# Rettangoli

		# Ridefinizione delle coordinate basate su quelle precedenti
		y1 = y1 + Util.heightPart	# Coordinata Y in alto
		y2 = y2 + Util.heightLine	# Coordinata Y in basso
		for i in range(0, nBit, 10):

			x = Util.offsetx + Util.widthPart * i
			Util.w.create_line(x, y1, x, y2, tags=(descriptor))
			Util.w.create_text(x + Util.LeftPaddingText, y2, anchor="sw", text=str(i + 1), tags=(descriptor))	# Labels

		Util.w.create_text(Util.offsetx, Util.offsety + (Util.heightRow * rowNumber), anchor="nw", text=infoFile, tags=(descriptor))	# Nome file

		dCond = Condition() # Condizione per fermare il download

		# Bottoni

		#image = Image.open("mazzini.jpeg").resize((20,20), Image.ANTIALIAS)

		b = Button(Util.master, height='10', width='10', image=Util.pause)
		#b.pack()
		b['command'] = lambda: pauseAndplay(b, dCond, queue)
		b.place(x=0, y=Util.offsety + (Util.heightRow * rowNumber))

		b2 = Button(Util.master, height='10', width='10', image=Util.stop)
		#b2.pack(ipadx=20, ipady=Util.offsety + (Util.heightRow * rowNumber))
		b2['command'] = lambda: stop(dCond, queue)
		b2.place(x=20, y=Util.offsety + (Util.heightRow * rowNumber))

		Util.buttonsList.append([b, b2])

		# Statistiche

		Util.w.create_text(Util.labelOffsetx, Util.labelDistance + Util.offsety + (Util.heightRow * rowNumber), anchor="nw", text='Progress: \t\t0%', tags=(descriptor))	# Nome file
		Util.w.create_text(Util.labelOffsetx, (Util.labelDistance * 2) + Util.offsety + (Util.heightRow * rowNumber), anchor="nw", text='Downloaded: \t0', tags=(descriptor))	# Nome file
		Util.w.create_text(Util.labelOffsetx, (Util.labelDistance * 3) + Util.offsety + (Util.heightRow * rowNumber), anchor="nw", text='Total: \t\t' + str(nBit), tags=(descriptor))	# Nome file

		Util.lockGraphics.release()

		#########

		# Risposta di FCHU

		while True:

			c = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

			if not c.connection():

				Util.printLog('Connection Error...')

			else:

				c.s.send(pkt_fchu.encode())


				hitPeers = c.s.recv(7)	# Intestazione pacchetto AFCH
				readB = len(hitPeers)

				listPeers = [] # Tutti i peer
				listStatus = []

				while(readB < 7):
					hitPeers += c.s.recv(7 - readB)
					readB = len(hitPeers)

				nBlock = math.ceil(nBit/8)
				nPeers = int(hitPeers[4:7].decode())
				toReadB = 60 + nBlock # Ip + stato

				if nPeers == 0:

					Util.printLog('No peer found...')
					exit()

				for peer in range(nPeers): # Per ogni peer

					infoPeer = c.s.recv(toReadB)
					readB = len(infoPeer)

					while(readB < toReadB):
						infoPeer += c.s.recv(toReadB - readB)
						readB = len(infoPeer)

					listPeers.append(infoPeer[:60].decode())			# Peer
					listStatus.append(list(infoPeer[60:]))	# Stato

				c.deconnection()

				# Creazione di una lista di parti pesata

				statusParts = [] # Lista dello stato delle parti

				for i in range(nBit):
					statusParts.append([i, 0, []]) # Parte, peso, ip

				for peer in range(nPeers):

					for block in range(nBlock):

						bit8 = listStatus[peer][block] # Isolo il blocco

						while bit8 > 0:

							maxBit = 7 - int(log(bit8,2)) # Indice del più alto bit impostato ad 1
							offset = 8 * block

							statusParts[maxBit + offset][1] += 1					# Aumento il peso
							statusParts[maxBit + offset][2].append(listPeers[peer])	# Inserisco l'ip

							bit8 = bit8 ^ (1 << (7 - maxBit)) # Elimino il bit utilizzato

				shuffle(statusParts) # Mescolo la lista (scelta random delle parti col medesimo peso)

				statusParts = [[part[0], part[2]] for part in sorted(statusParts,key=itemgetter(1))] # Riordino della lista dalla parte più rara (rarest first)

				if not controllerIsAlive:

					Util.printLog('DOWNLOAD ATTIVATO')
					controllerIsAlive = True

					idPartOne = idRec - (nBit - 1) # Id del primo rettagolo
					t = D(statusParts, queue, descriptor, idPartOne, infoFile, lenpart, md5, dCond, b, b2)
					t.start()

				else:

					if t.is_alive():

						queue.put(statusParts)

					else:

						print('Terminato')
						exit()
			sleep(60)
