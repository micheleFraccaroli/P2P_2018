import sqlite3 as s3
import math

class dataBase:
	def __init__(self):

		def create(self):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS file (sessionid VARCHAR(16) NOT NULL, md5 VARCHAR(32) NOT NULL, name VARCHAR(100), lenfile INTEGER(10), lenpart INTEGER(6), npart INTEGER(8),PRIMARY KEY(sessionid, md5))')
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

			res = c.execute('INSERT INTO file VALUES(?,?,?,?,?,?)', (sessionid, md5, name, lenfile, lenpart, npart))

			con.commit()
			con.close()
			return str(npart)
