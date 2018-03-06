import socket
import os
import math
import multiprocessing as mp
import hashlib as hl


class Download:
    def __init__(self):
        # mio ip e porta
        self.ipp2p_A = '10.14.92.226'
        self.pp2p_A = 54321

        # ip e porta che ricavo dalla funzione di 'search'
        self.ipp2p_B = '10.14.76.72'
        self.pp2p_B = 12345

        # md5 del file che mi restituisce la 'search'

        file = open("lion.jpg", "rb")
        img = file.read()
        # self.file_signature = hl.md5(img).hexdigest()
        self.file_signature = 'd054890aa6a20fe5273d24feff7acc79'

        # lista con chunk
        self.data_recv = []
        self.data_to_send = []
        self.chunk_size = 1024

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

        self.first_packet = self.s.recv(50)

        if (self.first_packet[:4].decode() == "ARET"):
            i = self.first_packet[4:10]  # n di chunk o indice del ciclo for
            l = self.first_packet[10:15]  # lunghezza del primo chunk
            end_pack = 15 + l.decode()
            self.data_recv.append(self.first_packet[15:end_pack])  # dati

            for j in range(i):
                self.packet = self.s.recv(end_pack)
                self.data_recv.append(self.packet[end_pack])

        self.deconnection()

        return self.data_recv

    def chunking(self, file_obj, file_name, chunk_size):
        list_of_chunk = []
        info = os.stat(file_name)
        dim_file = info.st_size

        nchunk = math.modf(dim_file / chunk_size)[1] + 1  # numero di chunk
        for i in range(int(nchunk)):
            d = bytearray(file_obj.read(chunk_size))
            if (len(d) == chunk_size):
                list_of_chunk.append(d)
            elif (len(d) < chunk_size):
                dif = chunk_size - len(d)
                for i in range(dif):  # aggiungo gli spazi mancanti per colmare l'ultimo chunk
                    d.append(32)
                list_of_chunk.append(d)

        return list_of_chunk, int(nchunk)

    def upload(self):
        # dizionario simulato da creare nell'add file
        dict = {self.file_signature: 'lion.jpg'}
        print(self.file_signature)
        print(dict[self.file_signature])

        peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peersocket.bind((self.ipp2p_A, self.pp2p_A))

        peersocket.listen()

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
                    
                    for i in self.data_to_send:
                        nchunk = int(self.nchunk)
                        peer_response = "ARET" + str(nchunk).zfill(6) + str(self.chunk_size) + str(bytes(i))
                        print(peer_response)
                        other_peersocket.send(peer_response.encode('ascii'))

                except IOError:
                    print("Errore, file non trovato!\n")


if __name__ == "__main__":
    l = []
    down = Download()
    p1 = mp.Process(target=down.upload)
    p1.start()  # processo con l'upload dei dati quando vengo contattato da un alto peer

    op = input("'D' for download: ")
    if (op == "D"):
        p2 = mp.Process(target=down.download)
        p2.start()  # processo con la funzione di download