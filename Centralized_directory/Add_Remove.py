import hashlib
from pathlib import Path
from Centralized_directory.Conn import Conn

class AddRm:
    def __init__(self, ipp2p, pp2p):
        self.ipp2p = ipp2p
        self.pp2p = pp2p
        self.dict_filesystem = {}
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
                self.filename = self.filename.ljust(100, ' ')

            self.con.connection()

            self.dict_filesystem[self.FileHash.hexdigest()] = self.filename

            data_add_file = "ADDF" + str(self.sid.decode()) + self.FileHash.hexdigest() + self.filename

            self.s.send(data_add_file.encode())

            print("Ip peer ---> " + str(self.ipp2p))
            print("Port peer ---> " + str(self.pp2p))
            print(data_add_file)

            self.ack_add = self.s.recv(7)  # 4B di AADD + 3B di copia del file
            self.bytes_read = len(self.ack_add)

            while(self.bytes_read < 7):
                self.ack_add += self.s.recv(7 - self.bytes_read)
                self.bytes_read = len(self.ack_add)

            if (self.ack_add[:4].decode() == "AADD"):
                print(str(self.ack_add[0:7].decode()), "\n")
            else:
                print("Errore del pacchetto, stringa 'AADD' non trovata")
                exit()

            self.con.deconnection()

        else:
            print("Controllare l'esistenza del file o il percorso indicato in fase di input")

        return self.dict_filesystem

    def rimuovi(self):

        print("\n--- RIMUOVI FILE ---\n")

        self.rm_file = input("Inserisci il nome del file che desideri eliminare dalla directory:\n")

        self.check_file = Path(self.rm_file)

        if (self.check_file.is_file()):

            self.f = open(self.file, 'rb')
            self.contenuto = self.f.read()

            self.FileHash = hashlib.md5()
            self.FileHash.update(self.contenuto)
            self.FileHash.hexdigest()

            self.con.connection()

            data_remove_file = "DELF" + str(self.sid.decode()) + self.FileHash.hexdigest()
            print(data_remove_file)

            self.s.send(data_remove_file.encode())

            self.ack_rm = self.s.recv(7)  # 4B di DELF + 3B di copia del file
            self.bytes_read = len(self.ack_rm)

            while(self.bytes_read < 7):
                self.ack_rm += self.s.recv(7 - self.bytes_read)
                self.bytes_read = len(self.ack_rm)

            if (self.ack_rm[:4].decode() == "ADEL"):
                print(str(self.ack_rm.decode()), "\n")
            else:
                print("Errore del pacchetto, stringa 'ADEL' non trovata")
                exit()

            self.con.deconnection()

        else:
            print("Controllare l'esistenza del file o che il percorso indicato in fase di input sia corretto")