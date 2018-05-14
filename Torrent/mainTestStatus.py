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

nThread = 6

# Demone grafico
t = Graphics()
t.daemon = True
print(t.daemon)
t.start()

# Thread del tracket che poduce lo stato di un file
t = Track()
t.start()

for i in range(nThread):
	var = input('Lunghezza byte per ricerca numero ' + str(i+1) + ': ')
	t = RF(var)
	t.start()

while True:
	sleep(10)