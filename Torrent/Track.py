from threading import *
from Conn import Conn
import codecs
from math import *
import sys

class Track(Thread):

	def __init__(self):

		Thread.__init__(self)

	def run(self):

		c = Conn(port=3000)
		peersocket = c.initializeSocket()

		while True:

			other_peersocket, addr = peersocket.accept()

			totalBit = int(other_peersocket.recv(8).decode())

			tot = totalBit
			byte = []
		
			# Blocchi completi
			while totalBit >= 8:

				byte.append(255)
				totalBit -= 8

			# Blocco incompleto (finale)
			if totalBit > 0:
				
				lastBlock = (1 << totalBit) - 1

				byte.append(int('{:08b}'.format(lastBlock)[::-1], 2))

			###################

			# INSERISCI QUI ALTRI BLOCCHI PER POTER AVERE PESI DIVERSI

			###################

			box = ceil(tot/8)
			print('peers pronti: ',str(len(byte)//box).zfill(5))
			other_peersocket.send(str(box).zfill(8).encode()) 			# Numero blocchi
			other_peersocket.send(str(tot).zfill(8).encode()) 			# Numero bit
			other_peersocket.send(str(len(byte)//box).zfill(8).encode())	# Numero peers
			
			charAscii = ''
			for el in byte:

				charAscii = charAscii + chr(el)

			a = other_peersocket.send(codecs.encode(charAscii,'iso-8859-1'))
			print('scritto: ',a)
			other_peersocket.close()