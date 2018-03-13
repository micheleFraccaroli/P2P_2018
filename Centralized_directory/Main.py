import os
import multiprocessing as mp
from pathlib import Path
from Centralized_directory.dir_login import Peer
from Centralized_directory.ricerca import Ricerca
from Centralized_directory.Add_Remove import AddRm
from Centralized_directory.upload import Upload
from Centralized_directory.file_system import file_system

IpMap = {'LR': '172.16.8.1', 'MC': '172.16.8.2', 'MF': '172.16.8.3',
         'MG': '172.16.8.4'}  # Dizionario per gli ip statici

dict = {}
check_filesystem = Path("File_System.txt")
if (check_filesystem.is_file()):
    file_read = file_system(None, None)
    dict = file_read.read()

def clear():
    os.system('cls||clear')


######### INPUT INIZIALE #########

flag = True
while flag:
    flag = False
    print("Benvenuto! Fornisci (nick IPv4|Ipv6 porta) per fare il login: ")
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