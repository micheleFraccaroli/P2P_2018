from Conn import Conn
from dataBase import dataBase
import Util

class login:
    def __init__(self, config):
        self.ip4_t = config.trackerV4
        self.ip6_t = config.trackerV6
        self.port_t = config.trackerP
        self.ip4_l = config.selfV4
        self.ip6_l = config.selfV6
        self.port_l = config.selfP

    def send_login(self):
        con = Conn(self.ip4_t, self.ip6_t, self.port_t)
        if con.connection():

            addr = Util.ip_formatting(self.ip4_l, self.ip6_l, self.port_l)

            packet = "LOGI" + addr

            con.s.send(packet.encode())

            recv_packet = con.s.recv(20)
            if(recv_packet[:4].decode() == 'ALGI'):
                db.insertSid(recv_packet[4:].decode())
        else:
            Util.printLog('Richiesta LOGO fallita')
