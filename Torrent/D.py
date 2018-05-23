from threading import *
from queue import *
import Util
from time import sleep
from random import uniform
from Conn import Conn
from curses import wrapper

class Worker(Thread):

	def __init__(self, idRect, part, data, fileName, fileDescriptor, lenPart, listPeers , missingParts, md5, tag, wLock, fLock):

		Thread.__init__(self)
		self.idRect = idRect					# Id del rettangolo grafico
		self.part = part 						# Numero della parte da scaricare
		self.data = data						# Dati condivisi
		self.fileDescriptor = fileDescriptor	# Descrittore del file in scrittura
		self.fileName = fileName 				# Nome del file
		self.lenPart = lenPart					# Lunghezza di una parte in byte
		self.listPeers = listPeers				# Lista dei peers disponibili per la parte
		self.missingParts = missingParts		# Parti impossibili da scaricare
		self.md5 = md5 							# MD5 del file
		self.tag = tag 							# Tag del file
		self.wLock = wLock 						# Lock sulle variabili globali
		self.fLock = fLock 						# Lock sulle operazioni del file

	def run(self):

		Util.w.itemconfig(self.idRect, fill='#0000ff', width=1)
		
		jobDone = False
		for peers in self.listPeers:

			peer = Util.ip_deformatting(peers[:55],peers[55:])

			c = Conn(peer[0], peer[1], peer[2]) # ipv4 ipv6 port

			if c.connection():

				packet = 'RETP' + self.md5 + str(self.part).zfill(8) # Preparo il pacchetto RETP

				c.s.send(packet.encode()) # Invio richiesta download

				# Lettura della risposta

				nChunk = c.s.recv(10) # 'AREP' + n° chunks

				readB = len(nChunk)
				while (readB < 10):

					nChunk += c.s.recv(10 - readB)
					readB = len(nChunk)

				nChunk = int(nChunk[4:].decode())

				# Elaborazione dei chunk
				self.fLock.acquire()

				self.fileDescriptor.seek(self.lenPart * (self.part - 1)) # Sposto il puntatore nell'area corretta
				
				for _ in range(nChunk):

					# Estrazione lunghezza chunk

					lenChunk = c.s.recv(5)

					readB = len(lenChunk)
					while (readB < 5):
						lenChunk += c.s.recv(5 - readB)
						readB = len(lenChunk)

					lenChunk = int(lenChunk.decode())

					# Estrazione dati chunk

					dataChunk = c.s.recv(lenChunk)

					readB = len(dataChunk)
					while (readB < lenChunk):
						
						dataChunk += c.s.recv(lenChunk - readB)
						readB = len(dataChunk)
					self.fileDescriptor.write(dataChunk) # Scrivo il chunk su file

				self.fLock.release()
				c.deconnection()
				jobDone = True
				break

		if jobDone: # Job completato
			sleep(uniform(0.5,1))
			self.wLock.acquire()
			self.data['downloadedParts'] += 1
			self.wLock.release()

			percent, parts = Util.w.find_withtag(self.tag)[-3:-1] # Terzultimo e penultimo

			Util.w.itemconfig(percent, text='Progress: \t\t' + '{0:.2f}'.format(self.data['downloadedParts'] / self.data['totalParts'] * 100) + '%')
			Util.w.itemconfig(parts, text='Downloaded: \t' + str(self.data['downloadedParts']))
			Util.w.itemconfig(self.idRect, fill='#00ff00', width=1)

		else: # Fallita connessione al peer per scaricare la parte

			Util.w.itemconfig(self.idRect, fill='#ff0000', width=1)
			
			self.wLock.acquire()
			self.missingParts.append(self.part - 1)
			print('job failed for :',current_thread())
			self.wLock.release()

		self.wLock.acquire()
		self.data['workers'] -= 1
		self.wLock.release()
		Util.dSem.release()
		
class D(Thread):

	def __init__(self, status, queue, tag, firstId, fileName, lenPart, md5, dCond, b1, b2):

		Thread.__init__(self)
		self.status = status 		# Stato del file [indice parte, [ip]]
		self.pun = 0				# Indice di lettura (prossimo download)
		self.queue = queue			# Coda da cui ricavare lo stato aggiornato dopo FCHU
		self.tag = tag 				# Tag dell'elemento in download
		self.firstId = firstId		# Primo id della serie di rettangoli
		self.fileName = fileName 	# Nome del file
		self.lenPart = lenPart		# Lunghezza della parte
		self.md5 = md5				# MD5 del file
		self.cond = dCond			# Condizione per stoppare il download
		self.b1 = b1				# Buttone pause&play
		self.b2 = b2				# Buttone stop

	def removeGraphic(self):

		Util.lockGraphics.acquire()
		print('                  ',self.tag)
		index = Util.rows.index(self.tag)

		#Util.rows.append(self.tag)
		#Util.rows.remove(self.tag)

		Util.w.delete(self.tag)
		self.b1.destroy()
		self.b2.destroy()

		# Sposto tutti i file che erano sotto a quello eliminato
		ind = index + 1
		for el in Util.rows[index + 1:]:

			Util.w.move(el, 0,- Util.heightRow)
			
			b1, b2 = Util.buttonsList[ind]
			
			infoB1 = b1.place_info()
			infoB2 = b1.place_info()

			b1.place(y=int(infoB1['y']) - Util.heightRow)
			b2.place(y=int(infoB2['y']) - Util.heightRow)
			
			ind += 1

		Util.buttonsList.remove(Util.buttonsList[index])
		Util.rows.remove(self.tag)
		Util.lockGraphics.release()

	def spawnWorker(self, data, f, missingParts, wLock, fLock):

		while self.pun < len(self.status):

			# Controllo aggiornamento status
			newStatus = None
			try:
			
				newStatus = self.queue.get(False) # Prelevo elemento dalla coda senza bloccarmi 

				if type(newStatus) != str:
					print('UPDATE')
					toDelete = self.status[:self.pun] # Parti già scaricate

					self.status = toDelete + [part for part in newStatus if part not in toDelete] # Elimino le parti già scaricate dallo stato e gliele pre concateno
					
			except Empty:

				pass # Mantengo stato attuale
			
			if newStatus == 'stop':
				
				flag = True;
				while flag:	# Attendo che i thread abbiano terminato il download

					wLock.acquire()
					if data['workers'] == 0:
						flag = False
					wLock.release()

				self.removeGraphic()
				
				exit()

			elif newStatus == 'pause':

				self.cond.acquire()
				self.cond.wait()
				self.cond.release()

			else:

				Util.dSem.acquire()
				print(self.status[self.pun][0] + self.firstId);sleep(4)
				t = Worker(self.status[self.pun][0] + self.firstId, self.status[self.pun][0] + 1, data, self.fileName, f, self.lenPart, self.status[self.pun][1], missingParts, self.md5, self.tag, wLock, fLock) # Istanza di download. Aggiungo 1 perchè gli id di tkinter partono da 1
				t.start()

				self.pun += 1 # Incremento puntatore al prossimo download
				
				wLock.acquire()
				data['workers'] += 1
				wLock.release()
		
		# Download terminato, attendo che i worker abbiano finito
		
		flag = True;
		while flag:	# Attendo che i thread abbiano terminato il download

			wLock.acquire()
			if data['workers'] == 0:
				flag = False
			wLock.release()

	def run(self):
		
		data={}
		data['workers'] = 0 					# Numero di workers attivi
		data['totalParts'] = len(self.status)	# Numero totali di parti
		data['downloadedParts'] = 0				# Numero di parti scaricate

		wLock = Lock()
		fLock = Lock()
		missingParts = [] # Lista delle parti mancanti in caso di errori in download

		f = open(self.fileName, "wb") # Apro il file, pronto per scrivere
		
		self.spawnWorker(data, f, missingParts, wLock, fLock)

		# Se al termine del download ci sono parti che non ho potuto scaricare
		# tento di riscaricarle

		while len(missingParts) != 0:
			
			self.status = [part for part in self.status if part not in missingParts] + missingParts # Riordino l stato mettendo le parti mancanti alla fine
			self.pun = len(self.status) - len(missingParts) # Indice del lla prima parte mancante
			missingParts = [] 	# Risetto la lista delle parte mancanti per il prossimo ciclo
			sleep(4) 			# Attendo 10 seondi prima di ricominciare il download
			self.spawnWorker(data, f, missingParts, wLock, fLock)

		print('Terminato!')
		f.close()
		exit()