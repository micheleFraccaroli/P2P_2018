import os
import multiprocessing as mp
from pathlib import Path
from Dir_login import Peer
from Ricerca import Ricerca
from Add_Remove import AddRm
from Upload import Upload
from File_system import File_system

IpMap = {'LR': '172.16.8.1', 'MC': '172.16.8.2', 'MF': '192.168.43.33',
         'MG': '172.16.8.4'}  # Dizionario per gli ip statici pu your ip here

dict = {}
check_filesystem = Path("File_System.txt")
if (check_filesystem.is_file()):
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
    print("Benvenuto! Fornisci (nick IPv4_direcotry||Ipv6_directory porta) per effettuare il login: ")
    info = input()
    info = info.split(' ')
    if len(info) > 3:
        clear()
        print("Input errato, sono stati inseriti troppi parametri!")
        flag = True
    elif len(info) < 3:
        clear()
        print("Input errato, parametri mancanti!")
        flag = True
    else:
        if not IpMap.get(info[0]):
            clear()
            print('Nick non corretto!')
            flag = True

clear()
peer = Peer(info[1], IpMap[info[0]], 'mettiquiiltuoipv6quandosaichesicuramentefunziona', info[2])
sid = peer.login()

######### MENU PRINCIPALE #########
clear()

# background process for upload
uploading = Upload(dict, IpMap['MF'], 50003)
up = mp.Process(target=uploading.upload())
up.start()

print("Indicare l'operazione da eseguire: ")

flag = True
while flag:
    print("1-\tRicerca\n2-\tAggiunta\n3-\tRimozione\n4-\tLogout")
    op = input()

    if op == '1':
        ricerca = Ricerca(sid, info[1])
        ricerca.cerca()
        ricerca.stampaRicerca()

    elif op == '2':
        file_dict = open("File_System.txt", "a")

        add_rm = AddRm(info[1], 3000, dict)
        file_add = input("Digita il nome del file che vuoi aggiungere: ")
        dict = add_rm.aggiunta(file_add)

        file_dict.write(dict)

    elif op == '3':
        add_rm = AddRm(info[1], 3000, dict)
        dict = add_rm.rimuovi()

    elif op == '4':
        peer = Peer(info[1], IpMap[info[0]], 'mettiquiiltuoipv6quandosaichesicuramentefunziona', info[2])
        peer.logout()

        flag = False

    else:
        print('Input errato!')
        flag = True

    exit()
