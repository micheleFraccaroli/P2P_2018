import socket
import Util
import sys
import math
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
import threading as th
import partList_gen as pL

#thread che si occupa della gestione dell'aggiunta di un file proveniente da un peer

class t_addr(th.Thread):
    def __init__(self, socket):
        th.Thread.__init__(self)
        self.socket = socket
        self.list = [] # lista per dizionario globale

    def run(self):
        self.addr_pkt = self.socket.recv(164)

        if(len(self.addr_pkt)!=0):
            self.bytes_read = len(self.addr_pkt)
            while(self.bytes_read < 164):
                self.addr_pkt += self.socket.recv(164-self.bytes_read)
                self.bytes_read = len(self.addr_pkt)

        self.sessionid = self.addr_pkt[4:20].decode()
        self.lenfile = self.addr_pkt[20:30].decode()
        self.lenpart = self.addr_pkt[30:36].decode()
        self.filename = self.addr_pkt[36:136].decode()
        self.md5 = self.addr_pkt[136:].decode()

        db = dataBase()
        search = db.check_file(self.sessionid, self.md5)

        if(serach == 0):
            npart = db.insert_file(self.sessionid, self.md5, self.filename, int(self.lenfile), int(self.lenpart))
            self.aadr_pkt = "AADR"+npart
            self.socket.send(self.addr_pkt.encode())
            self.socket.close()
        else:
            npart = db.update_file(self.sessionid, self.md5, self.filename, int(self.lenfile), int(self.lenpart))
            self.aadr_pkt = "AADR"+npart
            self.socket.send(self.addr_pkt.encode())
            self.socket.close()

        # insert or update md5 in global dict
        self.list.append(Util.globalDict[self.sessionid])
        self.list.append(self.md5)
        Util.globalDict[self.sessionid] = self.list

        # insert into interested 
        peer_addr = db.getPeerBySid(self.sessionid)
        db.insertInterested(self.sessionid, peer_addr[0], peer_addr[1])

        # insert into bitmapping
        totalBit = math.ceil((self.lenfile / self.lenpart))
        bits = pL.partList_gen(totalBit, 255)
        db.insertBitmapping(self.md5, self.sessionid, bits)