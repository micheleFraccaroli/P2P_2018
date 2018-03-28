import socket
from Conn import Conn
import ipaddress as ipa
import Util

peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peersocket.bind(('', 50004))

peersocket.listen(5)

while True:
    other_peersocket, addr = peersocket.accept()

    res = other_peersocket.recv(102)
    if(res[:4].decode() == "QUER"):
        print("--- From original project ---")
        print(res[4:20].decode())
        print(res[20:80].decode())
        print(res[80:82].decode())

    ipp = Util.ip_deformatting(res[20:75].decode(),res[75:80].decode(),None)
    #print("\n\n")
    
   # print(int(res[75:80]))

    #con = Conn(str(ipa.ip_address(ippp[0])), str(ipa.ip_address(ippp[1])), int(res[75:80]))
    con = Conn(ipp[0], ipp[1], ipp[2])
    
    con.connection()
    filename = 'file.jpg' + ((100-8)*' ')
    
    risposta = "AQUE" + res[4:20].decode() + res[20:80].decode() + res[80:82].decode() + "qwertyhgfdsaq1234567ytgyt67890oi" + filename
    print(risposta)
    con.s.send(risposta.encode())

    con.deconnection()