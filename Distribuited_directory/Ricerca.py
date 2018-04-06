import sys
import os
import socket
import Util
import string
import random
import ipaddress as ipad
import threading as th
import random as ra
import time
from Conn import Conn
from Retr import Retr
from Vicini import Vicini
from dataBase import dataBase
from Vicini_res import Vicini_res
from Config import *

class Ricerca:
    def __init__(self, ipv4, ipv6, port, ttl, time_res, search, lock):
        self.lock =  lock
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = port
        self.ttl = ttl
        self.time_res = time_res
        self.search = search

    def query(self, config):

        db = dataBase()
        pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
        
        ipp2p_pp2p = Util.ip_formatting(self.ipv4, self.ipv6, self.port)
        
        # richiesta vicini
        near = Vicini(config)
        # thread per ascolto di riposta dei vicini
        
        th_near = Vicini_res(self.port, self.lock)
        th_near.start()
        # partenza richiesta dei vicini
        near.searchNeighborhood()
        th_near.join()
        
        db.insertRequest(pktid, ipp2p_pp2p[:55], time.time())

        self.research = "QUER" + pktid + ipp2p_pp2p + str(self.ttl).zfill(2) + (self.search+(' '*(20-len(self.search))))

        # retrieve neighbors from database
        self.neighbors = db.retrieveNeighborhood()
        
        #thread in ascolto per ogni ricerca
        retr = Retr(self.port, config, self.lock)
        retr.start()

        #sending query to roots and neighbors
        for n in self.neighbors:
            addr = Util.ip_deformatting(n[0], n[1], self.ttl)
            
            #ip4 = ipad.ip_address(n[0][:15])
            ip6 = ipad.ip_address(n[0][16:])

            self.con = Conn(addr[0], str(ip6), addr[2])
            try:
                Util.printLog("QUER --------------------------------")
                Util.printLog(self.research)
                Util.printLog(str(len(self.research)))
                Util.printLog(addr[0])
                Util.printLog("-------------------------------------")
                self.con.connection()
                self.con.s.send(self.research.encode())
                self.con.deconnection()
            except IOError as expt:
                print("Errore di connessione")
                print(expt)
                sys.exit(0)
        
        del db
        return pktid


if __name__ == '__main__':
    search = input("Inserisci file da cercare: ")
    porta1 = ra.randint(50000, 59999)
    src1 = Ricerca('172.16.8.3', 'fc00::8:3', porta1, 1, 300, search)
    pkid = src1.query()

    #retr = Retr('172.16.8.3', 50003)
    #retr.start()
    print("--- fine prima ricerca ---")

    search = input("Inserisci file da cercare: ")
    porta2 = ra.randint(50000, 59999)
    src2 = Ricerca('172.16.8.3', 'fc00::8:3', porta2, 1, 300, search)
    pkid2 = src2.query()
    #retr = Retr('172.16.8.3', 50004)
    #retr.start()
    print("--- fine seconda ricerca ---")