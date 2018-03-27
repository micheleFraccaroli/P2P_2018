import sys
import socket
import os
import math
from pathlib import Path
from Conn import Conn
import multiprocessing as mp

class Download:
    def __init__(self, ipp2p_B_4, ipp2p_B_6, pp2p_B, md5, filename):

        #ip other peer
        self.ipp2p_B_4 = ipp2p_B_4
        self.ipp2p_B_6 = ipp2p_B_6
        self.pp2p_B = pp2p_B

        #file
        self.file_signature = md5
        self.filename = filename

        #chunk veriables
        self.data_recv = []

        #var for bytes controller
        self.bytes_read_f = 0
        self.bytes_read_l = 0
        self.bytes_read = 0
        self.bytes_read_i = 0

    def download(self):
        print("\n--- DOWNLOAD ---\n")

        self.con = Conn(self.ipp2p_B_4, self.ipp2p_B_6, int(self.pp2p_B))
        self.con.connection()

        self.md5 = self.file_signature
        print(self.md5)

        to_peer = "RETR" + self.md5

        self.con.s.send(to_peer.encode('ascii'))

        self.first_packet = self.con.s.recv(10)
        self.bytes_read_f = len(self.first_packet)
        while (self.bytes_read_f < 10):
            self.first_packet += self.con.s.recv(10 - self.bytes_read_f)
            self.bytes_read_f = len(self.first_packet)

        if (self.first_packet[:4].decode() == "ARET"):
            i = self.first_packet[4:10].decode()  # n di chunk o indice del ciclo for

            for j in range(int(i)):
                self.chunk_length = self.con.s.recv(5)  # lunghezza del primo chunk

                self.bytes_read_l = len(self.chunk_length)
                while (self.bytes_read_l < 5):       # controllo che siano stati realmente letti i bytes richiesti
                    self.chunk_length += self.con.s.recv(5 - self.bytes_read_l)
                    self.bytes_read_l = len(self.chunk_length)

                self.chunk = self.con.s.recv(int(self.chunk_length))  # dati
                #self.data_recv.append(self.chunk)
                self.bytes_read = len(self.chunk)

                while (self.bytes_read < int(self.chunk_length)):        # controllo che siano stati realmente letti i bytes richiesti
                    self.chunk += self.con.s.recv(int(self.chunk_length) - self.bytes_read)
                    self.bytes_read = len(self.chunk)
                    #self.data_recv.append(buffer)
                self.data_recv.append(self.chunk)
        self.con.deconnection()

        check_file = Path(self.filename)
        print(check_file)

        if (check_file.is_file()):
            choice = input("\nIl file esiste già nel tuo file system, vuoi sovrascriverlo? (Y,n): ")
            if(choice == "Y"):
                path_file = "/img/" + self.filename
                os.remove(path_file)
                file_recv = open(path_file, "ab")
                for i in self.data_recv:
                    file_recv.write(i)
            else:
                return
        else:
            file_recv = open(path_file,"ab")
            for i in self.data_recv:
                file_recv.write(i)

        f = open(path_file,"rb")
        r = f.read()
        print("\n--- FILE DOWNLOADED ---\n")

'''
if __name__ == "__main__":
    l = []

    file_name = "bigimg.jpg"

    down = Download('qwert12345yuiop5', '172.16.8.3', 'fc00::8:3', 50003, '926e7971a76e7157b179b131f4f6e55a', file_name, '127.0.1.1', '::1')
    op = input("'D' for download: ")
    if (op == "D"):
        down.download()
        print("\n--- END ---") 
'''