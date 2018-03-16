import socket

class Conn:
    def __init__(self,ip, port):
        self.ipp2p = ip
        self.pp2p = port

    def connection(self):
        try:
            # this is for ipv4 and ipv6
            self.infoS = socket.getaddrinfo(self.ipp2p, self.pp2p)
            self.s = socket.socket(*self.infoS[0][:3])
            self.s.connect(self.infoS[0][4])

        except IOError as expt:
            print (expt)

    def deconnection(self):
        try:
            self.s.close()
        except IOError as expt:
            print (expt)