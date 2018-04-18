import sys
import socket
from Conn import Conn
from Util import Util

class Login:
    def __init__(self, ipp2p_dir_v4, ipp2p_dir_v6, my_ipv4, my_ipv6, pp2p_bf, config):
        self.ip_dir_4 = ipp2p_dir_v4
        self.ip_dir_6 = ipp2p_dir_v6
        self.dir_port = config.selfP

        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.pp2p_bf = pp2p_bf

        self.con = Conn(self.ip_dir_4, self.ip_dir_6, self.dir_port)

    def login(self):
        print("\n--- LOGIN ---\n")

        try:
            self.con.connection()
        except IOError as expt:
            print("Errore di connessione")
            print(expt)
            sys.exit(0)
        
        self.ipp2p = Util.ip_formatting(self.ip_dir_4, self.ip_dir_6, self.dir_port)

        data_login = "LOGI" + self.ipp2p

        self.con.s.send(data_login.encode('ascii'))

        self.ack_login = self.con.s.recv(20)  # 4B di ALGI + 16B di SID

        bytes_read = len(self.ack_login)

        while(bytes_read < 20):
            self.ack_login += self.s.recv(20 - self.bytes_read)
            self.bytes_read += len(self.ack_login)

        print("Ip peer ---> " + str(self.ipp2p))
        print("Port peer ---> " + str(self.pp2p))

        if (self.ack_login[:4].decode() == "ALGI"):
            self.sid = self.ack_login[4:20]

            if (self.sid == '0000000000000000'):
                print("Errore durante il login\n")
                exit()
            else:
                print("Session ID ---> " + str(self.sid.decode()) + "\n")
        else:
            print("Errore del pacchetto, string 'ALGI' non trovata")
            self.con.deconnection()
            exit()

        self.con.deconnection()

        return self.sid

    def logout(self, sid):
        print("\n--- LOGOUT ---\n")

        self.con.connection()

        data_logout = "LOGO" + sid.decode()

        self.con.s.send(data_logout.encode('ascii'))

        self.ack_logout = self.con.s.recv(7)

        self.bytes_read = len(self.ack_logout)

        while(self.bytes_read < 7):
            self.ack_logout += self.con.s.recv(7 - self.bytes_read)
            self.bytes_read = len(self.ack_logout)

        if (self.ack_logout[:4].decode() == "ALGO"):
            print("Numero di file eliminati ---> " + str(self.ack_logout[4:7].decode()))

        self.con.deconnection()