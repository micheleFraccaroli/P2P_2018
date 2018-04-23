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

        self.con.s.send(data_login.encode())
        self.con.deconnection()

        return self.sid

    def logout(self, sid):
        print("\n--- LOGOUT ---\n")

        self.con.connection()

        data_logout = "LOGO" + sid.decode()
        self.con.s.send(data_logout.encode())
        self.con.deconnection()