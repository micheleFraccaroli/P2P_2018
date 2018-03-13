import socket
import os
import math
from pathlib import Path
from Centralized_directory.Add_Remove import AddRm
from Centralized_directory.Conn import Conn
from Centralized_directory.dir_login import Peer
import multiprocessing as mp

class Download:
    def __init__(self, sid, ipp2p_B, pp2p_B, md5, filename, ipp2p_dir):

        #ip other peer
        self.ipp2p_B = ipp2p_B
        self.pp2p_B = pp2p_B

        #ip directory
        self.ipp2p_dir = ipp2p_dir
        self.pp2p_dir = 3000

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

        #sessionID for download number
        self.sid = sid

    def download(self):
        print("\n--- DOWNLOAD ---\n")

        self.con = Conn(self.ipp2p_B, self.pp2p_B)
        self.con.connection()

        self.md5 = self.file_signature
        print(self.md5)

        to_peer = "RETR" + self.md5

        self.s.send(to_peer.encode('ascii'))

        self.first_packet = self.s.recv(10)
        self.bytes_read_f = len(self.first_packet)
        while (self.bytes_read_f < 10):
            self.first_packet += self.s.recv(10 - self.bytes_read_f)
            self.bytes_read_f = len(self.first_packet)

        if (self.first_packet[:4].decode() == "ARET"):
            i = self.first_packet[4:10].decode()  # n di chunk o indice del ciclo for

            for j in range(int(i)):
                self.chunk_length = self.s.recv(5)  # lunghezza del primo chunk

                self.bytes_read_l = len(self.chunk_length)
                while (self.bytes_read_l < 5):       # controllo che siano stati realmente letti i bytes richiesti
                    self.chunk_length += self.s.recv(5 - self.bytes_read_l)
                    self.bytes_read_l = len(self.chunk_length)

                self.chunk = self.s.recv(int(self.chunk_length))  # dati
                #self.data_recv.append(self.chunk)
                self.bytes_read = len(self.chunk)

                while (self.bytes_read < int(self.chunk_length)):        # controllo che siano stati realmente letti i bytes richiesti
                    self.chunk += self.s.recv(int(self.chunk_length) - self.bytes_read)
                    self.bytes_read = len(self.chunk)
                    #self.data_recv.append(buffer)
                self.data_recv.append(self.chunk)
        self.con.deconnection()

        check_file = Path(self.filename)
        print(check_file)

        if (check_file.is_file()):
            choice = input("\nIl file esiste già nel tuo file system, vuoi sovrascriverlo? (Y,n): ")
            if(choice == "Y"):
                os.remove(self.filename)
                file_recv = open(self.filename, "ab")
                for i in self.data_recv:
                    file_recv.write(i)
            else:
                exit()
        else:
            file_recv = open(self.filename,"ab")
            for i in self.data_recv:
                file_recv.write(i)

        f = open(self.filename,"rb")
        r = f.read()
        print("\n--- FILE DOWNLOADED ---\n")

        self.con = Conn(self.ipp2p_dir, self.pp2p_dir)
        self.con.connection()

        self.info_packet = "DREG" + self.sid + self.md5
        self.s.send(self.info_packet.encode('ascii'))

        self.info_recv = self.s.recv(9)
        self.bytes_read_i = len(self.info_recv)
        while (self.bytes_read_i < 9):
            self.info_recv += self.s.recv(9 - self.bytes_read_i)
            self.bytes_read_i = len(self.info_recv)
        if(self.info_recv[:4].decode() == "ADRE"):
            self.num_download = self.info_recv[4:9]

        print(self.num_download)
        self.con.deconnection()

'''
if __name__ == "__main__":
    l = []
    down = Download('192.168.43.69', 12345, '192.168.43.225', 54321, 'd054890aa6a20fe5273d24feff7acc79', 'other.jpg', '127.0.0.1')
    uploading = mp.Process(target=down.upload)
    uploading.start()
    #down.upload()

    op = input("'D' for download: ")
    if (op == "D"):
        downloading = mp.Process(target=down.download)
        downloading.start()
        #down.download()
        print("\n--- END ---")
'''