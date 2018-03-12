import socket
import hashlib
from pathlib import Path


class Peer:

    def __init__(self,ip_dir,my_ipv4,my_ipv6,pPort):
        self.ip_dir = ip_dir
        self.dir_port = 3000

        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.pPort = pPort  # Porta di comunicazione verso gli altri Peers

    # -------- fase di login e logout con la directory --------

    def connection(self):
        try:
            # this is for ipv4 and ipv6
            self.infoS = socket.getaddrinfo(self.ip_dir, self.dir_port)
            self.s = socket.socket(*self.infoS[0][:3])
            self.s.connect(self.infoS[0][4])

        # self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.connect(self.dir_addr)
        except IOError as expt:  # l'eccezione ha una sotto eccez. per la socket
            print("Errore nella connessione alla directory --> " + expt)

    def deconnection(self):
        try:
            self.s.close()
        except IOError as expt:  # l'eccezione ha una sotto eccez. per la socket
            print("Errore nella connessione alla directory --> " + expt)

    def login(self):
        print("\n--- LOGIN ---\n")

        self.connection()

        # self.ipp2p_bf = self.s.getsockname()[0] #ip peer bad formatted

        # formattazione ip
        self.split_ip = self.my_ipv4.split(".")
        ip1 = self.split_ip[0].zfill(3)
        ip2 = self.split_ip[1].zfill(3)
        ip3 = self.split_ip[2].zfill(3)
        ip4 = self.split_ip[3].zfill(3)

        self.ipp2p = ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4 + '|' + 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff80'

        # formattazione porta
        self.pp2p_bf = self.s.getsockname()[1]  # porta peer bad formatted
        self.pp2p = '%(#)03d' % {"#": int(self.pp2p_bf)}

        data_login = "LOGI" + self.ipp2p + self.pp2p

        self.s.send(data_login.encode('ascii'))

        self.ack_login = self.s.recv(20)  # 4B di ALGI + 16B di SID

        self.bytes_read = len(self.ack_login)

        while(self.bytes_read < 20):
            self.ack_login += self.s.recv(20 - self.bytes_read)
            self.bytes_read = len(self.ack_login)

        print("Ip peer ---> " + str(self.ipp2p))
        print("Port peer ---> " + str(self.pp2p))
        print("First 4 byte from dir----> " + str(self.ack_login[:4].decode()))

        if (self.ack_login[:4].decode() == "ALGI"):
            self.sid = self.ack_login[4:20]

            if (self.sid == '0000000000000000'):
                print("Errore durante il login\n")
                exit()
            else:
                print("Session ID ---> " + str(self.sid.decode()) + "\n")
        else:
            print("Errore del pacchetto, string 'ALGI' non trovata")
            exit()

        self.deconnection()

    def logout(self):
        print("\n--- LOGOUT ---\n")

        self.connection()

        data_logout = "LOGO" + self.sid.decode()

        self.s.send(data_logout.encode('ascii'))

        self.ack_logout = self.s.recv(7)

        self.bytes_read = len(self.ack_logout)

        while(self.bytes_read < 7):
            self.ack_logout += self.s.recv(7 - self.bytes_read)
            self.bytes_read = len(self.ack_logout)

        print("First 4 byte from dir----> " + str(self.ack_logout[:4].decode()))

        if (self.ack_logout[:4].decode() == "ALGO"):
            print("Numero di file eliminati ---> " + str(self.ack_logout[4:7].decode()))

        self.deconnection()

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

            self.connection()

            # formattazione ip
            self.split_ip = self.my_ipv4.split(".")
            ip1 = self.split_ip[0].zfill(3)
            ip2 = self.split_ip[1].zfill(3)
            ip3 = self.split_ip[2].zfill(3)
            ip4 = self.split_ip[3].zfill(3)

            self.ipp2p = ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4

            # formattazione porta
            self.pp2p_bf = self.s.getsockname()[1]  # porta peer bad formatted
            self.pp2p = '%(#)03d' % {"#": int(self.pp2p_bf)}

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

            self.deconnection()

        else:
            print("Controllare l'esistenza del file o il percorso indicato in fase di input")

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

            self.connection()

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

            self.deconnection()

        else:
            print("Controllare l'esistenza del file o che il percorso indicato in fase di input sia corretto")    


# ---------------------------------------------


if __name__ == "__main__":
    peer = Peer()
    op = input("Login:\n")

    if(op == "LI"):
        peer.login()
        while True:
            op = input("LO, ADD, RM: ")
            if(op == "LO"):
                peer.logout()
            elif(op == "AG"):
                peer.aggiunta("lion.jpg")
            elif(op == "RM"):
                peer.rimuovi()
