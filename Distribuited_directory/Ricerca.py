import sys
import os
import socket
from Conn import Conn

class Ricerca:
    def __init__(self, neighbors, ipv4, ipv6, port, ttl, time_res, search):
        self.neighbors = neighbors
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = port
        self.ttl = ttl
        self.time_res = time_res
        self.search = search

    def query(self):
        pktid = int.from_bytes(os.urandom(16), byteorfer='little')
        ipp2p, pp2p = ip_formatting()
        self.research = "QUER" + ipp2p + pp2p + self.ttl + self.search

        #sending query to roots
        for n in self.neighbors:
            self.con = Conn(n[0], n[1], n[2])
            try:
                self.con.connection()
                self.con.s.send(self.research.encode('ascii'))
                self.con.deconnection()
            except IOError as expt:
                print("Errore di connessione")
                print(expt)
                sys.exit(0)
        
        return pktid