import Util
from Config import Config
import sqlite3 as s3
import math
from pathlib import Path

class dataBase:

	def create(self, mode):

		if not Path('TorrentDB.db').is_file():

			config = Config()

			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS file (sessionid VARCHAR(16) NOT NULL, md5 VARCHAR(32) NOT NULL, name VARCHAR(100), lenfile INTEGER, lenpart INTEGER, npart INTEGER,PRIMARY KEY(sessionid, md5))')
			c.execute('CREATE TABLE IF NOT EXISTS config (name VARCHAR(20) NOT NULL, value VARCHAR(50) NOT NULL, PRIMARY KEY(name))')
			c.execute('CREATE TABLE IF NOT EXISTS f_in (md5 VARCHAR(32), sid VARCHAR(16), FOREIGN KEY(md5) REFERENCES file(md5), FOREIGN KEY(id) REFERENCES interested(id))')
			c.execute('CREATE TABLE IF NOT EXISTS bitmapping (id INTEGER, md5 VARCHAR(32) NOT NULL, sid VARCHAR(16) NOT NULL, bits INTEGER NOT NULL, FOREIGN KEY(md5) REFERENCES file, FOREIGN KEY(sid) REFERENCES interested)')
			# Configurazione
			for el in config.__dict__:
				c.execute('INSERT INTO config VALUES (?,?)',(el,str(config.__dict__[el])))

			c.execute('INSERT INTO config VALUES ("mode",?)', (mode,))
			c.execute('INSERT INTO config VALUES ("sessionId","default")')

			con.commit()
			con.close()

		else: # Database già esistente, riutilizzo le impostazioni

			Util.sessionId = self.retrieveConfig(('sessionId',))

			sessionMode = self.retrieveConfig(('mode',))

			if sessionMode == mode:

				return ['OK', mode]

			else:
				return ['ER', sessionMode]

	def login(self, ip, port, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, sid))

		con.commit()
		con.close()

	def getHitpeer(self, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		hitpeer = c.execute('SELECT COUNT(*) FROM f_in WHERE md5 = ?', (md5,))
		hitpeer = c.fetchone()

		con.close()

		return hitpeer[0]

	def insertBitmapping(self, md5, sid, bits):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		query = 'INSERT INTO bitmapping VALUES('

		for b in bits:
			query = query + md5 + sid + b + '),'

		query = query[:len(query)-1]

		c.execute(query)

		con.commit()
		con.close()

	def retrieveBits(self, md5, sid, part):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ? LIMIT 1 OFFSET ?', (md5, sid, (part-1)))
		res = c.fetchone()

		con.close()
		return res[0]

	def getBitmapping(self,sid, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ? ORDER BY sid', (md5, sid))
		res = c.fetchall()

		con.close()
		return res

	def getPeerBySid(self, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT ip, port FROM login WHERE idSession = ' + sid)
		res = c.fetchone()

		con.close()
		return res

	def getInterestedPeers(self, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT sid FROM f_in WHERE md5 = ' + md5)
		sid_int = c.fetchall()

		con.close()
		return sid_int

	def insert_file(self, sessionid, md5, name, lenfile, lenpart):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()
		npart = math.ceil((lenfile/lenpart))

		c.execute('INSERT INTO file VALUES(?,?,?,?,?,?)', (sessionid, md5, name, lenfile, lenpart, npart))

		con.commit()
		con.close()
		return str(npart).zfill(8)

	def insertInterested(self, sid, ip, port):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('INSERT INTO interested VALUES(?,?,?)',(sid,ip,port))

		con.commit()
		con.close()

	def check_file(self, sessionid, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT count(*) FROM file WHERE sessionid=? AND md5=?',(sessionid, md5))
		res = c.fetchone()

		con.commit()
		con.close()
		return res[0]

	def update_file(self, sessionid, md5, name, lenfile, lenpart):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()
		npart = math.ceil((lenfile/lenpart))

		c.execute('UPDATE file SET name = ?, lenfile = ?, lenpart = ?, npart = ?  WHERE md5 = ? AND sessionid = ?', (name, lenfile, lenpart, npart, md5, sessionid))

		con.commit()
		con.close()
		return str(npart).zfill(8)


	def updatePart(self, partNum, md5, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ?', (md5, sid))
		res = c.fetchall()

		part = partNum//8
		toUpdate = res[part][0]
		Updated = '' # bit aggiornati
		c.execute('UPDATE bitmapping SET bits = ? WHERE bits = ?', (Updated, toUpdate))

		con.commit()
		con.close()

		return str(npart).zfill(8)

	def search_files(self, string):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT count(DISTINCT md5) FROM file WHERE name LIKE ?', ('%'+string.strip()+'%',))
		nmd5 = c.fetchone()

		c.execute('SELECT md5, name, lenfile, lenpart FROM file WHERE name LIKE ? ORDER BY md5', ('%'+string.strip()+'%',))
		file = c.fetchall()

		con.close()
		return nmd5[0], file

	def retrieveInfoFile(self, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT lenfile, lenpart FROM file WHERE ms5 = ' + md5)
		res = c.fetchone()

		con.close()
		return res
