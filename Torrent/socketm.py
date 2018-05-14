import socket
import codecs
import math
from operator import itemgetter # Per il sorting
from random import shuffle
from Graphics import Graphics
import Util
from time import sleep

t = Graphics()
t.daemon = True
print(t.daemon)
t.start()

peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peersocket.bind(('', 3000))

peersocket.listen(20)

scorr = 0


print("IN ATTESA DI UNA RICHIESTA ")

other_peersocket, addr = peersocket.accept()
byte = []

nBlock = int(other_peersocket.recv(3).decode())
nBit = int(other_peersocket.recv(3).decode())
nPeers = int(other_peersocket.recv(3).decode())

statusParts = [] # Dizionario delle parti inizializzato
for i in range(nBit):
	statusParts.append([i,0])

by = 0
var = ''
while by < nBlock * nPeers:
	var += codecs.decode(other_peersocket.recv(nBlock * nPeers - by),'iso-8859-1')
	
	by = len(var)


other_peersocket.close()

######### CREO LA GRAFICA INIZIALE
num = 0

idPart = Util.w.create_rectangle(50+num, 50, 54+num, 100, fill="blue", width=1)
descriptor = 'File' + str(idPart)
num += 4
Util.w.addtag_withtag(descriptor,idPart)

for i in range(nBit - 1):

	Util.w.create_rectangle(50+num, 50, 54+num, 100, fill="red", width=1, tags=(descriptor))
	num += 4
'''
for el in range(1,201):
	x0, y0, x1, y1 = (Util.w.coords(el))
	Util.w.coords(el, x0, y0+50, x1, y1+50)
'''
sleep(4)

Util.w.move(descriptor, 0, 50)

#########

print(len(var),nPeers,nBit,nBlock)
for peer in range(nPeers): # Ciclo per ogni peer
	
	byte.append([])

	for block in range(nBlock): # Ciclo per ogni blocco di un singolo peer
		
		offset = peer * nBlock
		
		byte[peer].append(ord(var[block + offset])) # Blocchi trasformati in interi

print(byte)

for peer in range(nPeers):

	for block in range(nBlock):

		bit = int('{:08b}'.format(byte[peer][block])[::-1], 2) # Inverto i bit

		while bit > 0:

			maxBit = int(math.log(bit,2)) # Indice del più alto bit impostato ad 1
			offset = 8 * block

			statusParts[maxBit + offset][1] += 1

			bit = bit ^ (1 << maxBit) # Elimino il bit utilizzato

shuffle(statusParts)

statusParts = [part[0] for part in sorted(statusParts,key=itemgetter(1))]

print('status: ',statusParts)
if scorr == 0: # Init dello stato
	gStatus = statusParts
else: # Update dello stato
	toDelete = gStatus[:scorr]

	gStatus = toDelete + [part for part in statusParts if part not in toDelete] # Elimino le parti già scaricate dallo stato e gliele pre concateno
	print('delete: ',toDelete)
print('gstatu: ',gStatus)

while scorr != len(statusParts):
	Util.w.itemconfig(statusParts[scorr] + 1,fill='#00ff00',width=0)
	scorr +=1
	sleep(0.1)

print('Terminato')