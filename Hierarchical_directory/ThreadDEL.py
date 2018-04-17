import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
from Upload import Upload
import threading as th

#thread che si occupa della gestione dell'eliminazione di un file da parte di un peer

class threadDEL(th.Thread):
    def init(self, pkt_del):
        th.Thread.__init__(self)
        self.pkt_del = pkt_del

    def run(self):
        self.sessionid = self.pkt_del[4:20]
        self.md5 = self.pkt_del[20:52]

        db = dataBase()
        find = retrive_file(self.sessionid, self.md5)

        if(find > 0):
            Util.printLog("DEFF: non ho trovato nessun file")
        else:
            db.delete_file(self.sessionid, self.md5)
            Util.printLog("DEFF: ho eliminato il file")
        del db
