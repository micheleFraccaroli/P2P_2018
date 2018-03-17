import sys
import socket
from Conn import Conn
#import hashlib
#from pathlib import Path

class Peer:

    def __init__(self, ipp2p_dir_v4, ipp2p_dir_v6, my_ipv4, my_ipv6, pp2p_bf):
        self.ip_dir_4 = ipp2p_dir_v4
        self.ip_dir_6 = ipp2p_dir_v6
        self.dir_port = 3000

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

        # self.ipp2p_bf = self.s.getsockname()[0] #ip peer bad formatted

        # formattazione ipv4
        self.split_ip_4 = self.my_ipv4.split(".")
        ip1_4 = self.split_ip_4[0].zfill(3)
        ip2_4 = self.split_ip_4[1].zfill(3)
        ip3_4 = self.split_ip_4[2].zfill(3)
        ip4_4 = self.split_ip_4[3].zfill(3)

        # formattazione ipv6
        self.split_ip_6 = self.my_ipv6.split(":")
        ip1_6 = self.split_ip_6[0].zfill(4)
        ip2_6 = self.split_ip_6[1].zfill(4)
        ip3_6 = self.split_ip_6[2].zfill(4)
        ip4_6 = self.split_ip_6[3].zfill(4)
        ip5_6 = self.split_ip_6[4].zfill(4)
        ip6_6 = self.split_ip_6[5].zfill(4)
        ip7_6 = self.split_ip_6[6].zfill(4)
        ip8_6 = self.split_ip_6[7].zfill(4)

        self.ipp2p = ip1_4 + '.' + ip2_4 + '.' + ip3_4 + '.' + ip4_4 + '|' + ip1_6 + ':' + ip2_6 + ':' + ip3_6 + ':' + ip4_6 + ':' + ip5_6 + ':' + ip6_6 + ':' + ip7_6 + ':' + ip8_6 
        
        # formattazione porta
        self.pp2p = '%(#)05d' % {"#": int(self.pp2p_bf)}

        data_login = "LOGI" + self.ipp2p + self.pp2p

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