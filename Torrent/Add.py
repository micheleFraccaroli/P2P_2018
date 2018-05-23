import sys
import os
import Util
import hashlib
from pathlib import Path
from Conn import Conn
from dataBase import dataBase
from time import sleep

#classe per l'aggiunta di un file al tracker, completa al 90%, manca solo la restituzione dal db delle variabili lenpart
#e sessionid che se ne sta occupando CESO
#aggiunta del file lato peer
class Add:
    def __init__(self, config, sid):

        db = dataBase()

        self.t_ipv4 = config.trackerV4
        self.t_ipv6 = config.trackerV6
        self.t_port = config.trackerP
        self.sid = sid
        self.lenpart = db.retrieveConfig(('lenPart',)).zfill(6)
        self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

    def add_file(self, file):

        self.check_file = Path('Files/'+file)

        if (self.check_file.is_file()):
            self.f = open('Files/'+file, 'rb')
            self.contenuto = self.f.read()
            self.filename = file
            self.size = str(os.stat('Files/'+file).st_size).zfill(10)

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            if (len(self.filename) < 100):
                self.f_name = self.filename.ljust(100, ' ')

            if(self.con.connection()):
                self.data_add_file = 'ADDR' + self.sid + self.size + str(self.lenpart).zfill(6) + self.f_name + self.FileHash.hexdigest()
                self.con.s.send(self.data_add_file.encode())

                self.ack_aadr = self.con.s.recv(12)
                self.bytes_read = len(self.ack_aadr)

                while(self.bytes_read < 12):
                    print(self.bytes_read)
                    self.ack_aadr += self.con.s.recv(12 - self.bytes_read)
                    self.bytes_read = len(self.ack_aadr)

                    print('Added file ' + nameFile + 'to tracker')

                self.con.deconnection()
            else:
                print("Connection refused...")
        else:
            print("There isn't any file with this name in your directory")
            sleep(4)

if __name__ == '__main__':
    aggiunta = Add("127.0.0.1","::1",3000, "1234567891234567")
    aggiunta.add_file("baboon.png")
