import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from Conn import Conn
from Upload import Upload
import threading as th

#thread che si occupa della gestione dell'eliminazione di un file per conto di un peer

class ThreadDEL(th.Thread):
    def init(self, pkt_del):
        th.Thread.__init__(self)
        self.pkt_del = pkt_del
        self.lock = lock

    def run(self):
        self.sessionid = self.pkt_del[4:20]
        self.md5 = self.pkt_del[20:52]

        db = dataBase()
        self.lock.acquire()
        find = db.retriveFILE(self.sessionid, self.md5)

        if(find == 0):
            self.lock.release()
            Util.printLog("[DEFF] non ho trovato nessun file caricato da: "+self.sessionid+" con il seguente md5: "+self.md5)
        else:
            db.deleteFILE(self.sessionid, self.md5)
            self.lock.release()
            Util.printLog("[DEFF] ho eliminato il file caricato da: "+self.sessionid+" con il seguente md5: "+self.md5)
        del db

if __name__ == '__main__':

    sessionid = '1234'.ljust(16,'1')
    md5 = 'abcd'.ljust(32,'2')
    pkt_del = 'DEFF'+sessionid+md5

    th_DEL = ThreadINS(pkt_del)
    th_DEL.start()
