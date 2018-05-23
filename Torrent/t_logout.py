import sys
import threading as th
import Util
from dataBase import dataBase
from plot_net import plot_net
from matplotlib.pyplot import pause

class t_logout(th.Thread):
   def __init__(self,other_peersocket, packet):
      th.Thread.__init__(self)
      self.other_peersocket = other_peersocket
      self.bytes_read = 0
      self.packet = packet

   def run(self):
      db = dataBase()
      self.statusLogout, partdown = db.checkLogout(self.packet)

      packet = self.statusLogout + str(partdown).zfill(10)

      self.other_peersocket.send(packet.encode())
      self.other_peersocket.close()