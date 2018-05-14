from threading import *
from queue import *
import Util
from time import sleep
from random import uniform

class Worker(Thread):

	def __init__(self, part, workers, lock):

		Thread.__init__(self)
		self.part = part
		self.workers = workers
		self.wLock = lock

	def run(self):

		Util.w.itemconfig(self.part, fill='#0000ff', width=1)
		sleep(uniform(0.2,1))
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

		while self.pun < len(self.status):

			# Controllo aggiornamento status

			try:
			
				newStatus = self.queue.get(False) # Prelevo elemento dalla coda senza bloccarmi 

				toDelete = self.status[:self.scorr] # Parti già scaricate

				self.status = toDelete + [part for part in newStatus if part not in toDelete] # Elimino le parti già scaricate dallo stato e gliele pre concateno
					
			except Empty:

				pass # Mantengo stato attuale
			Util.dSem.acquire()
			print(len(self.status))
			t = Worker(self.status[self.pun] + self.firstId, workers, wLock) # Istanza di download. Aggiungo 1 perchè gli id di tkinter partono da 1
			t.start()
			self.pun += 1 # Incremento puntatore al prossimo download

			wLock.acquire()
			workers[0] += 1
			wLock.release()
		# Download terminato, sposto il file scaricato in fondo alla lista

		flag = True
		while flag:
			wLock.acquire()
			if workers[0] == 0:
				flag = False
			wLock.release()


		#self.moveToBottom()
