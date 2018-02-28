import socket

class Peer:

	def __init__(self):
		self.ip_dir = '192.168.1.106' #edit for presentation
		self.dir_port = 3000
		self.dir_addr = (self.ip_dir, self.dir_port)

		self.my_ipv4 = '192.168.1.102'
		self.my_ipv6 = 'fe80::ac89:c3f8:ea1a:ca4b'
		self.pPort = 50001 #peer port for receaving connection from other peer

	#-------- fase di login e logout con la directory --------

	def connection(self):
		try:
			#this is for ipv4 and ipv6
			self.infoS = socket.getaddrinfo(self.ip_dir, self.dir_port)
			self.s = socket.socket(*self.infoS[0][:3])
			self.s.connect(self.infoS[0][4])

			#self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#self.s.connect(self.dir_addr)
		except IOError, expt: #l'eccezione ha una sotto eccez. per la socket
			print ("Errore nella connessione alla directory --> " + expt)

	def deconnection(self):
		try:
			self.s.close()
		except IOError, expt: #l'eccezione ha una sotto eccez. per la socket
			print ("Errore nella connessione alla directory --> " + expt)

	def login(self):
		print("\n--- LOGIN ---\n")

		self.connection()

		#self.ipp2p_bf = self.s.getsockname()[0] #ip peer bad formatted
		
		#formattazione ip
		self.split_ip = self.my_ipv4.split(".")
		ip1 = self.split_ip[0].zfill(3)
		ip2 = self.split_ip[1].zfill(3)
		ip3 = self.split_ip[2].zfill(3)
		ip4 = self.split_ip[3].zfill(3)

		self.ipp2p = ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4

		#formattazione porta
		self.pp2p_bf = self.s.getsockname()[1]  #porta peer bad formatted
		self.pp2p = '%(#)03d' % {"#" : int(self.pp2p_bf)}

		data_login = "LOGI" + self.ipp2p + self.pp2p

		self.s.send(data_login.encode('ascii'))

		self.ack_login = self.s.recv(20) #4B di ALGI + 16B di SID
		#self.ack.decode('ascii')

		if (self.ack_login[:4] == "ALGI"):
			self.sid = self.ack_login[4:20]
			if (self.sid == '0000000000000000'):
				print("Errore durante il login\n")
				exit()
			else:	
				print("Session ID ---> " + self.sid + "\n")
		else:
			print("Errore del pacchetto, string 'ALGI' non trovata")
			exit()

		self.deconnection()

	def logout(self):
		print("\n--- LOGOUT ---\n")

		self.connection()

		data_logout = "LOGO" + self.sid

		self.s.send(data_logout.encode('ascii'))

		self.ack_logout = self.s.recv(7)

		if(self.ack_logout[:4] == "ALGO"):
			print("Numero di file eliminati ---> " + str(self.ack_logout[4:7]))

		self.deconnection()

	#---------------------------------------------