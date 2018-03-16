import sys
import os
import hashlib
from pathlib import Path
from Conn import Conn
from File_system import File_system

class AddRm:
    def __init__(self, ipp2p, pp2p, dict_filesystem, sid):
        self.ipp2p = ipp2p
        self.pp2p = pp2p
        self.sid = sid
        self.dict_filesystem = dict_filesystem
        self.con = Conn(self.ipp2p, self.pp2p)

    def aggiunta(self, file):

        print("\n--- AGGIUNTA ---\n")

        # verifico l'esistenza del file

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

            self.dict_filesystem[self.FileHash.hexdigest()] = self.filename

            data_add_file = "ADDF" + str(self.sid.decode()) + self.FileHash.hexdigest() + f_name

            self.con.s.send(data_add_file.encode())

            print("Ip peer ---> " + str(self.ipp2p))
            print("Port peer ---> " + str(self.pp2p))
            print(data_add_file)

            self.ack_add = self.con.s.recv(7)  # 4B di AADD + 3B di copia del file
            self.bytes_read = len(self.ack_add)

            while(self.bytes_read < 7):
                self.ack_add += self.con.s.recv(7 - self.bytes_read)
                self.bytes_read = len(self.ack_add)

            if (self.ack_add[:4].decode() == "AADD"):
                print(str(self.ack_add[0:7].decode()), "\n")
            else:
                print("Errore del pacchetto, stringa 'AADD' non trovata")
                exit()

            self.con.deconnection()

        else:
            print("Controllare l'esistenza del file o il percorso indicato in fase di input")

        file_write = File_system(self.FileHash.hexdigest(), self.filename)
        file_write.write()

        return self.dict_filesystem

    def rimuovi(self):

        print("\n--- RIMUOVI FILE ---\n")

        self.rm_file = input("Inserisci il nome del file che desideri eliminare dalla directory:\n")

        self.check_file = Path(self.rm_file)

        if (self.check_file.is_file()):

            self.f = open(self.rm_file, 'rb')
            self.contenuto = self.f.read()

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            self.con.connection()

            data_remove_file = "DELF" + str(self.sid.decode()) + self.FileHash.hexdigest()
            print(data_remove_file)

            self.con.s.send(data_remove_file.encode())

            self.ack_rm = self.con.s.recv(7)  # 4B di DELF + 3B di copia del file
            self.bytes_read = len(self.ack_rm)

            while(self.bytes_read < 7):
                self.ack_rm += self.s.recv(7 - self.bytes_read)
                self.bytes_read = len(self.ack_rm)

            if (self.ack_rm[:4].decode() == "ADEL"):
                print(str(self.ack_rm.decode()), "\n")
            else:
                print("Errore del pacchetto, stringa 'ADEL' non trovata")
                exit()

            print(self.dict_filesystem)
            del self.dict_filesystem[self.FileHash.hexdigest()]

            self.con.deconnection()

            file_delete = File_system(self.FileHash.hexdigest(), self.rm_file)
            self.dict_filesystem = file_delete.over(self.dict_filesystem)

            return self.dict_filesystem

        else:
            print("Controllare l'esistenza del file o che il percorso indicato in fase di input sia corretto")

'''
if __name__ == '__main__':
    dict = {}
    if (os.path.exists("File_System.txt")):
        file_read = File_system(None, None)
        dict = file_read.read()
    sid = 'qwertyuio0987654'
    add_rm = AddRm('192.168.43.225','3000',dict, sid.encode())
    file_add = input("Digita il nome del file che vuoi aggiungere: ")
    dict = add_rm.aggiunta(file_add)

    dict = add_rm.rimuovi()
    print(dict)
'''