from Conn import Conn
import string
import random
import socket
from Download import Download

print('avvio main')
'''
Conn = Conn('127.0.0.1', '::1', 50004)
Conn.connection()

#pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
pktid = 'COR3BEWPI98CHFOP'
ip = '172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004'
door = '50004'
ttl = '02'
ricerca = 'CrAs'
ricerca_20 = ricerca.ljust(20,' ')
string_request = "QUER"+pktid+ip+door+ttl+ricerca_20
print(string_request+"\n")
'''

peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peersocket.bind(('', 50004))

peersocket.listen(10)

	
other_peersocket, addr = peersocket.accept()
from_peer = other_peersocket.recv(212)
bytes_read_f = len(from_peer)
while (bytes_read_f < 212):
	print('sono qua\n')
	from_peer += other_peersocket.recv(212 - bytes_read_f)
	bytes_read_f = len(from_peer)	
print(from_peer.decode())

'''
down = Download('127.0.0.1', '::1', '50009', '1c3f60a268cd166d867f34196f1b985c', 'wewe')
down.download()
'''