import sys
import socket
from Conn import Conn
#import hashlib
#from pathlib import Path

class Peer:

    def __init__(self, ipp2p_dir, my_ipv4, my_ipv6, pp2p_bf):
        self.ip_dir = ipp2p_dir
        self.dir_port = 3000

        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.pp2p_bf = pp2p_bf

        self.con = Conn(self.ip_dir, self.dir_port)

    def login(self):
        print("\n--- LOGIN ---\n")

        try:
            self.con.connection()
        except:
            print("Errore di connessione")
            sys.exit(0)

        # self.ipp2p_bf = self.s.getsockname()[0] #ip peer bad formatted

        # formattazione ip
        self.split_ip = self.my_ipv4.split(".")
        ip1 = self.split_ip[0].zfill(3)
        ip2 = self.split_ip[1].zfill(3)
        ip3 = self.split_ip[2].zfill(3)
        ip4 = self.split_ip[3].zfill(3)

        self.ipp2p = ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4 + '|' + 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff80'

        # formattazione porta
        self.pp2p = '%(#)03d' % {"#": int(self.pp2p_bf)}

        data_login = "LOGI" + self.ipp2p + self.pp2p

        self.con.s.send(data_login.encode('ascii'))

        self.ack_login = self.con.s.recv(20)  # 4B di ALGI + 16B di SID

        bytes_read = len(self.ack_login)

        while(bytes_read < 20):
            self.ack_login += self.s.recv(20 - self.bytes_read)
            self.bytes_read += len(self.ack_login)

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
            self.con.deconnection()
            exit()

        self.con.deconnection()

        return self.sid

    def logout(self, sid):
        print("\n--- LOGOUT ---\n")

        self.con.connection()

        data_logout = "LOGO" + sid.decode()

        self.con.s.send(data_logout.encode('ascii'))

        self.ack_logout = self.s.recv(7)

        self.bytes_read = len(self.ack_logout)

        while(self.bytes_read < 7):
            self.ack_logout += self.con.s.recv(7 - self.bytes_read)
            self.bytes_read = len(self.ack_logout)

        print("First 4 byte from dir----> " + str(self.ack_logout[:4].decode()))

        if (self.ack_logout[:4].decode() == "ALGO"):
            print("Numero di file eliminati ---> " + str(self.ack_logout[4:7].decode()))

        self.con.deconnection()

# ---------------------------------------------

'''
if __name__ == "__main__":
    peer = Peer()
    op = input("LI for login: ")

    if(op == "LI"):
        peer.login()
        op = input("LO for logout or AG for add: ")
        if(op == "LO"):
            peer.logout()
        elif(op == "AG"):
            peer.aggiunta("lion.jpg")
'''