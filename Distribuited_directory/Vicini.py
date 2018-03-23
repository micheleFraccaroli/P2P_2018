import Util
from Conn import Conn

class Vicini:
	def __init__(self,config):

		rand=Util.ip_packet16()
		self.pack = 'NEAR' + rand + Util.ip_formatting(config.selfV4,config.selfV6,config.selfP) + str(config.ttl)

	def cercaVicini(self,config):

		connRoot1 = Conn(config.listNode[0][0],config.listNode[0][1],config.listNode[0][2])
		connRoot2 = Conn(config.listNode[1][0],config.listNode[1][1],config.listNode[1][2])

		connRoot1.connection()
		connRoot2.connection()

		connRoot1.send(self.pack.encode())
		connRoot2.send(self.pack.encode())

		connRoot1.deconnection()
		connRoot2.deconnection()