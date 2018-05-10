import socket
import random

class Conn:
    def __init__(self, ipv4, ipv6, port):
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.pp2p = port

    def ip_choice(self, a,b):
        prob = random.random()
        if(prob < 0.5):
            return a
        else:
            return b

    def connection(self):
    
        # this is for ipv4 and ipv6
            
        ip = self.ip_choice(0,1) #se 0:ipv4 altrimenti 1:ipv6

        if(ip == 1):
            self.ipp2p = self.ipv6
        else:
            self.ipp2p = self.ipv4

        try:        
            self.infoS = socket.getaddrinfo(self.ipp2p, self.pp2p)
            self.s = socket.socket(*self.infoS[0][:3])
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#            self.s.setblocking(0)
            self.s.connect(self.infoS[0][4])

        except IOError as e:
            print(e)
            return False
        
        else:
            return True

    def deconnection(self):
        try:
            self.s.close()
        except IOError as expt:
            print (expt)