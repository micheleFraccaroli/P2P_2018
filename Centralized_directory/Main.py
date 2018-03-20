import os
import multiprocessing as mp
from pathlib import Path
from Dir_login import Peer
from Ricerca import Ricerca
from Add_Remove import AddRm
from Upload import Upload
from File_system import File_system

IpMap = {'LR': '172.16.8.1', 'MC': '172.16.8.2', 'MF': '172.16.8.3',
         'MG': '172.16.8.4'}  # Dizionario per gli ipv4 statici put your ip here

IpMap_6 = {'LR': 'fc00::8:1', 'MC': 'fc00:0000:0000:0000:0000:0000:0008:0005', 'MF': 'fc00:0000:0000:0000:0000:0000:0008:0003',
         'MG': 'fc00:0000:0000:0000:0000:0000:0008:0004'}   # Dizionario per gli ipv6 statici put your ip here

dict = {}

if (os.path.exists("File_System.txt")):
    file_read = File_system(None, None)
    dict = file_read.read()

def clear():
    # Clear Windows command prompt.
    if (os.name in ('ce', 'nt', 'dos')):
        os.system('cls')

    # Clear the Linux terminal.
    elif ('posix' in os.name):
        os.system('clear')


######### INPUT INIZIALE #########

flag = True
while flag:
    flag = False
    info = input("Benvenuto! Fornisci ('nick IPv4_direcotry Ipv6_directory porta') per effettuare il login: ")
    info = info.split(' ')
    if len(info) > 4:
        clear()
        print("Input errato, sono stati inseriti troppi parametri!")
        flag = True
    elif len(info) < 4:
        clear()
        print("Input errato, parametri mancanti!")
        flag = True
    else:
        if not IpMap.get(info[0]):
            clear()
            print('Nick non corretto!')
            flag = True

clear()

#           IPv4_d   IPv6_d     mio_ipv4        mio_ipv6        port_p
peer = Peer(info[1], info[2], IpMap[info[0]], IpMap_6[info[0]], info[3])
sid = peer.login()

######### MENU PRINCIPALE #########
clear()

# background process for upload in v4 and v6
#process for ipv4
uploading = Upload(dict, IpMap[info[0]], int(info[3]))
up_4 = mp.Process(target=uploading.upload)
up_4.start()

#process for ipv6
uploading_6 = Upload(dict, IpMap_6[info[0]], int(info[3]))
up_6 = mp.Process(target=uploading_6.upload)
up_6.start()


print("Indicare l'operazione da eseguire: ")

flag = True
while flag:
    print("1-\tRicerca\n2-\tAggiunta\n3-\tRimozione\n4-\tLogout")
    op = input()

    if op == '1':
        ricerca = Ricerca(sid.decode(), info[1], info[2])
        ricerca.cerca()
        ricerca.stampaRicerca()

    elif op == '2':
        file_dict = open("File_System.txt", "a")

        add_rm = AddRm(info[1], info[2], 3000, dict, sid)
        file_add = input("Digita il nome del file che vuoi aggiungere: ")
        dict = add_rm.aggiunta(file_add)

    elif op == '3':
        add_rm = AddRm(info[1], info[2], 3000, dict, sid)
        dict = add_rm.rimuovi()

    elif op == '4':
        peer = Peer(info[1], info[2], IpMap[info[0]], IpMap_6[info[0]], info[3])
        peer.logout(sid)

        up_4.terminate()
        up_6.terminate()
        
        flag = False

    else:
        print('Input errato!')
        flag = True

    #exit()