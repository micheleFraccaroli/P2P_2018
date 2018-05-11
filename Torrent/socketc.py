from Conn import Conn
import codecs
from math import *
import sys

'''
c = Conn('127.0.0.1','::1',3000)

c.connection()
a = ['00000001','11111111','11110000','00001111']
##### int(log(value,2)) potenza massima da controllare

c.s.send('fracca'.encode())
for el in a:

	charAscii = chr(int(el,2))

	c.s.send(codecs.encode(charAscii,'iso-8859-1'))
c.s.send('geme'.encode())
c.deconnection()
'''

totalBit = int(sys.argv[1])
byte = []

# Blocchi completi
while totalBit >= 8:

	byte.append(255)
	totalBit -= 8

# Blocco incompleto (finale)
if totalBit > 0:
	
	lastBlock = (1 << totalBit) - 1

	byte.append(int('{:08b}'.format(lastBlock)[::-1], 2))

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