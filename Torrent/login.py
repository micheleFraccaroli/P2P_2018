from Conn import Conn
from dataBase import dataBase
import Util

class login:
   def __init__(self, ip, port, config):
      self.ip_t = ip
      self.port_t = port
      self.ip4_l = config.selfV4
      self.ip6_l = config.selfV6
      self.port_l = config.selfP

   def login(self):
      con =Conn(self.ip[:15],self.ip[16:], self.port)
      con.connection()
      
      addr = Util.ip_formatting(self.ip4_l, self.ip6_l, self.port_l)

      packet = "LOGI" + addr

      con.s.send(packet.encode())

      recv_packet = con.s.recv(20)
      if(recv_packet[:4].decode() == 'ALGI'):
         db.insertSid(recv_packet[4:].decode())