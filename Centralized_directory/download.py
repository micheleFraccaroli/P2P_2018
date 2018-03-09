import time
import socket
import os
import math
import binascii as bhash
import multiprocessing as mp
import hashlib as hl
from threading import Timer


class Download:
    def __init__(self):
        # mio ip e porta
        self.ipp2p_A = '192.168.43.69' #put your ip here!
        self.pp2p_A = 54322

        # ip e porta che ricavo dalla funzione di 'search'
        self.ipp2p_B = '192.168.43.225'
        self.pp2p_B = 12345

        # md5 del file che mi restituisce la 'search'
        '''
        file = open("lion.jpg", "rb")
        img = file.read()
        # self.file_signature = hl.md5(img).hexdigest()
        '''
        #variabili provenienti dalla ricerca
        self.file_signature = 'd054890aa6a20fe5273d24feff7acc79'
        self.filename = 'lion_recv.jpg'

        # lista con chunk
        self.data_recv = []
        self.data_to_send = []
        self.chunk_size = 1024

        # variabili per controllo byte in ricezione
        self.bytes_read_f = 0
        self.bytes_read = 0
        self.bytes_read_l = 0

    def connection(self):
        try:
            # this is for ipv4 and ipv6
            self.infoS = socket.getaddrinfo(self.ipp2p_B, self.pp2p_B)
            self.s = socket.socket(*self.infoS[0][:3])
            self.s.connect(self.infoS[0][4])

        except IOError as expt:
            print ("Errore nella connessione alla directory --> " + expt)

    def deconnection(self):
        try:
            self.s.close()
        except IOError as expt:
            print ("Errore nella connessione alla directory --> " + expt)

    def download(self):
        print("\n--- DOWNLOAD ---\n")

        self.connection()

        self.md5 = self.file_signature  # md5 from search
        print(self.md5)

        to_peer = "RETR" + self.md5

        self.s.send(to_peer.encode('ascii'))


        self.first_packet = self.s.recv(10)
        self.bytes_read_f = len(self.first_packet)
        while (self.bytes_read_f < 10):
            self.first_packet = self.s.recv(10 - self.bytes_read_f)
            self.bytes_read_f = self.bytes_read_f + len(self.first_packet)


        if (self.first_packet[:4].decode() == "ARET"):
            i = self.first_packet[4:10].decode()  # n di chunk o indice del ciclo for
            print(i)
            for j in range(int(i)):
                self.chunk_length = self.s.recv(5)  # lunghezza del primo chunk

                self.bytes_read_l = len(self.chunk_length)
                while (self.bytes_read_l < 5):       # controllo che siano stati realmente letti i byte richiesti
                    self.chunk_length = self.s.recv(5 - self.bytes_read_l)
                    self.bytes_read_l = self.bytes_read_l + len(self.chunk_length)

                print(len(self.chunk_length))
                self.chunk = self.s.recv(int(self.chunk_length))  # dati

                self.bytes_read = len(self.chunk)
                while (self.bytes_read < int(self.chunk_length)):        # controllo che siano stati realmente letti i byte richiesti
                    self.chunk = self.s.recv(int(self.chunk_length) - self.bytes_read)
                    self.bytes_read = self.bytes_read + len(self.chunk)

                print(self.bytes_read)
                print(self.chunk)
                self.data_recv.append(self.chunk)
                print(self.data_recv[j])

        self.deconnection()

        file_recv = open(self.filename,"ab") # rigenerazione immagine
        for i in self.data_recv:
            file_recv.write(i)

        f = open(self.filename,"rb")
        r = f.read()
        print(r)

    def chunking(self, file_obj, file_name, chunk_size):
        list_of_chunk = []
        info = os.stat(file_name)
        dim_file = info.st_size

        nchunk = math.modf(dim_file / chunk_size)[1] + 1  # numero di chunk
        for i in range(int(nchunk)):
            d = file_obj.read(chunk_size)
            #d = bytearray(f)
            if (len(d) == chunk_size):
                list_of_chunk.append(d)
            elif (len(d) < chunk_size):
                '''
                dif = chunk_size - len(d)
                for i in range(dif):  # aggiungo gli spazi mancanti per colmare l'ultimo chunk
                    d = d + bytes(' '.encode())
                '''
                list_of_chunk.append(d)

        return list_of_chunk, int(nchunk)

    def upload(self):
        # dizionario simulato da creare nell'add file
        dict = {self.file_signature: 'lion.jpg'}
        print(self.file_signature)
        print(dict[self.file_signature])

        peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peersocket.bind((self.ipp2p_A, self.pp2p_A))

        peersocket.listen(1)

        while True:
            other_peersocket, addr = peersocket.accept()
            print("Connesso al peer " + str(addr))

            self.from_peer = other_peersocket.recv(36)
            print("Primi 4 byte ----> " + str(self.from_peer[:4].decode()))
            print("\ne successivo md5 ---------> " + str(self.from_peer[4:36].decode()))
            if (self.from_peer[:4].decode() == "RETR"):
                try:
                    file_to_send = dict[self.from_peer[4:36].decode()]
                    print("file to send ---> " + str(file_to_send))
                    f = open(file_to_send, "rb")
                    self.data_to_send, self.nchunk = self.chunking(f, file_to_send, self.chunk_size)

                    nchunk = int(self.nchunk)

                    first_response = "ARET" + str(nchunk).zfill(6)
                    other_peersocket.send(first_response.encode('ascii'))
                    for i in self.data_to_send:
                        length = str(len(i)).zfill(5)
                        other_peersocket.send(length.encode('ascii'))
                        print(length)
                        other_peersocket.send(i)
                        print(len(i))
                        print(i)

                except IOError:
                    print("Errore, file non trovato! errore")


if __name__ == "__main__":
    l = []
    down = Download()
    #p1 = mp.Process(target=down.upload)
    #p1.start()  # processo con l'upload dei dati quando vengo contattato da un alto peer
    op = input("'D' for download or 'U' for upload: ")
    if(op == "U"):
        down.upload()

    elif (op == "D"):
        down.download()
        print("\n--- END ---")
