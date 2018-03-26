import sys
import os
import socket
from Conn import Conn
import Util
from Retr import Retr
import random
import string

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
        pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
        ipp2p_pp2p = Util.ip_formatting(self.ipv4, self.ipv6, self.port)
        self.research = "QUER" + pktid + ipp2p_pp2p + str(self.ttl).zfill(2) + self.search


        print(self.neighbors)
        #sending query to roots
        for n in self.neighbors:
            self.con = Conn(n[0], n[1], n[2])
            try:
                self.con.connection()
                self.con.s.send(self.research.encode())
                self.con.deconnection()
            except IOError as expt:
                print("Errore di connessione")
                print(expt)
                sys.exit(0)
        
        return pktid

if __name__ == '__main__':
    Util.define_g()
    l = [['127.0.0.2', '::1', 3000], ['127.0.0.3', '::1', 3003]]
    search = input("Inserisci file da cercare: ")
    src1 = Ricerca(l, '127.0.0.1', '::1', 50003, 1, 10, search)
    src2 = Ricerca(l, '127.0.0.1', '::1', 50003, 1, 10, search)
    pkid = src1.query()
    pkid2 = src2.query()

    print(pkid)
    print(pkid2)
    Util.diz[str(pkid)] = []
    Util.diz[str(pkid2)] = []

    print(Util.diz)

    retr = Retr('127.0.0.1', 50003)
    retr.spawn_thread()