import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
from Upload import Upload
import threading as th

#thread che si occupa della gestione dell'aggiunta di un file da parte di un peer

class threadINS(th.Thread):
    def init(self, pkt_ins):
        th.Thread.__init__(self)
        self.pkt_ins = pkt_ins

    def run(self):
        self.sessionid = self.pkt_ins[4:20]
        self.md5 = self.pkt_ins[20:52]
        self.filename = self.pkt_ins[52:]

        db = dataBase()
        find = retrive_file(self.sessionid, self.md5)

        if(find == 0):
            db.insert_file(self.sessionid, self.md5, self.filename)
            db.update_file(self.filename, self.md5)
        else:
            db.update_file(self.filename, self.md5)

        del db
