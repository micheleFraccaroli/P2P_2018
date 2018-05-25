from Conn import Conn
import codecs
from math import *
import sys

def partList_gen(totalBit, flag): # flag = 255 o 0
	byte = []

	# Blocchi completi
	while totalBit >= 8:
		byte.append(flag)
		totalBit -= 8
	
	# Blocco incompleto (finale)
	if totalBit > 0:
		if(flag == 0):
			byte.append(0)
		else:
			lastBlock = (1 << totalBit) - 1
			byte.append(int('{:08b}'.format(lastBlock)[::-1], 2))

	return byte