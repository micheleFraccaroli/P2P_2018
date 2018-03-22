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

    def ip_formatting(self):
        # formattazione ipv4
        self.split_ip_4 = self.ipv4.split(".")
        ip1_4 = self.split_ip_4[0].zfill(3)
        ip2_4 = self.split_ip_4[1].zfill(3)
        ip3_4 = self.split_ip_4[2].zfill(3)
        ip4_4 = self.split_ip_4[3].zfill(3)

        # formattazione ipv6
        self.split_ip_6 = self.ipv6.split(":")
        ip1_6 = self.split_ip_6[0].zfill(4)
        ip2_6 = self.split_ip_6[1].zfill(4)
        ip3_6 = self.split_ip_6[2].zfill(4)
        ip4_6 = self.split_ip_6[3].zfill(4)
        ip5_6 = self.split_ip_6[4].zfill(4)
        ip6_6 = self.split_ip_6[5].zfill(4)
        ip7_6 = self.split_ip_6[6].zfill(4)
        ip8_6 = self.split_ip_6[7].zfill(4)

        ipp2p = ip1_4 + '.' + ip2_4 + '.' + ip3_4 + '.' + ip4_4 + '|' + ip1_6 + ':' + ip2_6 + ':' + ip3_6 + ':' + ip4_6 + ':' + ip5_6 + ':' + ip6_6 + ':' + ip7_6 + ':' + ip8_6 
        
        # formattazione porta
        pp2p = '%(#)05d' % {"#": int(self.port)}

        return ipp2p, pp2p

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