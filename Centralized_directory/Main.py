from dir_login import Peer
from threading import Thread
from time import sleep
import os

def clear():
	os.system('cls||clear')

def funT(d,u,f):
		for i in range(0,4):
			print(d,u,f)
			sleep(1)

thread = Thread(target = funT, args = (10,11,'Fracca'))
thread.start()
thread.join()	

print('finito')

flag=True
while flag:
	flag=False
	print("Benvenuto! Fornisci (nick IPv4|Ipv6) per collegarti ad una directory: ")
	info=input()
	info=info.split(' ')
	if len(info)>2:
		print("Input errato, sono stati inseriti troppi parametri!")
		flag=True
	elif len(info)<2:
		print("Input errato, parametri mancanti!")
		flag=True
		
peer=Peer()
peer.login()
