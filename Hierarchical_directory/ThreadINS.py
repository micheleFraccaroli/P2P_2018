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

class ThreadINS(th.Thread):
    def init(self, pkt_ins):
        th.Thread.__init__(self)
        self.pkt_ins = pkt_ins
        self.lock = lock

    def run(self):
        self.sessionid = self.pkt_ins[4:20]
        self.md5 = self.pkt_ins[20:52]
        self.filename = self.pkt_ins[52:]

        db = dataBase()
        self.lock.acquire()
        find = db.retriveFILE(self.sessionid, self.md5)

        if(find == 0):
            db.insertFILE(self.sessionid, self.md5, self.filename)
            db.updateFILE(self.filename, self.md5)
            self.lock.release()
            Util.printLog("[ADFF] l'utente con il seguente SessionID: "+self.sessionid+"ha aggiunto il file: "+self.filename)
        else:
            db.updateFILE(self.filename, self.md5)
            self.lock.release()
            Util.printLog("[ADFF] aggiornato nome file in : "+self.filename)
        del db

if __name__ == '__main__':

    sessionid = '1234'.ljust(16,'1')
    md5 = 'abcd'.ljust(32,'2')
    filename = 'ciao'.ljust(100, '3')
    pkt_ins = 'ADFF'+sessionid+md5+filename

    th_INS = ThreadINS(pkt_ins)
    th_INS.start()
