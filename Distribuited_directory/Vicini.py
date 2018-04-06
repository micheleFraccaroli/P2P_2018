import Util
from Conn import Conn
from dataBase import dataBase

class Vicini:
	def __init__(self,config, port):
		rand=Util.ip_packet16()
		self.pack = 'NEAR' + rand + Util.ip_formatting(config.selfV4,config.selfV6,port) + str(config.ttl).zfill(2)

	def searchNeighborhood(self):

		db = dataBase()
		nears = db.retrieveNeighborhood()
		
		for near in nears:
			Util.printLog("NEAR ------")
			Util.printLog(str(near))
			Util.printLog(self.pack)
			Util.printLog("-----------")
			data = Util.ip_deformatting(near[0],near[1],None)
			connRoot = Conn(data[0],data[1],data[2])
			connRoot.connection()
			connRoot.s.send(self.pack.encode())
			connRoot.deconnection()

'''
if __name__=='__main__':

	dataBase = dataBase()
	dataBase.create()
	nears = dataBase.retrieveNeighborhood()

	for near in nears:
		Util.printLog(str(near[0]))
		data = ip_deformatting(near[0],near[1],None)
		Util.printLog(str(data))
		
		connRoot = Conn(data[0],data[1],data[2])
		connRoot.connection()
		connRoot.s.send(self.pack.encode())
		connRoot.deconnection()
'''