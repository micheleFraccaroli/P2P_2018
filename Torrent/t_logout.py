import sys
import threading as th
from dataBase import dataBase

class t_logout(th.Thread):
   def __init__(self,other_peersocket):
      th.Thread.__init__(self)
      self.other_peersocket = other_peersocket
      self.bytes_read = 0

   def run(self):
      db = dataBase()

      recv_packet = self.other_peersocket.recv(16)
      self.bytes_read = len(recv_packet)
      while(self.bytes_read < 16):
         recv_packet += self.other_peersocket.recv(16 - self.bytes_read)
         self.bytes_read = len(recv_packet)

      statusLogout, partdown = db.checkLogout(recv_packet.decode())

      packet = statusLogout + str(partdown).zfill(10)

      self.other_peersocket.send(packet.encode())