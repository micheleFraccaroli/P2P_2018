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

nThread = 2

# Demone grafico

t = Graphics()
t.daemon = True
t.start()
'''
sleep(2)
idt=Util.w.create_text(10,10,text="Percentuale completamento: 0%",anchor='nw',tags='casa')
idt=Util.w.create_text(10,30,text="Percentuale completamento: 10%",anchor='nw',tags='casa')
idt=Util.w.create_text(10,50,text="Percentuale completamento: 0%",anchor='nw',tags='coso')
idt=Util.w.create_text(10,70,text="Percentuale completamento: 0%",anchor='nw',tags='coso')
idt=Util.w.create_text(10,90,text="Percentuale completamento: 0%",anchor='nw',tags='cacca')
idt=Util.w.create_text(10,110,text="Percentuale completamento: 0%",anchor='nw',tags='cacca')



sleep(2)
Util.w.itemconfig(idt,text=str(Util.w.find_above('1')))
'''

# Thread del tracket che poduce lo stato di un file
t = Upload('127.0.0.1','::1',3500)
t.daemon = True
t.start()

input('Press to start thread...')

#q = LifoQueue()
status = [a for a in range(159)]
print(status)
shuffle(status)
#t = D( status, q, 'test', 200, 'baboon.png', 4096, 'qwertyuiopqwertyuiopqwertyuiopad')
t=RF('127.0.0.1','::1',3000)
t.start()
print('started...')

#q2 = LifoQueue()
status = [a for a in range(159)]
print(status)
shuffle(status)
#t = D( status, q, 'test', 200, 'baboon.png', 4096, 'qwertyuiopqwertyuiopqwertyuiopad')
t=RF('127.0.0.1','::1',3000)
t.start()
print('started...')

t.join()
print('uscito...')
sleep(10)
'''
for i in range(nThread):
	var = input('Lunghezza byte per ricerca numero ' + str(i+1) + ': ')
	t = RF(var)
	t.start()

while True:
	sleep(10)
'''