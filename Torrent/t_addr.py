import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
import threading as th

#thread che si occupa della gestione dell'aggiunta di un file proveniente da un peer

class t_addr(th.Thread):
    def __init__(self, socket):
        th.Thread.__init__(self)
        self.socket = socket

    def run(self):
        self.addr_pkt = self.socket.recv(164)

        if(len(self.addr_pkt)!=0):
            self.bytes_read = len(self.addr_pkt)
            while(self.bytes_read < 164):
                self.addr_pkt += self.socket.recv(164-self.bytes_read)
                self.bytes_read = len(self.addr_pkt)

        self.sessionid = self.addr_pkt[4:20]
        self.lenfile = self.addr_pkt[20:30]
        self.lenpart = self.addr_pkt[30:36]
        self.filename = self.addr_pkt[36:136]
        self.md5 = self.addr_pkt[136:]

        db = dataBase()
        npart = db.insert_file(self.sessionid, self.md5, self.filename, self.lenfile, self.lenpart)
        self.aadr_pkt = "AADR"+npart

        self.socket.send(self.addr_pkt.encode())
        self.socket.close()
