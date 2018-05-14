import sys
import os
import hashlib
from pathlib import Path
from Conn import Conn

#aggiunta del file lato peer
class Add:
    def __init__(self, t_ipv4, t_ipv6, t_port):
        self.t_ipv4 = t_ipv4
        self.t_ipv6 = t_ipv6
        self.t_port = t_port
        self.sid = Util.sessionId
        self.lenpart = Util.lenpart.zfill(6)
        self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

    def add_file(self, file):

        check_file = Path('img/'+file)

        if (check_file.is_file()):
            self.f = open('img/'+file, 'rb')
            self.contenuto = self.f.read()
            self.filename = self.f.name
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

                self.con.deconnection()
            else:
                print("Errore di connessione, riprovare...")
        else:
            print("Non ho trovato nessun file con il seguente nome nella cartella img")
'''
if __name__ == '__main__':
    aggiunta = Add("127.0.0.1","::1",3000, "1234567891234567")
    aggiunta.add_file("immagine.jpg")
'''
