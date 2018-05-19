from threading import *
from queue import *
import Util
from time import sleep
from random import uniform
from Conn import Conn
from curses import wrapper

class Worker(Thread):

	def __init__(self, idRect, part, workers, fileName, fileDescriptor, lenPart, listPeers , missingParts, md5, wLock, fLock):

		Thread.__init__(self)
		self.idRect = idRect					# Id del rettangolo grafico
		self.part = part 						# Numero della parte da scaricare
		self.workers = workers					# Numero di worker attivi
		self.fileDescriptor = fileDescriptor	# Descrittore del file in scrittura
		self.fileName = fileName 				# Nome del file
		self.lenPart = lenPart					# Lunghezza di una parte in byte
		self.listPeers = listPeers				# Lista dei peers disponibili per la parte
		self.missingParts = missingParts		# Parti impossibili da scaricare
		self.md5 = md5 							# MD5 del file
		self.wLock = wLock 						# Lock sulle variabili globali
		self.fLock = fLock 						# Lock sulle operazioni del file

	def run(self):

		#Util.w.itemconfig(self.idRect, fill='#0000ff', width=1)

		jobDone = False
		for peer in self.listPeers:

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

	            # if Path(fileName).is_file():

	            # 	res = wrapper(Util.menu,['Yes',True,'No',False],['The file requested already exists. Override it?'])

		           #  if res:
		                
		           #      os.remove(fileName)
		           #      file = open(fileName, "ab")

		           #      for chunk in self.listChunk:
		                    
		           #          file.write(chunk)
		                
		           #      file.close()
		            
		           #  else:
		           #  	return

		if jobDone:

			pass#Util.w.itemconfig(self.part, fill='#00ff00', width=1)

		else: # Fallita connessione al peer per scaricare la parte

			#Util.w.itemconfig(self.part, fill='#ff0000', width=1)
			
			self.wLock.acquire()
			self.missingParts.append(self.part - 1)
			print('job failed for :',current_thread())
			self.wLock.release()

		self.wLock.acquire()

		self.workers[0] -= 1
		
		self.wLock.release()
		Util.dSem.release()
		
class D(Thread):

	def __init__(self, status, queue, tag, firstId, fileName, lenPart, md5):

		Thread.__init__(self)
		self.status = status 		# Stato del file
		self.pun = 0				# Indice di lettura (prossimo download)
		self.queue = queue			# Coda da cui ricavare lo stato aggiornato dopo FCHU
		self.tag = tag 				# Tag dell'elemento in download
		self.firstId = firstId		# Primo id della serie di rettangoli
		self.fileName = fileName 	# Nome del file
		self.lenPart = lenPart		# Lunghezza della parte
		self.md5 = md5				# MD5 del file

	def moveToBottom(self):

		Util.lockGraphics.acquire()

		index = Util.rows.index(self.tag)
		Util.rows.append(self.tag)
		Util.rows.remove(self.tag)

		# Sposto tutti i file che erano sotto a quello spostato in fondo
		for el in Util.rows[index:]:

			Util.w.move(el, 0, 50)

		Util.lockGraphics.release()

	def spawnWorker(self, workers, f, missingParts, wLock, fLock):

		while self.pun < len(self.status):

			# Controllo aggiornamento status

			try:
			
				newStatus = self.queue.get(False) # Prelevo elemento dalla coda senza bloccarmi 

				toDelete = self.status[:self.scorr] # Parti già scaricate

				self.status = toDelete + [part for part in newStatus if part not in toDelete] # Elimino le parti già scaricate dallo stato e gliele pre concateno
					
			except Empty:

				pass # Mantengo stato attuale

			Util.dSem.acquire()
			from random import random
			if int(random()*100<60):
				port=3500
			else:
				port=5000
			t = Worker(self.status[self.pun] + self.firstId, self.status[self.pun] + 1, workers, self.fileName, f, self.lenPart, [['127.0.0.1','::1',port]], missingParts, self.md5, wLock, fLock) # Istanza di download. Aggiungo 1 perchè gli id di tkinter partono da 1
			t.start()

			self.pun += 1 # Incremento puntatore al prossimo download
			wLock.acquire()
			workers[0] += 1
			wLock.release()
		
		# Download terminato, attendo che i worker abbiano finito
		
		flag = True;
		while flag:	# Attendo che i thread abbiano terminato il download

			wLock.acquire()
			if workers[0] == 0:
				flag = False
			wLock.release()

	def run(self):
		
		workers = [0] # Numero di workers attivi
		wLock = Lock()
		fLock = Lock()
		missingParts = [] # Lista delle parti mancanti in caso di errori in download

		f = open('Files/copia-' + self.fileName, "wb") # Apro il file, pronto per scrivere
		
		self.spawnWorker(workers, f, missingParts, wLock, fLock)

		# Se al termine del download ci sono parti che non ho potuto scaricare
		# tento di riscaricarle

		while len(missingParts) != 0:
			
			self.status = [part for part in self.status if part not in missingParts] + missingParts # Riordino l stato mettendo le parti mancanti alla fine
			self.pun = len(self.status) - len(missingParts) # Indice del lla prima parte mancante
			missingParts = [] # Risetto la lista delle parte mancanti per il prossimo ciclo
			sleep(4) # Attendo 10 seondi prima di ricominciare il download
			self.spawnWorker(workers, f, missingParts, wLock, fLock)

		print('Terminato!')
		f.close()
		exit()