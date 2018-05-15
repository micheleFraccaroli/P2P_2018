from threading import *
from queue import *
import Util
from time import sleep
from random import uniform
from Conn import Conn
from curses import wrapper

class Worker(Thread):

	def __init__(self, part, workers, listChunk, fileName , missingParts, lock):

		Thread.__init__(self)
		self.part = part
		self.workers = workers
		self.wLock = lock
		self.listChunk = listChunk
		self.missingParts = missingParts

	def run(self):

		Util.w.itemconfig(self.part, fill='#0000ff', width=1)

		c = Conn(self.ipV4, self.ipV6, self.port)

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

	            self.listChunk.append(dataChunk) # Lista di chunk
	            c.deconnection()

	            if Path(fileName).is_file():

	            	res = wrapper(Util.menu,['Yes',True,'No',False],['The file requested already exists. Override it?'])

		            if res:
		                
		                os.remove(fileName)
		                file = open(fileName, "ab")

		                for chunk in self.listChunk:
		                    
		                    file.write(chunk)
		                
		                file.close()
		            
		            else:
		            	return

		else: # Fallita connessione al peer per scaricare la parte

			self.wLock.acquire()
			self.missingParts.append(self.part)
			self.wLock.release()




		Util.w.itemconfig(self.part, fill='#00ff00', width=1)

		self.wLock.acquire()
		self.workers[0] -= 1
		self.wLock.release()

		Util.dSem.release()
		
class D(Thread):

	def __init__(self, status, queue, tag, firstId):

		Thread.__init__(self)
		self.status = status 	# Stato del file
		self.pun = 0			# Indice di lettura (prossimo download)
		self.queue = queue		# Coda da cui ricavare lo stato aggiornato dopo FCHU
		self.tag = tag 			# Tag dell'elemento in download
		self.test = 0
		self.firstId = firstId	# Primo id della serie di rettangoli

	def moveToBottom(self):

		Util.lockGraphics.acquire()

		index = Util.rows.index(self.tag)
		Util.rows.append(self.tag)
		Util.rows.remove(self.tag)

		# Sposto tutti i file che erano sotto a quello spostato in fondo
		for el in Util.rows[index:]:

			Util.w.move(el, 0, 50)

		Util.lockGraphics.release()

	def run(self):
		
		workers = [0] # Numero di workers attivi
		wLock = Lock()
		missingParts = [] # Lista delle parti mancanti in caso di errori in download

		while self.pun < len(self.status):

			# Controllo aggiornamento status

			try:
			
				newStatus = self.queue.get(False) # Prelevo elemento dalla coda senza bloccarmi 

				toDelete = self.status[:self.scorr] # Parti già scaricate

				self.status = toDelete + [part for part in newStatus if part not in toDelete] # Elimino le parti già scaricate dallo stato e gliele pre concateno
					
			except Empty:

				pass # Mantengo stato attuale

			Util.dSem.acquire()

			t = Worker(self.status[self.pun] + self.firstId, workers, missingParts, wLock) # Istanza di download. Aggiungo 1 perchè gli id di tkinter partono da 1
			t.start()

			self.pun += 1 # Incremento puntatore al prossimo download

			wLock.acquire()
			workers[0] += 1
			wLock.release()
		# Download terminato, sposto il file scaricato in fondo alla lista

		flag = True
		while flag:	# Attendo che i thread abbiano terminato il download
			wLock.acquire()
			if workers[0] == 0:
				flag = False
			wLock.release()


		#self.moveToBottom()
