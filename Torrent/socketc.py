from Conn import Conn
import codecs
from math import *
import sys

totalBit = int(sys.argv[1])
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

byte.append(128)
byte.append(128)
byte.append(0)
print(byte)

c = Conn('127.0.0.1','::1',3000)

box = ceil(tot/8)

c.connection()
c.s.send(str(box).zfill(3).encode())
c.s.send(str(tot).zfill(3).encode())
c.s.send(str(len(byte)//box).zfill(3).encode())
for el in byte:

	charAscii = chr(el)

	c.s.send(codecs.encode(charAscii,'iso-8859-1'))

c.deconnection()