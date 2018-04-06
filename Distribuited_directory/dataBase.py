import sqlite3
import os
from Util
from Config import Config
import time
import subprocess as sub

class dataBase:

	def create(self,config):
		
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('CREATE TABLE IF NOT EXISTS requests (pid VARCHAR(16), ip VARCHAR(55), timeOperation FLOAT NOT NULL,PRIMARY KEY(pid,ip))')
		c.execute('CREATE TABLE IF NOT EXISTS responses (id INTEGER,pid VARCHAR(16) NOT NULL, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, md5 VARCHAR(32), name VARCHAR(100), PRIMARY KEY(id))')
		c.execute('CREATE TABLE IF NOT EXISTS neighborhood (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(ip))')

		root1 = Util.ip_formatting(config.root1V4,config.root1V6,config.root1P)
		root2 = Util.ip_formatting(config.root2V4,config.root2V6,config.root2P)
		
		try:
			c.execute('INSERT INTO neighborhood VALUES (null,?,?)',(root1[:55],root1[55:]))
			c.execute('INSERT INTO neighborhood VALUES (null,?,?)',(root2[:55],root2[55:]))
			con.commit()
		except:
			pass
		con.close()
	
	def destroy(self):

		try:
			sub.call(['rm','-f','P2P.db'])
		except:
			pass

	def retrieveNeighborhood(self,config):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT ip, port FROM neighborhood ORDER BY random() LIMIT 4')
		res = c.fetchall()
		
		resIp = list(resp[0] for resp in res)
		
		root1 = Util.ip_formatting(config.root1V4, config.root1V6, config.root1P)
		root2 = Util.ip_formatting(config.root2V4, config.root2V6, config.root2P)

		if root1[:len(root1)-5] not in resIp:
			resIp[0] = root1[:len(root1)-5]
		
		if root2[:len(root1)-5] not in resIp:
			resIp[1] = root2[:len(root1)-5]
		
		resId=tuple(resId)
		
		c.execute('DELETE FROM neighborhood WHERE ip NOT IN '+resIp)
		c.execute('SELECT ip, port FROM neighborhood')
		res = c.fetchall()

		con.commit()
		con.close()

		return res

	def retrieveAll(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM neighborhood')
		res = c.fetchall()
		c.close()
		return res

	def insertNeighborhood(self,ip,port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO neighborhood VALUES (?,?)',(ip,port))

		con.commit()
		con.close()

	def insertSearch(self, pktid, ip, timestamp):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('INSERT INTO requests VALUES (?,?,?)', (pktid, ip, timestamp))
		con.commit()
		con.close()

	def retrivenSearch(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('SELECT count(*) FROM requests WHERE pid=? AND ip=?',(pktid, ip))
		res = c.fetchone()
		con.close()
		return res[0]

	def retriveSearch(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('SELECT timeOperation FROM requests WHERE pid=? AND ip=?',(pktid, ip))
		res = c.fetchone()
		con.close()
		return res[0]

	def updateTimestamp(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		new_timestamp = time.time()
		c.execute('UPDATE requests SET timeOperation = ? WHERE pid=? AND ip=?',(new_timestamp, pktid, ip))
		con.commit()
		con.close()

	def insertRequest(self, pktid, ip, timeOp):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO requests VALUES (?,?,?)',(pktid, ip, timeOp))

		con.commit()
		con.close()
	
	def insertResponse(self, pktid, ip, port, md5, name):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO responses VALUES (null,?,?,?,?,?)',(pktid, ip, port, md5, name))

		con.commit()
		con.close()
	
	def retrieveResponses(self, pid):

			con = sqlite3.connect('P2P.db')
			c = con.cursor()

			res = c.execute('SELECT pid, ip, port, md5, name FROM responses where pid = "' + pid + '"')
			res = c.fetchall()
			c.close()

			return res
	
if __name__ == '__main__':
	print("faccio")
	config=Config()
	c=dataBase()
	c.destroy()
	c.create(config)

	c.insertNeighborhood('192.168.1.3',5600)
	c.insertNeighborhood('192.168.1.4',5601)
	c.insertNeighborhood('192.168.1.5',5602)
	c.insertNeighborhood('192.168.1.6',5603)
	c.insertNeighborhood('192.168.1.7',5604)
	c.insertNeighborhood('192.168.1.8',5605)
	c.insertNeighborhood('192.168.1.9',5606)
	c.insertNeighborhood('192.168.1.10',5607)
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])
	print('\n\n\n')
	vicini=c.retrieveNeighborhood()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ')
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])