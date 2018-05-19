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

class tracker:
	def body(self):
		open_conn = Conn(port = 3000)
		peersocket = open_conn.initializeSocket()

		while True:
			Util.printLog("###### IN ATTESA DI UNA RICHIESTA #######")
			print('RICHISTA')
			other_peersocket, addr = peersocket.accept()
			print('ancora')
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

				# LOGIN ---
				if(recv_type.decode() == "LOGI"):
					th_LOGIN = t_login(other_peersocket)
					th_LOGIN.start()

				# LOGOUT ---
				if(recv_type.decode() == "LOGO"):
					t_LOGOUT = t_logout(other_peersocket)
					t_LOGOUT.start()

				# LOOK ---
				if(recv_type.decode() == "LOOK"):
					t_LOOK = t_look(other_peersocket)
					t_LOOK.start()
					print('LOOK')

				# FCHU ---
				if(recv_type.decode() == "FCHU"):
					th_FCHU = t_fchu(other_peersocket)
					th_FCHU.start()

				# ADDR ---
				if(recv_type.decode() == "ADDR"):
					th_ADDR = t_addr(other_peersocket)
					th_ADDR.start()

				# RPAD ---
				if(recv_type.decode() == "RPAD"):
					th_RPAD = t_rpad(other_peersocket)
					th_RPAD.start()

if __name__ == "__main__":
	t = tracker()
	t.body()