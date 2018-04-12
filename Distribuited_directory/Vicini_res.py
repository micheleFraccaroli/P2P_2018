import socket
import Util
import sys
import threading as th
from dataBase import dataBase

class Vicini_res(th.Thread):
    def __init__(self, port,lock, stop_event):
        th.Thread.__init__(self)
        self.bytes_read = 0
        self.port = port
        self.lock = lock
        self.stop_event = stop_event

    def run(self):
        db = dataBase()

        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.port))
        #peersocket.settimeout(20)
        peersocket.listen(20)

        while (not self.stop_event.is_set()):
            try:
                other_peersocket, addr = peersocket.accept()
                recv_packet = other_peersocket.recv(80)
                
                self.bytes_read = len(recv_packet)
                
                while(self.bytes_read < 80):
                    recv_packet += other_peersocket.recv(80 - self.bytes_read)
                    self.bytes_read = len(recv_packet)

                Util.printLog("ANEAR da: " + addr[0])
                # retrieving data from near research
                Util.printLog("pacchetto ====> " + str(recv_packet.decode()))

                if(recv_packet[:4].decode() == "ANEA"):
                    self.lock.acquire()
                    db.insertResponse(recv_packet[4:20].decode(), recv_packet[20:75].decode(), recv_packet[75:80].decode(),"null", "null")
                    db.insertNeighborhood(recv_packet[20:75].decode(), recv_packet[75:80].decode())
                    self.lock.release()
            except:
                sys.exit()

        del db