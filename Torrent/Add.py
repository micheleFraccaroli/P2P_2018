import sys
import os
import hashlib
from pathlib import Path
from Conn import Conn

#classe per l'aggiunta di un file al tracker, completa al 90%, manca solo la restituzione dal db delle variabili lenpart
#e sessionid che se ne sta occupando CESO
#aggiunta del file lato peer
class Add:
    def __init__(self, config, sid):
        self.t_ipv4 = config.trackerV4
        self.t_ipv6 = config.trackerV6
        self.t_port = config.trackerP
        self.sid = sid
        self.lenpart = "262144"
        self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

    def add_file(self, file):

        self.check_file = Path('img/'+file)

        if (self.check_file.is_file()):
            self.f = open('img/'+file, 'rb')
            self.contenuto = self.f.read()
            self.filename = file
            self.size = str(os.stat('img/'+file).st_size).zfill(10)

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            if (len(self.filename) < 100):
                self.f_name = self.filename.ljust(100, ' ')

            if(self.con.connection()):
                self.data_add_file = self.sid + self.size + self.lenpart + self.f_name + self.FileHash.hexdigest()
                self.con.s.send(self.data_add_file.encode())

                self.ack_aadr = self.con.s.recv(12)
                self.bytes_read = len(self.ack_aadr)

                while(self.bytes_read < 12):
                    self.ack_aadr += self.con.s.recv(12 - self.bytes_read)
                    self.bytes_read = len(self.ack_aadr)

                    print('Added file ' + nameFile + 'to tracker')

                self.con.deconnection()
            else:
                print("Connection refused...")
        else:
            print("Thre isn't no file with this name in your directory img")

if __name__ == '__main__':
    aggiunta = Add("127.0.0.1","::1",3000, "1234567891234567")
    aggiunta.add_file("baboon.png")
