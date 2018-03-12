from dir_login import Peer
from ricerca import Ricerca
from time import sleep
import os
import multiprocessing as mp

IpMap={'LR':'172.16.8.1','MC':'172.16.8.2','MF':'172.16.8.3','MG':'172.16.8.4'} # Dizionario per gli ip statici

def clear():
	os.system('cls||clear')

######### INPUT INIZIALE #########
flag=True
while flag:
	flag=False
	print("Benvenuto! Fornisci (nick IPv4|Ipv6 porta) per collegarti ad una directory: ")
	info=input()
	info=info.split(' ')
	if len(info)>3:
		clear()
		print("Input errato, sono stati inseriti troppi parametri!")
		flag=True
	elif len(info)<3:
		clear()
		print("Input errato, parametri mancanti!")
		flag=True
	else:
		if  not IpMap.get(info[0]):
			clear()
			print('Nick non corretto!')
			flag=True

peer=Peer(info[1],IpMap[info[0]],'mettiquiiltuoipv6quandosaichesicuramentefunziona',info[2])
peer.login()

######### MENU PRINCIPALE #########
clear()

print("Indicare l'operazione da eseguire: ")

flag=True
while flag
	flag=False
	print("1-\tRicerca\n2-\tAggiunta\n3-\tRimozione\n4-\tLogout")
	op=input()
	
	if op=='1':
		ricerca=Ricerca()
		
		flag=False
	elif op=='2':
		# AGGIUNTA
		flag=False
	elif op=='3':
		# RIMOZIONE
		flag=False
	elif op=='4':
		peer.logout()
		flag=False
	else:
		print('Input errato!')
		flag=True
		
	exit()