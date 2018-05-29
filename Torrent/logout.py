from Conn import Conn
import Util
from dataBase import *

#Classe per l'invio della richiesta di logout da parte del peer

class logout:
    def __init__(self, config):
        self.t_ipv4 = config.trackerV4
        self.t_ipv6 = config.trackerV6
        self.t_port = config.trackerP
        self.sid = Util.sessionId
        self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)

    def send_logout(self):
        if(self.con.connection()):
            db = dataBase()
            self.log_pkt = "LOGO"+self.sid
            self.con.s.send(self.log_pkt.encode())

            self.ack_log = self.con.s.recv(14)
            self.bytes_read = len(self.ack_log)

            while(self.bytes_read < 14):
                self.ack_log += self.con.s.recv(14 - self.bytes_read)
                self.bytes_read = len(self.ack_log)

            if(self.ack_log[0:4].decode() != "NLOG"):
                db.updateConfig('mode','normal')
                db.deleteAll()
                Util.mode = 'normal'
                del db
            else:
                Util.printLog("Logout failed: "+self.ack_log.decode())
            self.con.deconnection()
        else:
            Util.printLog("Connection refused...")
