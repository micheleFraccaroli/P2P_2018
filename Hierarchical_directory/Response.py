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

# lock
lock = th.Lock()

class thread_Response(th.Thread):
    def __init__(self, recv_packet, lock): 
        th.Thread.__init__(self) # thread instance first level
        self.bytes_read = 0
        self.lock = lock
        self.recv_packet = recv_packet

    def run(self):
        db = dataBase()
        while True:
                if(Util.statusRequest[self.recv_packet[4:20]]):
                    self.lock.acquire()
                    db.insertResponse(self.recv_packet[4:20].decode(), self.self.recv_packet[20:75].decode(), self.recv_packet[75:80].decode(), self.recv_packet[80:112].decode(), self.recv_packet[112:212].decode())
                    self.lock.release()
                else:
                    pktid = '***' + str(self.recv_packet[4:20].decode())
                    self.lock.acquire()
                    db.insertResponse(pktid, self.self.recv_packet[20:75].decode(), self.recv_packet[75:80].decode(), self.recv_packet[80:112].decode(), self.recv_packet[112:212].decode())
                    self.lock.release()
        Util.printLog("CHIUDO THREAD LIVELLO UNO")