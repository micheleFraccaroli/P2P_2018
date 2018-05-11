import socket
import codecs
import math

peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peersocket.bind(('', 3000))

peersocket.listen(20)

print("IN ATTESA DI UNA RICHIESTA ")

other_peersocket, addr = peersocket.accept()
byte = []

nBlock = 3
nBit = 20
nPeers = 2

statusParts = {} # Dizionario delle parti inizializzato
for i in range(nBit):
	statusParts[i] = 0

var = other_peersocket.recv(nBlock * nPeers)
other_peersocket.close()

var = codecs.decode(var,'iso-8859-1') # Decodifica in caratteri ASCII

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

			statusParts[maxBit + offset] += 1

			bit = bit ^ (1 << maxBit) # Elimino il bit utilizzato

print(statusParts)