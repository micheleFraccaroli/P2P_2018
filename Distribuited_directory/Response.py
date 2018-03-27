import sys
import os
import socket
import time
import Util
import threading as th
import ipaddress as ipaddr
from Conn import Conn
from Search_receive import Search_res
from dataBase import dataBase
from Download import Download

# lock
lock = th.Lock()

class thread_Response(th.Thread):
    def __init__(self, other_peersocket): # dict_src è una lista di paket id che ho generato con la ricerca
        th.Thread.__init__(self) # thread istance 
        self.bytes_read = 0
        self.other_peersocket = other_peersocket

    def run(self):
        db = dataBase()
        list = []
        print("### NEW THREAD RUNNING ###\n")

        while True:
            recv_packet = self.other_peersocket.recv(212)

            self.bytes_read = len(recv_packet)
            while(self.bytes_read < 212):
                recv_packet += self.other_peersocket.recv(212 - self.bytes_read)
                self.bytes_read = len(recv_packet)

            # retrieving data from file research
            if(recv_packet[:4].decode() == "AQUE"):
                pktid_recv = recv_packet[4:20].decode()
                
                lock.acquire()
                db.insertResponse(pktid_recv, recv_packet[20:75].decode(), recv_packet[75:80].decode(), recv_packet[80:112].decode(), recv_packet[112:212].decode())
                lock.release()
                
                # download
                ipv4, ipv6 = recv_packet[20:75].decode().split('|')
                ipv4, ipv6, port, ttl = Util.ip_deformatting(ipv4, ipv6, recv_packet[75:80].decode(), None)
                down = Download(ipv4,ipv6,port,recv_packet[80:112].decode(),recv_packet[112:212].decode())

                self.other_peersocket.close()
                del db