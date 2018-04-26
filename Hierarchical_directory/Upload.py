import signal
import os
import math
import socket
import threading as th
import ipaddress as ipaddr
from File_system import File_system

class Upload(th.Thread):
    def __init__(self, pp2p_A, packet, other_peersocket):
        th.Thread.__init__(self)
        self.pp2p_A = pp2p_A
        self.packet = packet
        self.other_peersocket = other_peersocket
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
            if (len(d) == chunk_size):
                list_of_chunk.append(d)
            elif (len(d) < chunk_size):
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


    def run(self):
        dictSystem = {}
        while True:
            dictSystem = self.readFileDict()

            try:
                file_to_send = str(dictSystem[self.packet])
                f = open('share/'+file_to_send, "rb")
                self.data_to_send, self.nchunk = self.chunking(f, file_to_send, self.chunk_size)
                nchunk = int(self.nchunk)
                first_response = "ARET" + str(nchunk).zfill(6)
                self.other_peersocket.send(first_response.encode())
                for i in self.data_to_send:
                    length = str(len(i)).zfill(5)
                    self.other_peersocket.send(length.encode())
                    self.other_peersocket.send(i)

            except IOError:
                print("Errore, file non trovato! errore")

            #signal.signal(signal.SIGINT,handler)
            #signal.signal(signal.SIGTSTP,handler)
