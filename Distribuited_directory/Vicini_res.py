import socket
import threading as th
from dataBase import dataBase

class Vicini_res(th.Thread):
    def __init__(self, port):
        th.Thread.__init__(self)
        self.bytes_read = 0
        self.port = port

    def run(self):
        db = dataBase()

        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.port))
        peersocket.settimeout(20)
        peersocket.listen(20)

        while True:
            other_peersocket, addr = peersocket.accept()
            recv_packet = self.other_peersocket.recv(80)

            self.bytes_read = len(recv_packet)
            while(self.bytes_read < 80):
                recv_packet += self.other_peersocket.recv(80 - self.bytes_read)
                self.bytes_read = len(recv_packet)

            # retrieving data from near research
            if(recv_packet[:4].decode() == "ANEA"):
                lock.acquire()
                db.insertResponse(recv_packet[4:20].decode(), recv_packet[20:75].decode(), recv_packet[75:80].decode())
                db.insertNeighborhood(recv_packet[20:75].decode(), recv_packet[75:80].decode())
                lock.release()
        
        del db