import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
import threading as th

class t_aloo(th.Thread):
    def __init__(self, socket):
        th.Thread.__init__(self)
        self.socket = socket

    def run(self):
        self.look_pkt = self.socket.recv(36)

        if(len(self.look_pkt)!=0):
            self.bytes_read = len(self.look_pkt)
            while(self.bytes_read < 36):
                self.look_pkt += self.socket.recv(36-self.bytes_read)
                self.bytes_read = len(self.look_pkt)

        self.search = self.look_pkt[20:].decode()
        db = dataBase()
        nmd5, res = db.search_files(self.search)

        self.aloo_pkt = "ALOO"+str(nmd5).zfill(3)
        self.socket.send(self.aloo_pkt.encode())

        if(nmd5 > 0):
            for file in res:
                self.file_md5 = file[0]+file[1]+file[2]+file[3]
                self.socket.send(self.aloo_pkt.encode())

        self.socket.close()
