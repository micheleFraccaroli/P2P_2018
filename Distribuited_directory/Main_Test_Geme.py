from Conn import Conn
import string
import random

print('inizio invio')
Conn = Conn('127.0.0.1', '::1', 50004)
Conn.connection()
#pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
pktid = 'COR3BEWPI98CHFOI'
ip = '172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004'
door = '50004'
ttl = '02'
ricerca = 'CrAs'
ricerca_20 = ricerca.ljust(20,' ')
string_request = "QUER"+pktid+ip+door+ttl+ricerca_20
print(string_request+"\n")
Conn.s.send(string_request.encode())
while True:
	first_packet = Conn.s.recv(212)
	print("sono qua\n")
	bytes_read_f = len(first_packet)
	while (bytes_read_f < 212):
		first_packet += Conn.s.recv(212 - bytes_read_f)
		bytes_read_f = len(first_packet)	
	print(first_packet.decode())
Conn.deconnection()