import socket
import Util
import sys
import os
import ipaddress as ipad
from dataBase import dataBase
from dataBase import dataBaseSuper
from Conn import Conn
import threading as th

class ThreadLOGO():
    def __init__(self, pkt_logo, other_peersocket):
        self.pkt_logo = pkt_logo
        self.sessionid = self.pkt_logo[4:]
        self.other_peersocket = other_peersocket

    def answer(self, count, info):

        rows_delete = str(count).rjust(3,'0')
        pkt_algo = "ALGO"+rows_delete

        try:
            self.other_peersocket.send(pkt_algo.encode())
        except IOError as expt:
            print("Errore di connessione")
            print(expt)

    def LOGO(self):
        db = dataBaseSuper()
        Util.printLog("DENTRO A THREADLOGO")
        Util.lock.acquire()
        Util.printLog("SESSION ID LOGOUT: " + str(self.sessionid))
        self.info = db.retrieveLOGIN(self.sessionid)
        self.count = db.deleteFROMpeer(self.sessionid)
        Util.printLog("NUMERO DI FILE ELIMINATI ----> " + str(self.count))
        Util.lock.release()
        Util.printLog("[ALGO] disconnessione dell'utente: "+self.sessionid+", file eliminati: "+str(self.count))
        del db
        self.answer(self.count, self.info)
