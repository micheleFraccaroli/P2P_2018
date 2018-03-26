import sqlite3
import os

class dataBase:

	def create(self):

		errors=self.set()
		
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('CREATE TABLE IF NOT EXISTS errors (errno INTEGER, errStr VARCHAR(255) NOT NULL, PRIMARY KEY(errno))')
		c.execute('CREATE TABLE IF NOT EXISTS requests (pid VARCHAR(16), ip VARCHAR(55), timeOperation FLOAT NOT NULL,PRIMARY KEY(pid,ip))')
		c.execute('CREATE TABLE IF NOT EXISTS responses (pid VARCHAR(16) NOT NULL, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, md5 VARCHAR(32), name VARCHAR(100), PRIMARY KEY(pid,ip))')
		c.execute('CREATE TABLE IF NOT EXISTS neighborhood (id INTEGER, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(id))')
		
		c.executemany("INSERT INTO errors VALUES (?,?)",errors)
		c.execute("INSERT INTO neighborhood VALUES (1,'192.168.1.1',5000)")
		c.execute("INSERT INTO neighborhood VALUES (2,'192.168.1.2',5001)")

		con.commit()
		con.close()
	
	def destroy(self):

		os.system('rm P2P.db')

	def set(self):
		return	[
					(2,'File non trovato'),
					(13,'Accesso negato alla risorsa')
			]

	def retrievErrno(self,errno):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT errStr FROM errors WHERE errno = '+str(errno))
		return c.fetchone()[0]

	def retrieveNeighborhood(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM neighborhood ORDER BY random() LIMIT 4')
		res = c.fetchall()
		resId = list(res[0] for res in res)
		print(resId)
		if 1 not in resId:
			resId[0] = 1
		if 2 not in resId:
			resId[1] = 2
		resId=tuple(resId)
		print(resId)
		c.execute('DELETE FROM neighborhood WHERE id NOT IN '+str(resId))

		con.commit()
		con.close()
		#print('culo ',[res[0] for res in res])
		return res

	def retrieveAll(self):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('SELECT * FROM neighborhood')
		res = c.fetchall()
		#print('culo ',[res[0] for res in res])
		return res

	def insertNeighborhood(self,ip,port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO neighborhood VALUES (null,?,?)',(ip,port))

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


if __name__ == '__main__':
	print("faccio")
	c=dataBase()
	c.destroy()
	c.create()
	errno=c.retrievErrno(13)
	print(errno)
	c.insertNeighborhood('192.168.1.3',5600)
	c.insertNeighborhood('192.168.1.4',5601)
	c.insertNeighborhood('192.168.1.5',5602)
	c.insertNeighborhood('192.168.1.6',5603)
	
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])
	print('\n\n\n')
	vicini=c.retrieveNeighborhood()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])

	del c