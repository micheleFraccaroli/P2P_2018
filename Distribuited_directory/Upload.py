import signal
import os
import math
import socket
import multiprocessing as mp
import ipaddress as ipaddr
from File_system import File_system

class Upload:

    def __init__(self, pp2p_A):
        self.pp2p_A = pp2p_A
        print(self.pp2p_A)
        #chunk veriables
        self.data_to_send = []
        self.chunk_size = 1024

        self.bytes_read = 0

    def handler(signo,frame):
        print('Programma fermato....... codice segnale',signo)
        sys.exit(0)

    def chunking(self, file_obj, file_name, chunk_size):
        list_of_chunk = []        
        info = os.stat('img/'+file_name)
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

    def readFileDict(self):
        dict = {}
        f = open("File_System.txt", "r")
        
        r = f.read().splitlines()
        for i in r:
            line = i.split("|")
            dict[line[0]] = line[1]

        f.close()

        return dict


    def upload(self):
        dict = {}
        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.pp2p_A))

        peersocket.listen(10)
        
        while True:
            other_peersocket, addr = peersocket.accept()

            self.dict = self.readFileDict()

            self.from_peer = other_peersocket.recv(36)
            self.bytes_read = len(self.from_peer)
            while (self.bytes_read < 36):
                self.from_peer += other_peersocket.recv(36 - self.bytes_read)
                self.bytes_read = len(self.from_peer)

            if (self.from_peer[:4].decode() == "RETR"):
                try:
                    file_to_send = str(self.dict[self.from_peer[4:36].decode()])
                    f = open('img/'+file_to_send, "rb")
                    self.data_to_send, self.nchunk = self.chunking(f, file_to_send, self.chunk_size)
                    nchunk = int(self.nchunk)
                    first_response = "ARET" + str(nchunk).zfill(6)
                    other_peersocket.send(first_response.encode('ascii'))
                    for i in self.data_to_send:
                        length = str(len(i)).zfill(5)
                        other_peersocket.send(length.encode('ascii'))
                        other_peersocket.send(i)

                except IOError:
                    print("Errore, file non trovato! errore")
                    
            #signal.signal(signal.SIGINT,handler)
            #signal.signal(signal.SIGTSTP,handler)

'''
if __name__ == '__main__':
    dict = {}

    if (os.path.exists("File_System.txt")):
        file_read = File_system(None, None)
        dict = file_read.read()

    print(dict)

    u = Upload(dict, '192.168.43.69', 50004)
    u.upload()
'''