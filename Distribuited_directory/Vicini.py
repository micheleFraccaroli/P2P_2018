import Util
from Conn import Conn
from dataBase import dataBase

class Vicini:
	def __init__(self,config):
		rand=Util.ip_packet16()
		self.pack = 'NEAR' + rand + Util.ip_formatting(config.selfV4,config.selfV6,config.selfP) + str(config.ttl)

	def searchNeighborhood(self):

		dataBase = dataBase()
		nears = dataBase.retrieveNeighborhood()

		for near in nears:

			data = ip_deformatting(near[0],near[1],None)
			
			connRoot = Conn(data[0],data[1],data[2])
			connRoot.connection()
			connRoot.sed(self.pack.encode())
			connRoot.deconnection()

if __name__=='__main__':

	dataBase = dataBase()
	dataBase.create()
	nears = dataBase.retrieveNeighborhood()

	for near in nears:
		print(near[0])
		data = ip_deformatting(near[0],near[1],None)
		print(data)
		
		connRoot = Conn(data[0],data[1],data[2])
		connRoot.connection()
		connRoot.sed(self.pack.encode())
		connRoot.deconnection()