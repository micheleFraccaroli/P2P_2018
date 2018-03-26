import sqlite3
import os

class dataBase:

	def create(self):

		errors=self.set()
		
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('CREATE TABLE errors (errno INTEGER, errStr VARCHAR(255) NOT NULL, PRIMARY KEY(errno))')
		c.execute('CREATE TABLE requests (pid VARCHAR(16), ip VARCHAR(55), timeOperation FLOAT NOT NULL,PRIMARY KEY(pid,ip))')
		c.execute('CREATE TABLE responses (id INTEGER, pid VARCHAR(16) NOT NULL, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, md5 VARCHAR(32), name VARCHAR(100), PRIMARY KEY(id))')
		c.execute('CREATE TABLE neighborhood (id INTEGER, ip VARCHAR(55) NOT NULL, port VARCHAR(5) NOT NULL, PRIMARY KEY(id))')
		
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

		c.execute('SELECT ip, port FROM neighborhood ORDER BY random() LIMIT 4')
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
		c.close()
		return res

	def insertNeighborhood(self,ip,port):

		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO neighborhood VALUES (null,?,?)',(ip,port))

		con.commit()
		con.close()

	def insertRequest(self, pktid, ip, port, timeOp):
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO requests VALUES (?,?,?)',(pktid, ip, timeOp))

		con.commit()
		con.close()
	
	def insertResponse(self, pktid, ip, port, md5, name):
		con = sqlite3.connect('P2P.db')
		c = con.cursor()

		c.execute('INSERT INTO responses VALUES (null,?,?,?,?,?)',(pktid, ip, port, md5, name))

		con.commit()
		con.close()
	
	def retrieveResponses(self, pid):
			con = sqlite3.connect('P2P.db')
			c = con.cursor()

			res = c.execute('SELECT pid, ip, port, md5, name FROM responses where pid = "' + pid + '"')
			res = c.fetchall()
			c.close()

			return res
	

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
		print('id ',vicino[0],' ip ',vicino[1],' porta ')
	print('\n\n\n')
	vicini=c.retrieveAll()
	for vicino in vicini:
		print('id ',vicino[0],' ip ',vicino[1],' porta ',vicino[2])

	c.insertRequest('qywterdf3546rteg', '172.16.8.3|fc00::8:3', 50003, 301.46)
	c.insertResponse('qywterdf3546rteg', '172.16.8.3|fc00::8:3', 50003,'1ewr34etdfcgvscedret45362718uytr', 'file.jpg')
	
	responses = c.retrieveResponses('qywterdf3546rteg')

	for res in responses:
    		print("pid: " + res[0] + " ip: " + res[1] + " port: " + str(res[2]) + " md5: " + res[3] + " name: " + res[4])
	
	del c