import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
import threading as th

class t_look(th.Thread):
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

        self.search = self.look_pkt[16:].decode()
        db = dataBase()
        db.create()
        nmd5, res = db.search_files(self.search)

        self.aloo_pkt = "ALOO"+str(nmd5).zfill(3)
        self.socket.send(self.aloo_pkt.encode())

        if(nmd5 > 0):
            for file in res:
                self.file_md5 = file[0]+file[1]+file[2]+file[3]
                self.socket.send(self.aloo_pkt.encode())

        self.socket.close()

if __name__ == '__main__':

    peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    peersocket.bind(('', 3000))

    peersocket.listen(20)
    other_peersocket, addr = peersocket.accept()

    th_addr =  T_ADDR(other_peersocket)
    th_addr.start()
