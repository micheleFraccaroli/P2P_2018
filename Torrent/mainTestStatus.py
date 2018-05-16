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

nThread = 1

# Demone grafico
'''
t = Graphics()
t.daemon = True
print(t.daemon)
t.start()
'''
# Thread del tracket che poduce lo stato di un file
#t = Track()
#t.start()

input('Press to start thread...')
q = LifoQueue()
t = D( [0,6,5,4,3,2,1,9,7,8], q, 'test', 200, 'carudio.jpg', 200)
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