import sqlite3 as s3

class dataBase:
	def __init__(self):

		def create(self):
			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('CREATE TABLE IF NOT EXISTS login (ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, idSession VARCHAR(16) NOT NULL,PRIMARY KEY(ip))')
			c.execute('CREATE TABLE IF NOT EXISTS interested (id INTEGER, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, partList VARCHAR(300) NOT NULL,PRIMARY KEY(id))')
			c.execute('CREATE TABLE IF NOT EXISTS f_in (md5 VARCHAR(32), id INTEGER), FOREIGN KEY(md5) REFERENCES file(md5), FOREIGN KEY(id) REFERENCES interested(id)')

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

			res0 = c.execute('SELECT COUNT(*) FROM f_in WHERE md5 = ?', (md5,))
			res0 = c.fetchone()
			res1 = c.execute('SELECT id FROM f_in WHERE md5 = ?', (md5,))
			res1 = c.fetchall()

			con.close()

			return res0, res1

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
					dict_ip_part[i[0]] = i[2]
			elif(len(tup) == 1):
				res = c.execute('SELECT ip, port, partList FROM interested WHERE id = ' + str(tup[0]))
				res = c.fetchall()
				dict_ip_part[res[0]] = res[2]

			con.close()
			return dict_ip_part