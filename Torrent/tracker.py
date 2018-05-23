import socket
import sys
import os
import threading as th
import Util
from Conn import Conn
from t_login import t_login
from t_fchu import t_fchu
from t_addr import t_addr
from t_rpad import t_rpad
from t_logout import t_logout
from t_look import t_look
from plot_net import plot_net
from matplotlib.pyplot import pause
from dataBase import dataBase

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class tracker:
	def body(self):
		open_conn = Conn(port = 3000)
		peersocket = open_conn.initializeSocket()
		db = dataBase()
		c = ['black']
		db.create("tracker")

		# check logged
		pN = plot_net()
		res = db.checkLogged()
		if(res):
			for r in res:
				c.append('green')
				ip = Util.ip_deformatting(r[0], r[1])
				pN.addPeer(ip[0], c)
				pause(0.5)

		while True:
			Util.printLog("###### IN ATTESA DI UNA RICHIESTA #######")
			other_peersocket, addr = peersocket.accept()
			if addr[0][:2] == "::":
				addrPack = addr[0][7:]
				Util.printLog("Richiesta in arrivo da: "+addrPack)
			else:
				addrPack=addr[0]
				Util.printLog("Richiesta in arrivo da: "+addrPack)

			recv_type = other_peersocket.recv(4)

			if(len(recv_type) != 0):
				self.bytes_read = len(recv_type)
				while (self.bytes_read < 4):
					recv_type += other_peersocket.recv(4 - self.bytes_read)
					self.bytes_read = len(recv_type)
				Util.printLog("RICHIESTA IN ENTRATA AL TRACKER → " + str(recv_type.decode()))

				# LOGIN ---
				if(recv_type.decode() == "LOGI"):
					recv_packet = other_peersocket.recv(60)
					self.bytes_read = len(recv_packet)
					while(self.bytes_read < 60):
						recv_packet += other_peersocket.recv(60 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					th_LOGIN = t_login(other_peersocket, recv_packet.decode())
					th_LOGIN.start()
					
					c.append('green')
					ip = Util.ip_deformatting(recv_packet[:55].decode(), recv_packet[55:].decode())
					pN.addPeer(ip[0], c)
					pause(1)

				# LOGOUT ---
				if(recv_type.decode() == "LOGO"):
					recv_packet = other_peersocket.recv(16)
					self.bytes_read = len(recv_packet)
					while(self.bytes_read < 16):
						recv_packet += other_peersocket.recv(16 - self.bytes_read)
						self.bytes_read = len(recv_packet)

					addr = db.getPeerBySid(recv_packet.decode())
					if(addr):
						ip = Util.ip_deformatting(addr[0], addr[1])

						t_LOGOUT = t_logout(other_peersocket, recv_packet.decode())
						t_LOGOUT.start()
						t_LOGOUT.join()
						Util.printLog(t_LOGOUT.statusLogout)
						if(t_LOGOUT.statusLogout == "ALOG"):
							pN.removePeer(ip[0], c)
							pause(1)
					
				# LOOK ---
				if(recv_type.decode() == "LOOK"):
					Util.printLog("\n→ ARRIVO LOOK ←\n")
					t_LOOK = t_look(other_peersocket)
					t_LOOK.start()

				# FCHU ---
				if(recv_type.decode() == "FCHU"):
					#Util.printLog("\n→ ARRIVO FCHU ←\n")
					th_FCHU = t_fchu(other_peersocket)
					th_FCHU.start()

				# ADDR ---
				if(recv_type.decode() == "ADDR"):
					Util.printLog("\n→ ARRIVO ADDR ←\n")
					th_ADDR = t_addr(other_peersocket)
					th_ADDR.start()

				# RPAD ---
				if(recv_type.decode() == "RPAD"):
					#Util.printLog("\n→ ARRIVO RPAD ←\n")
					th_RPAD = t_rpad(other_peersocket)
					th_RPAD.start()

if __name__ == "__main__":

	print(bcolors.MAGENTA + "____________________________      ________   ______   " + bcolors.ENDC)
	print(bcolors.MAGENTA + "\______   \_____  \______   \    /  _____/  /  __  \  " + bcolors.ENDC)
	print(bcolors.OKBLUE  + " |     ___//  ____/|     ___/   /   \  ___  >      <  " + bcolors.ENDC)
	print(bcolors.OKBLUE  + " |    |   /       \|    |       \    \_\  \/   --   \ " + bcolors.ENDC)
	print(bcolors.CYAN    + " |____|   \_______ \____|        \______  /\______  / " + bcolors.ENDC)
	print(bcolors.CYAN    + "                  \/                    \/        \/  " + bcolors.ENDC)

	print(bcolors.MAGENTA + "→ tracker online" + bcolors.ENDC)

	t = tracker()
	t.body()