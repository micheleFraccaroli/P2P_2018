import sqlite3
import os
import Util
from Config import Config
import time
import subprocess as sub

class dataBase:

	def create(self,mode):

		if os.system('ls P2P.db 2>/dev/null 1>/dev/null') > 0: # Database mancante, lo creo

			config = Config()

			con = sqlite3.connect('P2P.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS config (name VARCHAR(20) NOT NULL, value VARCHAR(50) NOT NULL, PRIMARY KEY(name))')
			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS file (Sessionid VARCHAR(16), md5 VARCHAR(32) NOT NULL, name VARCHAR(100) NOT NULL,PRIMARY KEY(Sessionid, md5))')
			c.execute('CREATE TABLE IF NOT EXISTS requests (pid VARCHAR(16), ip VARCHAR(55), timeOperation FLOAT NOT NULL,PRIMARY KEY(pid,ip))')
			c.execute('CREATE TABLE IF NOT EXISTS responses (id INTEGER,pid VARCHAR(16) NOT NULL, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, md5 VARCHAR(32), name VARCHAR(100), PRIMARY KEY(id))')
			c.execute('CREATE TABLE IF NOT EXISTS peers (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS superPeers (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(ip))')

			root1 = Util.ip_formatting(config.root1V4,config.root1V6,config.root1P)
			root2 = Util.ip_formatting(config.root2V4,config.root2V6,config.root2P)

			try:

				# Vicini
				c.execute('INSERT INTO peers VALUES (?,?)',(root1[:55],root1[55:]))
				c.execute('INSERT INTO peers VALUES (?,?)',(root2[:55],root2[55:]))

				# Configurazione
				for el in config.__dict__:
					c.execute('INSERT INTO config VALUES (?,?)',(el,str(config.__dict__[el])))

				if mode == 'normal':

					c.execute('UPDATE config SET value = "1" WHERE name = "maxNear"')

				c.execute('INSERT INTO config VALUES ("mode",?)', (mode,))
				c.execute('INSERT INTO config VALUES ("sessionId","default")')

				con.commit()
			except:
				pass
			con.close()

			return ['OK', mode]

		else: # Database già esistente, riutilizzo le impostazioni

			Util.sessionId = self.retrieveConfig(('sessionId',))

			sessionMode = self.retrieveConfig(('mode',))

			if sessionMode == 'logged':

				if mode == 'normal':

					return ['LG', sessionMode]

				else:
					return ['ER', sessionMode]

			elif sessionMode == mode:

				return ['OK', mode]

			else:
				return ['ER', sessionMode]

	def destroy(self):

		os.system('rm -f P2P.db')

	def updateConfig(self, attr, value):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute("UPDATE config SET value = ? WHERE name = ?", (value, attr))

		con.commit()
		con.close()

	def retrieveAllConfig(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM config')
		res = c.fetchall()

		class Container(object):
			pass

		container = Container()
		for par in res:
			setattr(container,par[0],par[1])

		return container

	def retrieveConfig(self,lPars):

		if len(lPars) == 1:
			lPars = str(lPars)
			lPars = lPars.replace(',','') # Elimino la virgola dalla tupla con un solo elemento
		else:
			lPars = str(lPars)

		con = sqlite3.connect('P2P.db')
		c = con.cursor()
		#c.execute('SELECT * FROM config WHERE name IN ("mode")')
		c.execute('SELECT * FROM config WHERE name IN '+ lPars)
		res = c.fetchall()

		class Container(object):
			pass

		if len(res) > 1: # Ritorno un oggetto con gli attributi di config

			container = Container()
			for par in res:
				setattr(container,par[0],par[1])

			return container
		else: # Ritorno il singolo parametro richiesto
			return res[0][1]

	def insertPeers(self, ip, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM peers WHERE ip=?',(ip,))
		res = c.fetchone()

		if res == None:
			c.execute('INSERT INTO peers VALUES (?,?)',(ip,port))
			con.commit()

		con.close()

	def retrievePeers(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM peers')
		res = c.fetchall()

		con.close()

		return res

	def retrievePeerSid(self, sid):
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT ip, port FROM login WHERE idSession = ?', (sid) )
		res = c.fetchall()

		c.close()

		return res

	#def updatePeers(self):
	def deletePeers(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('DELETE FROM peers')

		con.commit()
		con.close()

	def insertSuperPeers(self, ip, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO superPeers VALUES(?,?)',(ip,port))

		con.commit()

		res = c.execute('SELECT value FROM config WHERE name = "maxNear"')
		maxNear = res.fetchone()

		c.execute('SELECT * FROM superPeers ORDER BY random() LIMIT ?',(maxNear))
		res = c.fetchall()

		resIp = tuple(resp[0] for resp in res)

		if len(resIp) == 1:
			resIp = str(resIp).replace(',','')
		else:
			resIp = str(resIp)

		c.execute('DELETE FROM superPeers WHERE ip NOT IN ' + resIp)

		con.commit()

		con.close()

	def retrieveSuperPeers(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		try:
			c.execute('SELECT * FROM superPeers')
			res = c.fetchall()
		except:
			pass

		con.close()

		return res

	def deleteSuperPeers(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('DELETE FROM superPeers')

		c.close()

	def insertRequest(self, pktid, ip, timeOp):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO requests VALUES (?,?,?)',(pktid, ip, timeOp))

		con.commit()
		con.close()

	def retrieveCounterRequest(self, pktid, ip):

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

	def insertResponse(self, pktid, ip, port, md5, name):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO responses VALUES (null, ?, ?, ?, ?, ?)', (pktid, ip, port, md5, name))

		con.commit()
		con.close()

	def retrieveResponse(self, pid, validTime): # validTime è config.timeResearch

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('SELECT pid, ip, port, md5, name, timeResponse FROM responses where pid = ? AND timeResponse < ?', (pid, validTime))
		res = c.fetchall()

		c.close()

		return res

class dataBaseSuper(dataBase):

	def existsLogged(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT count(*) FROM login')
		res = c.fetchone()
		con.close()

		return res[0]

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

	def insertID(self, ip, port, idSession):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, idSession))

		con.commit()
		con.close()

	def retrieveLOGIN(self, Sessionid):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('SELECT ip, port FROM login WHERE idSession = ?', (Sessionid,))
		res = c.fetchone()

		con.commit()
		con.close()

		return res

	def retrieveLOGINwithIP(self, ip, port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		res = c.execute('SELECT ip, port, idSession FROM login WHERE ip = ? and port = ?', (ip,port,))
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

	def retrieveFILE(self, Sessionid, md5):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT count(*) FROM file WHERE Sessionid=? AND md5=?',(Sessionid, md5))
		res = c.fetchone()
		con.close()

		return res[0]

	def findInLocalSP(self, search):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute("SELECT md5, name FROM file WHERE name LIKE '%?%'", (search))
		res = c.fetchall()

		con.commit()
		con.close()

		return res

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
		c2 = con.cursor()
		c3 = con.cursor()

		c.execute('SELECT count(*) FROM file WHERE Sessionid=?',(Sessionid,))
		res = c.fetchone()
		c2.execute('DELETE FROM file WHERE Sessionid = ?', (Sessionid,))
		c3.execute('DELETE FROM login WHERE idSession = ?', (Sessionid,))

		con.commit()
		con.close()
		return res[0]

	def searchFILEquer(self, search):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM file WHERE name LIKE "%?%"',(search,))
		res = c.fetchall()

		con.commit()
		con.close()

		return res

if __name__ == '__main__':
	print("faccio")
	c=dataBaseSuper()
	#c.destroy()
	c.create('normal')
	'''
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

	t = time.time()
	time.sleep(1)
	c.insertResponse('aaaaaaaaaaaaaaaa','172.16.8.1|fc00::8:1',500,'fhissbfksbfksabfkjefnkjsnfkj','Geme',time.time()-t)
	time.sleep(1)
	c.insertResponse('aaaaaaaaaaaaaaaa','172.16.8.1|fc00::8:1',500,'fhissbfksbfksabfkjefnkjsnfkj','Fracca',time.time()-t)
	time.sleep(1)
	c.insertResponse('aaaaaaaaaaaaaaaa','172.16.8.1|fc00::8:1',500,'fhissbfksbfksabfkjefnkjsnfkj','Ceso',time.time()-t)
	time.sleep(1)
	c.insertResponse('aaaaaaaaaaaaaaaa','172.16.8.1|fc00::8:1',500,'fhissbfksbfksabfkjefnkjsnfkj','Lucia',time.time()-t)

	res = c.retrieveResponse('aaaaaaaaaaaaaaaa',config.timeResearch)
	print('\n\n---RISPOSTE---\n\n')
	for re in res:
		print(re)

	c.insertSuperPeers('172.16.8.1',5000)
	c.insertSuperPeers('172.16.8.2',5000)
	c.insertSuperPeers('172.16.8.3',5000)
	c.insertSuperPeers('172.16.8.4',5000)
	c.insertSuperPeers('172.16.8.5',5000)
	c.insertSuperPeers('172.16.8.6',5000)
	c.insertSuperPeers('172.16.8.7',5000)
	c.insertSuperPeers('172.16.8.8',5000)
	r = c.retrieveSuperPeers(config.maxNear)

	b = ['172.16.8.9',5000]

	r.append(b)
	print('\n\n\n\n')
	for a in r:
		print(a)
	'''
	print('------------------------')
	config = c.retrieveConfig(('ttl','selfP','selfV4'))
	mod = c.retrieveConfig(('mode',))
	print('\n\n'+mod+'\n\n')
	c.updateConfig('mode','normall')
	mod = c.retrieveConfig(('mode',))
	print('\nNew:\n'+mod+'\n\n')


	mod = c.retrieveConfig(('sessionId',))
	print('\n\n'+mod+'\n\n')
	c.updateConfig('sessionId','test')
	mod = c.retrieveConfig(('sessionId',))
	print('\nNew:\n'+mod+'\n\n')

	print(config.ttl,config.selfP,config.selfV4)
