from threading import *
from Conn import Conn
import curses
import Util

#Thread che gestisce la prima parte della ricerca, ovvero l'invio della LOOK da parte del peer, una volta svolti i test
#va implementata nel file RF.py, al pkt sono stati omessi i 4Bytes di intestazione solo per dei testi, ricorda di metterli
#manca anche la gestione del session id che attualmente viene insetito a manualmente
class RF(Thread):
	def __init__(self, byt, t_ipv4, t_ipv6, t_port):
		Thread.__init__(self)
		self.search = ""
		self.t_ipv4 = t_ipv4
		self.t_ipv6 = t_ipv6
		self.t_port = t_port

	def run(self):

		while((self.search == "") or (len(self.search)>20)):
			self.search = input("input non corretto per iniziare una ricerca: ")

		self.sessionid = "1234567890123456"
		self.con = Conn(self.t_ipv4, self.t_ipv6, self.t_port)
		if(self.con.connection()):
			self.pkt_look = self.sessionid+self.search.ljust(20)
			self.con.s.send(self.pkt_look.encode())

			self.ack_look = self.con.s.recv(7)
			self.bytes_read = len(self.ack_look)

			while(self.bytes_read < 7):
				self.ack_look += self.con.s.recv(7 - self.bytes_read)
				self.bytes_read = len(self.ack_look)

			self.nanswer = int(self.ack_look[4:7].decode())
			n = 0
			self.pkt_look = ""
			self.list_answers = []
			while(n < self.nanswer):
				self.answer = self.con.s.recv(148)
				self.bytes_read = len(self.answer)
				while(self.bytes_read < 148):
					self.answer += self.con.s.recv(148 - self.bytes_read)
					self.bytes_read = len(self.answer)

				self.list_answers.extend((self.answer[32:132].decode().strip(),self.answer[:32].decode()))
				self.pkt_look += self.answer.decode()+"\n"
				n+=1
			self.list_answers.extend(("Abort",None))
			b = curses.wrapper(Util.menu, self.list_answers, ['Select a file:'])
			if(b != None):
				print("FCHU...")
			else:
				print("Non faccio nulla...")
			self.con.deconnection()
		else:
		  print("Errore durante la connessione...")

if __name__ == '__main__':
	th_RF = RF("3","127.0.0.1","::1",3000)
	th_RF.start()
