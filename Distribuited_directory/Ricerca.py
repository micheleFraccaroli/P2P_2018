import sys
import os
import socket
from Conn import Conn
import Util
from Retr import Retr
from Vicini import Vicini
from dataBase import dataBase
import random
import string
from time import time
from Config import *
import ipaddress as ipad
import threading as th
import random as ra

class Ricerca:
    def __init__(self, ipv4, ipv6, port, ttl, time_res, search):
    
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = port
        self.ttl = ttl
        self.time_res = time_res
        self.search = search

    def query(self, config):
        '''
        c = Config()
        db = dataBase()
        db.destroy()
        db.create(c)
        '''

        pktid = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(16))
        
        ipp2p_pp2p = Util.ip_formatting(self.ipv4, self.ipv6, self.port)
        
        # richiesta vicini
        near = Vicini(config)

        # thread per ascolto di riposta dei vicini
        '''
        Qua metti il thread che ascolta tutti gli "ANEA" che arrivano dai vicini
        mettendolo in join.
        Il thread sarà una specie di unione del thread di livello uno e due (dei file Retr.py e Response.py)
        in modo che rimanga in ascolto per n secondi per aspettare che tutti i vicini rispondano e poi li scriva sul
        DB.
        '''

        near.searchNeighborhood() # partenza richiesta dei vicini
        
        db.insertRequest(pktid, ipp2p_pp2p[:55], ipp2p_pp2p[55:], time())
        self.research = "QUER" + pktid + ipp2p_pp2p + str(self.ttl).zfill(2) + self.search

        self.neighbors = db.retrieveNeighborhood()
        print(self.neighbors)
        #self.neighbors = [['127.000.000.002|0000:0000:0000:0000:0000:0000:0000:0001',3000,2],['127.000.000.003|0000:0000:0000:0000:0000:0000:0000:0001',3001,2]]
        #sending query to roots and neighbors
        retr = Retr('172.16.8.3', self.port)
        retr.start()
        
        for n in self.neighbors:
            addr = Util.ip_deformatting(n[0], n[1], self.ttl)
            print(addr[0])
            #ip4 = ipad.ip_address(n[0][:15])
            ip6 = ipad.ip_address(n[0][16:])
            

            self.con = Conn(addr[0], str(ip6), addr[2])
            try:
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
    print("IO SONO QUI ")

    search = input("Inserisci file da cercare: ")
    porta2 = ra.randint(50000, 59999)
    src2 = Ricerca('172.16.8.3', 'fc00::8:3', porta2, 1, 300, search)
    pkid2 = src2.query()
    #retr = Retr('172.16.8.3', 50004)
    #retr.start()
    print("IO SONO QUI ANCORA")