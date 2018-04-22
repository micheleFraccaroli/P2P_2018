import time
import socket
import threading as th
from dataBase import dataBase
import Util
from Conn import Conn

class ThreadNEAR(th.Thread):
	def __init__(self,pack,lock,config):      #info[0] è l'ipv4, info[1] è l'ipv6 e info[2] è la porta, già formattata quindi uso direttamente 								l'informazione

		th.Thread.__init__(self)
		info           = Util.ip_deformatting(pack[20:75],pack[75:80],pack[80:])
		self.pid       = pack[4:20]
		self.lock      = lock
		self.config    = config

	def run(self):
			prefix=data_login[0:4]
			idSession="0000000000000000"

			if ((prefix!="LOGI")):
				return idSession
			not_duplicated=True
			for ssdi in exstisLogged.dataBase:
				if((exstisLogged.dataBase[ssdi].ip==idSession.ip or exstisLogged.dataBase[ssdi].ip==idSession.ip)) and int((exstisLogged.dataBase[ssdi].port==int(idSession.port))):
					not_duplicated=False
					print("ATTENZIONE: utente con IP "+idSession.ip+":"+str(idSession.port)+" gia' registrato!")
					idSession=ssdi
			
			if not_duplicated:
				idSession=Util.range(16)
				print( "Il nuovo session_id per utente con IP "+ip_deformatting.f_ipv4+":"+int(ip_deformatting.port)+" e': "+idSession)
				exstisLogged.dataBase[idSession]=ip_deformatting
			return idSession



