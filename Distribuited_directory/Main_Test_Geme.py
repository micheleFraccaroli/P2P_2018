from Conn import Conn
import string
import random

print('inizio invio')
Conn = Conn('127.0.0.1', '::1', 50004)
Conn.connection()
#pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
pktid = 'COR3BEWPI98CHFON'
ip = '172.016.008.004|fc00:0000:0000:0000:0000:0000:0008:0004'
door = '50004'
ttl = '02'
ricerca = 'immaginecondimension'
string_request = "QUER"+pktid+ip+door+ttl+ricerca
print(string_request)
Conn.s.send(string_request.encode())
Conn.deconnection()