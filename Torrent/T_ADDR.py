import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
import threading as th

#thread che si occupa della gestione dell'aggiunta di un file proveniente da un peer

class T_ADDR(th.Thread):
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
