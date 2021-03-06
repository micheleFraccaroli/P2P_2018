import sys
import os
import socket
import time
import Util
import threading as th
import ipaddress as ipaddr
from Conn import Conn
from dataBase import dataBase
from Download import Download

class thread_Response(th.Thread):

    def __init__(self, recv_packet): 

        th.Thread.__init__(self) # thread instance first level
        self.bytes_read = 0
        self.lock = Util.lock
        self.recv_packet = recv_packet

    def run(self):
        count = 0
        db = dataBase()

        if(Util.statusRequest[self.recv_packet[4:20]]):
            self.lock.acquire()
            db.insertResponse(self.recv_packet[4:20], self.recv_packet[20:75], self.recv_packet[75:80], self.recv_packet[80:112], self.recv_packet[112:212])
            count = count + 1
            self.lock.release()
            Util.printLog("INSERITI NEL DATABASE TUTTI GLI AQUE RICEVUTI ---> " + str(count))
        else:
            pktid = '***' + str(self.recv_packet[4:20].decode())
            Util.printLog("RICEVUTA RICHIESTA NON VALIDA ----> " + str(pktid))
        Util.printLog("CHIUDO THREAD LIVELLO UNO")