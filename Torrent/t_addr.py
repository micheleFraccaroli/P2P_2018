import socket
import sys
import math
import os
import ipaddress as ipad
from dataBase import dataBase
import threading as th
#import partList_gen as pL

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

        self.sessionid = self.addr_pkt[0:16].decode()
        self.lenfile = int(self.addr_pkt[16:26].decode())
        self.lenpart = int(self.addr_pkt[26:32].decode())
        self.filename = self.addr_pkt[32:132].decode().strip(' ')
        self.md5 = self.addr_pkt[132:].decode()

        db = dataBase()
        db.create()
        search = db.check_file(self.sessionid, self.md5)

        if(search == 0):
            npart = db.insert_file(self.sessionid, self.md5, self.filename, self.lenfile, self.lenpart)
            self.aadr_pkt = "AADR"+npart
            self.socket.send(self.aadr_pkt.encode())
            self.socket.close()
        else:
            npart = db.update_file(self.sessionid, self.md5, self.filename, self.lenfile, self.lenpart)
            self.aadr_pkt = "AADR"+npart
            self.socket.send(self.aadr_pkt.encode())
            self.socket.close()
        '''
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
        '''
if __name__ == "__main__":

    peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    peersocket.bind(('', 3000))

    peersocket.listen(20)
    other_peersocket, addr = peersocket.accept()

    th_addr =  t_addr(other_peersocket)
    th_addr.start()
