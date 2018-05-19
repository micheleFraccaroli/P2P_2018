import socket
import codecs
import math
from operator import itemgetter # Per il sorting
from random import shuffle
from Graphics import Graphics
import Util
from time import sleep
from Track import Track
from RF import RF
from queue import *
from D import D
from Upload import Upload
from random import shuffle

nThread = 1

# Demone grafico

t = Graphics()
t.daemon = True
#print(t.daemon)
t.start()

# Thread del tracket che poduce lo stato di un file
t = Upload('127.0.0.1','::1',3500)
t.daemon = True
t.start()

input('Press to start thread...')
q = LifoQueue()
status = [a for a in range(159)]
print(status)
shuffle(status)
#t = D( status, q, 'test', 200, 'baboon.png', 4096, 'qwertyuiopqwertyuiopqwertyuiopad')
t=RF('127.0.0.1','::1',3000)
t.start()
print('started...')
t.join()
'''
for i in range(nThread):
	var = input('Lunghezza byte per ricerca numero ' + str(i+1) + ': ')
	t = RF(var)
	t.start()

while True:
	sleep(10)
'''