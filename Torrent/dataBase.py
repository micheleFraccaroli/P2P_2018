import sqlite3 as s3
import math

class dataBase:
	def __init__(self):

		def create(self):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS file (sessionid VARCHAR(16) NOT NULL, md5 VARCHAR(32) NOT NULL, name VARCHAR(100), lenfile VARCHAR(10), lenpart VARCHAR(6), npart VARCHAR(8),PRIMARY KEY(sessionid, md5))')
			con.commit()
			con.close()

		def login(self, ip, port, sid):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, sid))

			con.commit()
			con.close()

		def insert_file(self, sessionid, md5, name, lenfile, lenpart):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()
			npart = math.ceil((lenfile/lenpart))

			c.execute('INSERT INTO file VALUES(?,?,?,?,?,?)', (sessionid, md5, name, lenfile, lenpart, str(npart).zfill(8)))

			con.commit()
			con.close()
			return str(npart).zfill(8)

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

			c.execute('UPDATE file SET name = ?, lenfile = ?, lenpart = ?, npart = ?,  WHERE md5 = ? AND sessionid = ?', (name, lenfile, lenpart, npart, md5, sessionid))

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
