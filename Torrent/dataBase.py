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
			c.execute('CREATE TABLE IF NOT EXISTS f_in (md5 VARCHAR(32), sid VARCHAR(16), FOREIGN KEY(md5) REFERENCES file(md5))')
			c.execute('CREATE TABLE IF NOT EXISTS bitmapping (md5 VARCHAR(32) NOT NULL, sid VARCHAR(16) NOT NULL, bits INTEGER NOT NULL, FOREIGN KEY(md5) REFERENCES file)')
			# Configurazione
			for el in config.__dict__:
				c.execute('INSERT INTO config VALUES (?,?)',(el,str(config.__dict__[el])))

			c.execute('INSERT INTO config VALUES ("mode",?)', (mode,))
			c.execute('INSERT INTO config VALUES ("sessionId","default")')

			con.commit()
			con.close()
			#print(mode,mode)

			return ['OK', mode]

		else: # Database già esistente, riutilizzo le impostazioni

			Util.sessionId = self.retrieveConfig(('sessionId',))

			sessionMode = self.retrieveConfig(('mode',))

			if sessionMode == mode:

				return ['OK', mode]

			else:
				return ['ER', sessionMode]

	def retrieveConfig(self,lPars):

		if len(lPars) == 1:
			lPars = str(lPars)
			lPars = lPars.replace(',','') # Elimino la virgola dalla tupla con un solo elemento
		else:
			lPars = str(lPars)

		con = s3.connect('TorrentDB.db')
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

	def updateConfig(self, attr, value):

		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute("UPDATE config SET value = ? WHERE name = ?", (value, attr))

		con.commit()
		con.close()

	def login(self, ip, port, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		try:
			res = c.execute('INSERT INTO login VALUES (?,?,?)', (ip, port, sid))
		except:
			Util.printLog("Just logged!")

		con.commit()
		con.close()

	def getHitpeer(self, md5, my_sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		hitpeer = c.execute('SELECT count(DISTINCT sid) FROM bitmapping WHERE md5 = ? and sid <> ?', (md5,my_sid))
		hitpeer = c.fetchone()

		con.close()

		return hitpeer[0]

	def insertBitmapping(self, md5, sid, bits):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT COUNT(*) FROM bitmapping WHERE md5 = ? AND sid = ?',(md5,sid))
		cc = c.fetchone()

		if(cc[0] == 0):
			query = 'INSERT INTO bitmapping VALUES('
			for b in bits:
				query = query + '"' + md5 + '","' + sid + '",' + str(b) + '),('

			query = query[:len(query)-2]
			c.execute(query)

			con.commit()
			con.close()

	def retrieveBits(self, md5, sid, part):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()
		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ? LIMIT 1 OFFSET ?', (md5, sid, part))
		res = c.fetchone()

		con.close()
		return res[0]

	def getBitmapping(self,sid, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ? ORDER BY sid', (md5, sid))
		res = c.fetchall()
		#print("Ritorno della query dei bits ---> " + str(res))
		con.close()
		return res

	def getPeerBySid(self, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT ip, port FROM login WHERE idSession = ?', (sid,))
		res = c.fetchone()

		con.close()
		return res

	def getInterestedPeers(self, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT sid FROM f_in WHERE md5 = ?', (md5,))
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

	def insertInterested(self, sid, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('INSERT INTO f_in VALUES(?,?)',(md5, sid))

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


	def updatePart(self, part, md5, sid, updated):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ?', (md5, sid))
		res = c.fetchall()

		#part = partNum//8
		#print("part database -->" + str(part))
		toUpdate = res[part][0]
		#print("toUpdate database ---> " + str(toUpdate))
		c.execute('UPDATE bitmapping SET bits = ? WHERE md5 = ? AND sid = ? LIMIT 1 OFFSET ?', (updated, md5, sid, part))

		con.commit()
		con.close()

		#return str(npart).zfill(8)

	def search_files(self, string, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT count(DISTINCT md5) FROM file WHERE name LIKE ? AND sessionid <> ?', ('%'+string.strip()+'%',sid))
		nmd5 = c.fetchone()

		c.execute('SELECT md5, name, lenfile, lenpart FROM file WHERE name LIKE ? AND sessionid <> ? ORDER BY md5', ('%'+string.strip()+'%',sid))
		file = c.fetchall()

		con.close()
		return nmd5[0], file

	def retrieveInfoFile(self, md5):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('SELECT npart, lenfile, lenpart, name FROM file WHERE md5 = ?', (md5,))
		res = c.fetchone()

		con.close()
		return res

	def deleteAll(self, sid=None):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		if sid != None:
			
			c.execute('DELETE FROM login WHERE idSession = ?', (sid,))
			c.execute('DELETE FROM f_in WHERE sid = ?', (sid,))
			c.execute('DELETE FROM bitmapping WHERE sid = ?', (sid,))
			c.execute('DELETE FROM file WHERE sessionid = ?', (sid,))
		
		else:

			c.execute('DELETE FROM login; DELETE FROM f_in; DELETE FROM bitmapping; DELETE FROM file')
		
		con.commit()

		con.close()

	def checkLogout(self, sid):

			con = s3.connect('TorrentDB.db')
			c = con.cursor()

			c.execute('SELECT md5 FROM file WHERE sessionid = "' + sid + '"')
			res = c.fetchall()

			partdown = 0
			partdown_final = 0

			if(res):
				#print(res)
				for md5 in res:
					Util.printLog("md5 --> " + str(md5))
					c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ?', (md5[0], sid))
					my = c.fetchall()
					my_l = []
					for m in my:
						my_l.append(m[0])
					Util.printLog("mio --> " + str(my_l))

					c.execute('SELECT sid FROM f_in WHERE md5 = "' + md5[0] + '" AND sid <> "' + sid + '"')
					res2 = c.fetchall()
					Util.printLog("sid interessati --> " + str(res2))
					list_matching = []
					for sidf in res2:
						c.execute('SELECT bits FROM bitmapping WHERE md5 = ? AND sid = ?', (md5[0], sidf[0]))
						st = c.fetchall()
						list_matching.append(st)
					i = 0
					k = 0
					buffer = []
					buffer_in = []
					Util.printLog("\nlist_matching ---> " + str(list_matching))
					if(list_matching):
						for r in list_matching[0]:
							for lm in range(len(list_matching)):
								buffer_in.append(list_matching[lm][i][0])
							Util.printLog("buffer_in ---> " + str(buffer_in))
							i = i + 1
							buffer.append(buffer_in)
							buffer_in = []

					j = 0
					buf_res_list = []
					Util.printLog("buffer ---> " + str(buffer))
					for buf in buffer:
						buf_res = 0
						for b in range(len(buf)):
							Util.printLog("b " + str(b))
							Util.printLog("buf[b] ---> " + str(buf[b]))
							buf_res = buf_res | buf[b]
							Util.printLog("buf_res " + str(buf_res))
							partdown = bin(buf_res)[2:].count('1')

						partdown_final = partdown_final + partdown		
						Util.printLog("partdown_final ---> " + str(partdown_final))

						buf_res_list.append(buf_res)
						Util.printLog("buf_res_list ---> " + str(buf_res_list))
						j = j + 1

				if(my_l != buf_res_list):
					return "NLOG", partdown_final
				else:
					self.deleteAll(sid)
					return "ALOG", partdown_final
			else:
				self.deleteAll(sid)

				return "ALOG", partdown_final

	# login del peer
	def insertSid(self, sid):
		con = s3.connect('TorrentDB.db')
		c = con.cursor()

		c.execute('INSERT INTO config VALUES("sid", ?)', (sid,))

		con.commit()
		con.close()

	def checkLogged(self):
		con = s3.connect("TorrentDB.db")
		c = con.cursor()

		c.execute("SELECT ip, port FROM login")
		res = c.fetchall()



		con.close()
		return res

if __name__ == "__main__":
	db = dataBase()
	db.create("tracker")
