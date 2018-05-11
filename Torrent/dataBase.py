import sqlite3 as s3
import math

class dataBase:
	def __init__(self):

		def create(self):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS interested (sid VARCHAR(16), ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL,PRIMARY KEY(id))')
			c.execute('CREATE TABLE IF NOT EXISTS f_in (md5 VARCHAR(32), sid VARCHAR(16), FOREIGN KEY(md5) REFERENCES file(md5), FOREIGN KEY(id) REFERENCES interested(id)')
			c.execute('CREATE TABLE IF NOT EXISTS file (sessionid VARCHAR(16) NOT NULL, md5 VARCHAR(32) NOT NULL, name VARCHAR(100), lenfile INTEGER(10), lenpart INTEGER(6), npart INTEGER(8),PRIMARY KEY(sessionid, md5))')
			c.execute('CREATE TABLE IF NOT EXISTS bitmapping (id INTEGER, md5 VARCHAR(32) NOT NULL, sid VARCHAR(16) NOT NULL, bits INTEGER NOT NULL, FOREIGN KEY(md5) REFERENCES file, FOREIGN KEY(sid) REFERENCES interested)')

			con.commit()
			con.close()

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

			return hitpeer

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

			res = c.execute('INSERT INTO file VALUES(?,?,?,?,?,?)', (sessionid, md5, name, lenfile, lenpart, npart))

			con.commit()
			con.close()
			return str(npart)

		def insertInterested(self, sid, ip, port):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('INSERT INTO interested VALUES(?,?,?)',(sid,ip,port))

			con.commit()
			con.close()

		def search_file(self, sessionid, md5):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			res = c.execute('SELECT count(*) FROM file WHERE sessionid=? AND md5=?',(sessionid, md5))

			con.commit()
			con.close()
			return res[0]

		def update_file(self, sessionid, md5, name, lenfile, lenpart):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()
			npart = math.ceil((lenfile/lenpart))

			res = c.execute('UPDATE file SET name = ?, lenfile = ?, lenpart = ?, npart = ?,  WHERE md5 = ? AND sessionid = ?', (name, lenfile, lenpart, npart, md5, sessionid))

			con.commit()
			con.close()
			return str(npart)

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