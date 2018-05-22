import ipaddress as ipa
import re
import random
import string
from Conn import Conn
import time
from datetime import datetime
from threading import *
from dataBase import *
from curses import *
from pathlib import Path
from threading import Semaphore, Lock

# Variabili globali
mode = None # Modalità di utilizzo del programma: 'normal', 'super', 'update', 'logged'
sessionId = None # Id sesion da loggati
statusRequest = {} # Dizionario per lo stato delle richieste: true: valida false: invalida
listPeers = [] # Lista dei peers utilizzata durante l'aggiornamento delle tabelle dei peers
lock = Lock()
globalLock = Lock()
loggedOut = Condition()
waitMenu = Condition()
globalDict = {} # sid : list of md5
activeSearch = 0 # Numero di ricerche attualmente pronte
searchLock = Lock() # Lock per le ricerche
menuLock = Lock() # Lock per i menu
searchIncoming = Condition()

# Grafica

rows = [] # Lista di tags dei file in download
buttonsList = [] # Tutti i bottoni
uniqueIdRow = 0

# Dimensioni rettangoli e linee
widthPart = 3           # Larghezza dei rettangoli
heightPart = 50         # Altezza dei rettangoli
offsety = 50            # Offset y dei blocchi
offsetx = 200           # Offset x dei blocchi

labelOffsetx = 5        # Offset x delle statistiche
labelDistance = 20      # Distanza tra i label

nameFileHeight = 20     # Altezza del testo del nome del file
heightLine = 15         # Altezza della riga per delineare i numeri delle parti

heightRow = heightPart + offsety + nameFileHeight + heightLine # Altezza di una barra di un file
lockGraphics = Lock()

# Testo
LeftPaddingText = 2

# Download

activeDownload = 3
dSem = Semaphore(activeDownload)

def ip_formatting(ipv4,ipv6,port):

    # formattazione ipv6
    ip6 = ipa.ip_address(ipv6)
    ipv6 = ip6.exploded

    # formattazione ipv4
    split_ip_4 = ipv4.split(".")

    p2p = ''.join(ipp.zfill(3)+'.' for ipp in split_ip_4[:3])+split_ip_4[3].zfill(3)+'|'+ipv6

    # formattazione porta
    pp2p=str(port).zfill(5)
    return p2p+pp2p

def ip_deformatting(ip,port,ttl = None):

    ipv4, ipv6 = ip.split('|')

    f_ipv4 = re.sub('[.]0+','.',ipv4)

    f_ipv6 = str(ipa.ip_address(ipv6))

    f_port = int(port)

    if(ttl != None):
        f_ttl = int(ttl)
        return f_ipv4, f_ipv6, f_port, f_ttl
    else:
        f_ttl = None
        return f_ipv4, f_ipv6, f_port

def ip_packet16():

    # Per 16 volte scelgo un char casuale tra lower_case, upper_case o digit
    rand=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
    return rand

def initializeFiles():

    f = open('errors.log','w')
    f.write('#### Error file launched on {:%d-%m-%Y %H:%M:%S} ####'.format(datetime.now())+'\n\n')
    f.close()

    f = open('logs.log','w')
    f.write('#### Log file launched on {:%d-%m-%Y %H:%M:%S} ####'.format(datetime.now())+'\n\n')
    f.close()

    file = Path("File_System.txt")
    if(not file.is_file()):
        file = open('File_System.txt', "w")
        file.close()

def printLog(desc):

    f = open('logs.log','a')
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now()) + desc + '\n')
    f.close()

def printError(desc):

    f = open('errors.log','a')
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now()) + desc + '\n')
    f.close()

def menu(stdscr, listMenu, titleMenu, flag = None):

    attr = {}
    numset = []

    if flag != None:
        listMenu.append('Abort') # Appendo l'opzione di aborto del menu
        listMenu.append(None)

    for count in range(int(len(listMenu)/2)): # Tasti ascii per le opzioni numeriche
        numset.append(49 + count)

    # Colori per le opzioni

    init_pair(1, COLOR_WHITE, COLOR_BLACK)
    init_pair(2, COLOR_BLACK, COLOR_WHITE)
    init_pair(3, COLOR_RED, COLOR_BLACK)

    use_default_colors() # Prendi i colori del terminale

    attr['normal'] = color_pair(1)
    attr['highlighted'] = color_pair(2)
    attr['system'] = color_pair(3)

    stdscr.timeout(1000)

    #stdscr.bkgd(' ',color_pair(1)) # Colore background
    depthMenu = [] # Lista di tutti i menu incontrati
    depthMenu.append(listMenu)

    depth = 0 # Profondità del menu per selezionare il titolo
    c=0
    option = 0
    while c != 10: # enter --> esci

        stdscr.clear()
        stdscr.addstr('\n\t')
        stdscr.addstr(titleMenu[depth] + '\n', A_UNDERLINE)

        count = 1
        for i in range(0, len(listMenu), 2):

            if i == option:
                par = attr['highlighted']
            elif depth > 0:
                if flag != None:
                    if i in [len(listMenu) - 4, len(listMenu) - 2]:
                        par = attr['system']
                    else:
                        par = attr['normal']
                else:
                    if i == len(listMenu) - 2:
                        par = attr['system']
                    else:
                        par = attr['normal']
            else:
                if flag != None:
                    if i == len(listMenu) - 2:
                        par = attr['system']
                    else:
                        par = attr['normal']
                else:
                    par = attr['normal']

            stdscr.addstr('\n\t[{0}] '.format(count))

            if par != attr['normal']:
                stdscr.addstr(listMenu[i] + '\n', par)
            else: # Non specificando la coppia di colore, uso i colori standard
                stdscr.addstr(listMenu[i] + '\n')
            count += 1

        c = stdscr.getch()

        if c == KEY_UP:

            if option > 0:
                option -= 2
            else:
                option = len(listMenu) - 2

        elif c == KEY_DOWN:

            if option < len(listMenu) - 2:
                option += 2
            else:
                option = 0

        elif c != 10 and c in numset:
            option = (c - 49) * 2

        elif c == 10:

            if type(listMenu[option + 1]) != list: # L'elemento non è una lista quindi è quello che cerco

                return listMenu[option + 1]

            else:                                  # L'elemento è una lista, quindi prevedo un altro livello di menu

                lenMenu = len(listMenu[option + 1])
                if listMenu[option + 1] in depthMenu: # Il nuovo menu è già stato incontrato, perciò in realtà è un menu di livello superiore

                    depth -= 1
                    depthMenu.remove(listMenu)

                    swpList = listMenu[option + 1]

                    listMenu.remove(listMenu[option + 1])
                    listMenu.remove('Back')

                    if flag != None:
                        listMenu.remove('Abort')
                        listMenu.remove(None)

                    listMenu = swpList # Swap dei due menu

                else: # Menu inferiore
                    depth += 1

                    listMenu[option + 1].append('Back')
                    listMenu[option + 1].append(listMenu)

                    if flag != None:
                        listMenu[option + 1].append('Abort')
                        listMenu[option + 1].append(None)

                    listMenu = listMenu[option + 1]
                    depthMenu.append(listMenu)

                    numset = []
                    for count in range(int(len(listMenu)/2)): # Tasti ascii per le opzioni numeriche
                        numset.append(49 + count)

                c = 0 # Resetto input e l'opzione scelta
                option = 0

        else:

            if activeSearch > 0 and current_thread() != main_thread(): # Ho delle ricerche    
            
                return None

def analyzeFile(nameFile, lenPart):  # Analizzo il file per terminare il download dopo un crash

    
    f = open('Files/' + nameFile, 'rb')

    if lenPart > 1024:

        db = dataBase()

        lenChunk = int(db.retrieveConfig(('lenChunk',)))
        nChunk = ceil(lenPart/lenChunk)

    else:
        lenChunk = lenPart # Prevedo 1 chunk per parte
        nChunk = 1

    missingParts = [] # Indici delle parti mancanti
    statusPart = [] # lista coi valori di tutti i chunk di una parte

    indexPart = 0
    while True:
        for _ in range(nChunk - 1):
            
            r = f.read(lenChunk)

            if r == b'':

                f.close()
                return missingParts # Ho finito, ritorno le parti mancanti
        
            else:
                statusPart.append(int.from_bytes(r,'big')) # Accumulo il valore dei chunk

        # Leggo l'ultimo chunk (probabilmente non è completamente pieno)

        remainder = lenPart % lenChunk # Byte rimasti da leggere

        if remainder == 0: # Chunk completamente pieno
            remainder = lenChunk
        
        r = f.read(remainder)

        if r == b'':

            f.close()
            return missingParts # Ho finito, ritorno le parti mancanti
        
        statusPart.append(int.from_bytes(r,'big'))

        if sum(statusPart) == 0: # Tutti i chunk sono nulli: parte mancante

            missingParts.append(indexPart)
        
        statusPart = [] # Reset degli stati
        indexPart += 1

########################################################################################

if __name__ == '__main__':

    a='0000:0000:0000:0000:0000:0000:0000:0001'
    b='FC00:0000:0000:0000:0000:0000:0008:0001'

    resA = ip_deformatting('172.016.001.001|'+a,'50000','3')
    resB = ip_deformatting('172.016.001.001|'+b,'50000','3')

    for res in resA:
        print(res)

    print('\n\n')

    for res in resB:
        print(res)

    a = ip_formatting('172.16.8.1','fc00::8:1',50)
    b = ip_formatting('172.16.8.1','::1',50)

    print(a)
    print(b)
