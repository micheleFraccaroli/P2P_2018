import Util
from Conn import Conn
from dataBase import dataBase

class Vicini:
	def __init__(self,config, port):
		rand=Util.ip_packet16()
		self.pack = 'NEAR' + rand + Util.ip_formatting(config.selfV4,config.selfV6,port) + str(config.ttl).zfill(2)
		self.config = config

	def searchNeighborhood(self):
		db = dataBase()
		nears = db.retrieveNeighborhood(self.config)
		
		for near in nears:
			data = Util.ip_deformatting(near[0],near[1],None)
			connRoot = Conn(data[0],data[1],data[2])
			connRoot.connection()
			connRoot.s.send(self.pack.encode())
			connRoot.deconnection()