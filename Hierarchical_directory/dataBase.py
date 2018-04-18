import sqlite3
import os
import Util
from Config import Config
import time
import subprocess as sub

class dataBase:

	def create(self, config):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55)NOT NULL, port VARCHAR(5)NOT NULL, idSession NOT NULL,PRIMARY KEY(ip))')
		c.execute('CREATE TABLE IF NOT EXISTS file (Sessionid VARCHAR(16), md5 VARCHAR(32) NOT NULL, name VARCHAR(100) NOT NULL,PRIMARY KEY(Sessionid, md5))')
		c.execute('CREATE TABLE IF NOT EXISTS requests (pid VARCHAR(16), ip VARCHAR(55), timeOperation FLOAT NOT NULL,PRIMARY KEY(pid,ip))')
		c.execute('CREATE TABLE IF NOT EXISTS responses (id INTEGER,pid VARCHAR(16) NOT NULL, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, md5 VARCHAR(32), name VARCHAR(100), timeResponse FLOAT NOT NULL, PRIMARY KEY(id))')
		c.execute('CREATE TABLE IF NOT EXISTS peers (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(ip))')
		c.execute('CREATE TABLE IF NOT EXISTS superPeers (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(ip))')

		root1 = Util.ip_formatting(config.root1V4,config.root1V6,config.root1P)
		root2 = Util.ip_formatting(config.root2V4,config.root2V6,config.root2P)

		try:
			c.execute('INSERT INTO peers VALUES (?,?)',(root1[:55],root1[55:]))
			c.execute('INSERT INTO peers VALUES (?,?)',(root2[:55],root2[55:]))
			con.commit()
		except:
			pass
		con.close()

	def destroy(self):

		try:
			sub.call(['rm','-f','P2P.db'])
		except:
			pass

	def insertPeers(self, ip, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM peers WHERE ip=?',(ip,))
		res = c.fetchone()

		if res == None:
			c.execute('INSERT INTO peers VALUES (?,?)',(ip,port))
			con.commit()

		con.close()

	def retrievePeers(self, config):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM peers')
		res = c.fetchall()

		con.close()

		return res

	def updatePeers(self):


	def insertSuperPeers(self, ip, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		try:
			c.execute('INSERT INTO superPeers VALUES(?,?)',(ip,port))
		except:
			pass

	def retrieveSuperPeers(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM superPeers ORDER BY random() LIMIT ?',(config.maxNear,))
		res = c.fetchall()

		c.execute('DELETE FROM superPeers WHERE ip NOT IN ?',(str(res),))
		c.execute('SELECT * FROM superPeers')
		res = c.fetchall()

		con.commit()
		con.close()

		return res

	def retrieveAll(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM peers')
		res = c.fetchall()

		c.close()

		return res

	def insertRequest(self, pktid, ip, timeOp):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO requests VALUES (?,?,?)',(pktid, ip, timeOp))

		con.commit()
		con.close()

	def retriveCounterRequest(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('SELECT count(*) FROM requests WHERE pid = ? AND ip = ?',(pktid, ip))
		res = c.fetchone()

		con.close()

		return res[0]

	def retrieveRequestTimestamp(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		c.execute('SELECT timeOperation FROM requests WHERE pid = ? AND ip = ?',(pktid, ip))
		res = c.fetchone()

		con.close()

		return res[0]

	def updateTimestamp(self, pktid, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		new_timestamp = time.time()
		c.execute('UPDATE requests SET timeOperation = ? WHERE pid = ? AND ip = ?', (new_timestamp, pktid, ip))

		con.commit()
		con.close()

	def insertResponse(self, pktid, ip, port, md5, name, timeResp):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO responses VALUES (null,?,?,?,?,?,?)', (pktid, ip, port, md5, name, timeResp))

		con.commit()
		con.close()

	def retrieveResponse(self, pid):

			con = sqlite3.connect('P2P.db')
			c = con.cursor()

			res = c.execute('SELECT pid, ip, port, md5, name, timeResp FROM responses where pid = ?', (pid,))
			res = c.fetchall()

			c.close()

			return res

class dataBaseSuper(dataBase):

	def retrieveID(self, ip):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('SELECT idSession FROM login WHERE ip = ?', (ip,))
		res = c.fetchone()

		con.close()

		if res:
			return res[0]
		else:
			return None

	def insertID(self, ip, idSession, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, idSession))

		con.commit()
		con.close()

	def retriveINFO(self, Sessionid):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('SELECT ip, port FROM login WHERE idSession = ?', (Sessionid,))
		res = c.fetchone()

		con.commit()
		con.close()

		return res

	def insertFILE(self, Sessionid, md5, filename):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('INSERT INTO file VALUES(?,?,?)', (Sessionid, md5, filename))

		con.commit()
		con.close()

	def retriveFILE(self, Sessionid, md5):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT count(*) FROM file WHERE Sessionid=? AND md5=?',(Sessionid, md5))
		res = c.fetchone()
		con.close()

		return res[0]

	def updateFILE(self, filename, md5):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('UPDATE file SET name = ? WHERE md5 = ?', (filename, md5))

		con.commit()
		con.close()

	def deleteFILE(self, Sessionid, md5):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('DELETE FROM file WHERE Sessionid = ? AND md5 = ?', (Sessionid, md5))

		con.commit()
		con.close()

	def deleteFROMpeer(self, Sessionid):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT count(*) FROM file WHERE Sessionid=?',(Sessionid,))
		res = c.fetchone()
		c.execute('DELETE FROM file WHERE Sessionid = ?', (Sessionid,))

		con.commit()
		con.close()
		return res[0]

if __name__ == '__main__':
	print("faccio")
	config=Config()
	c=dataBaseSuper()
	c.destroy()
	c.create(config)

	c.insertPeers('192.168.1.3',5600)
	c.insertPeers('192.168.1.4',5601)
	c.insertPeers('192.168.1.5',5602)
	c.insertPeers('192.168.1.6',5603)
	c.insertPeers('192.168.1.7',5604)
	c.insertPeers('192.168.1.8',5605)
	c.insertPeers('192.168.1.9',5606)
	c.insertPeers('192.168.1.10',5607)

	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])
	print('\n\n\n')
	vicini=c.retrievePeers()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ')
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])

	for i in range(4):
		res = c.retrieveID('172.168.1.1')
		if not res:
			print('---'+str(res)+'---')
			c.insertID('172.168.1.1','111100001')
		else:
			print('ID ::: ',res)
'''
