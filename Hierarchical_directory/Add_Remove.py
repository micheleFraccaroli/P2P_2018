import sys
import os
import hashlib
from pathlib import Path
from Conn import Conn
from File_system import File_system

class AddRm:
    def __init__(self, ipp2p_4, ipp2p_6, pp2p, sid):
        self.ipp2p_4 = ipp2p_4
        self.ipp2p_6 = ipp2p_6
        self.pp2p = pp2p
        self.sid = sid
        self.con = Conn(self.ipp2p_4, self.ipp2p_6, self.pp2p)

    def aggiunta(self, file):

        self.check_file = Path(file)

        if (self.check_file.is_file()):

            self.f = open(file, 'rb')
            self.contenuto = self.f.read()
            self.filename = self.f.name

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            if (len(self.filename) < 100):
                f_name = self.filename.ljust(100, ' ')

            self.con.connection()
            data_add_file = "ADDF" + str(self.sid.decode()) + self.FileHash.hexdigest() + f_name
            Util.printlog(data_add_file)
            self.con.s.send(data_add_file.encode())
            self.con.deconnection()
            file_write = File_system(self.FileHash.hexdigest(), self.filename)
            file_write.write()

        else:
            Util.printlog("[ADFF] Controllare l'esistenza del file o il percorso indicato in fase di input")

    def rimuovi(self, rm_file):

        self.check_file = Path(rm_file)

        if (self.check_file.is_file()):

            self.f = open(rm_file, 'rb')
            self.contenuto = self.f.read()

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            self.con.connection()
            data_remove_file = "DEFF" + str(self.sid.decode()) + self.FileHash.hexdigest()
            Util.printlog(data_remove_file)
            self.con.s.send(data_remove_file.encode())
            self.con.deconnection()

        else:
            Util.printlog("[DEFF] Controllare l'esistenza del file o che il percorso indicato in fase di input sia corretto")
