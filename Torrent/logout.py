from Conn import Conn
import Util
from dataBase import *

#Classe per l'invio della richiesta di logout da parte del peer

class logout:
    def _init_(self, config, sid):
        self.t_ipv4 = config.trackerV4
        self.t_ipv6 = config.trackerV6
        self.t_port = config.trackerP
        self.sid = sid
        self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

    def send_logout():
        if(self.con.connection()):
            self.log_pkt = "LOGO"+sid
            self.con.s.send(self.log_pkt.encode())

            self.ack_log = self.con.s.recv(14)
            self.bytes_read = len(self.ack_log)

            while(self.bytes_read < 14):
                self.ack_log += self.con.s.recv(14 - self.bytes_read)
                self.bytes_read = len(self.ack_log)
            print(self.ack_log.encode())
            if(self.ack_log[0:4].encode() == "NLOG"):
                Util.mode = 'logged'
            else:
                db = dataBase()
                db.destroy()
                del db
                Util.mode = 'normal'
            self.con.deconnection()
        else:
            print("Connection refused...")
