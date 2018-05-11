from Conn import Conn
import codecs
from math import *
import sys

'''
due parametri in ingresso: totalbit e flag che dev essere 255 o 0 e da mettere a linea 15 al posto del 255
'''
totalBit = int(sys.argv[1]) # divisione tra lunghezza del file e lunghezza delle parti
byte = []

# Blocchi completi
while totalBit >= 8:

	byte.append(255) # parametrizzare questo
	totalBit -= 8

# Blocco incompleto (finale)
if totalBit > 0:
	
	lastBlock = (1 << totalBit) - 1

	byte.append(int('{:08b}'.format(lastBlock)[::-1], 2))
#test
'''
byte.append(128)
byte.append(128)
byte.append(0)
print(byte)

c = Conn('127.0.0.1','::1',3000)

c.connection()

for el in byte:

	charAscii = chr(el)

	c.s.send(codecs.encode(charAscii,'iso-8859-1'))

c.deconnection()
'''