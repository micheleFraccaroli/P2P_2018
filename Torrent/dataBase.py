import sqlite3 as s3
import math

class dataBase:
	def __init__(self):

		def create(self):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS interested (id INTEGER, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, partList VARCHAR(300) NOT NULL,PRIMARY KEY(id))')
			c.execute('CREATE TABLE IF NOT EXISTS f_in (md5 VARCHAR(32), id INTEGER), FOREIGN KEY(md5) REFERENCES file(md5), FOREIGN KEY(id) REFERENCES interested(id)')
			c.execute('CREATE TABLE IF NOT EXISTS file (sessionid VARCHAR(16) NOT NULL, md5 VARCHAR(32) NOT NULL, name VARCHAR(100), lenfile INTEGER(10), lenpart INTEGER(6), npart INTEGER(8),PRIMARY KEY(sessionid, md5))')

			con.commit()
			con.close()

		def login(self, ip, port, sid):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, sid))

			con.commit()
			con.close()

		def getIDf_in(self, md5):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			hitpeer = c.execute('SELECT COUNT(*) FROM f_in WHERE md5 = ?', (md5,))
			hitpeer = c.fetchone()
			id_list = c.execute('SELECT id FROM f_in WHERE md5 = ?', (md5,))
			id_list = c.fetchall()

			con.close()

			return hitpeer, id_list

		def getInterestedPartList(self,id):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()
			id_list = []

			for n in id:
				id_list.append(n[0])	
			
			tup = tuple(id_list)

			dict_ip_part = {}
			if(len(tup) > 1):
				res = c.execute('SELECT ip, port, partList FROM interested WHERE id IN ' + str(tup))
				res = c.fetchall()
				for i in res:
					ip = i[0] + i[1]
					dict_ip_part[ip] = i[2]1
			elif(len(tup) == 1):
				res = c.execute('SELECT ip, port, partList FROM interested WHERE id = ' + str(tup[0]))
				res = c.fetchall()
				ip = res[0] + res[1]
				dict_ip_part[ip] = res[2]

			con.close()
			return dict_ip_part

		def insert_file(self, sessionid, md5, name, lenfile, lenpart):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()
			npart = math.ceil((lenfile/lenpart))

			res = c.execute('INSERT INTO file VALUES(?,?,?,?,?,?)', (sessionid, md5, name, lenfile, lenpart, npart))

			con.commit()
			con.close()
			return str(npart)

		def insertInterested(self, ip, port, npart):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			partList = '1'*(8*npart)

			res = c.execute('INSERT INTO interested VALUES()')