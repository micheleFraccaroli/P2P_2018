import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from dataBase import dataBaseSuper
from Conn import Conn
from Upload import Upload
import threading as th

class ThreadLOGO(th.Thread):
    def __init__(self, pkt_logo):
        th.Thread.__init__(self)
        self.pkt_logo = pkt_logo
        self.sessionid = self.pkt_logo[4:]

        def answer(self, db, count, info):

            rows_delete = str(count).rjust(3,'0')
            pkt_algo = "ALGO"+rows_delete

            addr = Util.ip_deformatting(info[0], info[1], None)
            ip6 = ipad.ip_address(info[0][16:])
            self.con = Conn(addr[0], str(ip6), addr[2])
            try:
                self.con.connection()
                self.con.s.send(pkt_algo.encode())
                self.con.deconnection()
            except IOError as expt:
                print("Errore di connessione")
                print(expt)
                #sys.exit(0)

        def run(self):
            db = dataBaseSuper()
            Util.lock.acquire()
            self.count = db.deleteFROMpeer(sessionid)
            self.info = db.retrieveLOGIN(sessionid)
            Util.lock.release()
            Util.printLog("[ALGO] disconnessione dell'utente: "+self.sessionid+", file eliminati: "+str(self.count))
            del db
            self.answer(db, self.count, self.info)

if __name__ == '__main__':

    sessionid = '1234'.ljust(16,'1')
    pkt_logo = 'LOGO'+sessionid

    th_LOGO = ThreaLOGO(pkt_logo)
    th_LOGO.start()
