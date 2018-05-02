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
from dataBase import dataBase
from dataBase import dataBase
import toPlotNetwork

# Variabili globali
mode = None # Modalità di utilizzo del programma: 'normal', 'super', 'update', 'logged'
sessionId = None # Id sesion da loggati
statusRequest = {} # Dizionario per lo stato delle richieste: true: valida false: invalida
listPeers = [] # Lista dei peers utilizzata durante l'aggiornamento delle tabelle dei peers
lock = Lock()
globalLock = Lock()
loggedOut = Condition()
waitMenu = Condition()

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

    stdscr.bkgd(' ',color_pair(1))
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
            stdscr.addstr(listMenu[i] + '\n', par)
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

#plotting network graph
def statusNetwork():
    db = dataBase()
    dbs = dataBaseSuper()

    nodes = [] #peer della rete
    sp_list = [] #superpeers della rete
    list_sp = db.retrieveSuperPeers()
    for lsp in list_sp:
        lsp_d = ip_deformatting(lsp[0], lsp[1]) 
        nodes.append(lsp_d[0])
        sp_list.append(lsp_d[0])
    my_ip = db.retrieveConfig(('selfV4', 'selfV6'))
    ip_SP = my_ip.selfV4 + "|" + my_ip.selfV6

    logged_list = [] # peer logged to supernode
    logged = dbs.retrieveLOGINsp()
    for lg in logged:
        lg_d = ip_deformatting(lg[0],lg[1])
        nodes.append(lg_d[0])
        logged_list.append(lg_d[0])

    nodes.insert(0,ip_SP[:15])

    edges = [] # archi della rete
    sol = [] # archi soluzione (traffico)
    for e1 in sp_list:
        edge = (ip_SP[:15],e1)
        edges.append(edge)
    for e2 in logged_list:
        edge = (e2, ip_SP[:15])
        sol.append(edge)

    num_sp = len(list_sp)
    num_peer = len(sol)
    toPlotNetwork.toPlot(nodes, edges, sol, num_sp, num_peer)


def updatePeers():
    
    globalLock.acquire()
    mode = Util.mode
    Util.mode = 'update'
    globalLock.release()

    lock.acquire()
    db = dataBase()

    listNormal = db.retrievePeers() 
    listSuper = db.retrieveSuperPeers()

    #db.deletePeers()
    db.deleteSuperPeers()
    
    config = db.retrieveConfig(('selfV4','selfV6','selfP','ttl'))
    idPacket = ip_packet16()
    ip = ip_formatting(config.selfV4, config.selfV6, config.selfP)

    db.insertRequest(idPacket, ip[:55],time.time())

    lock.release()

    pack = 'SUPE' + idPacket + ip + config.ttl.zfill(2)

    listPeers = listSuper + list(set(listNormal) - set(listSuper))

    globalLock.acquire()
    statusRequest[idPacket] = True
    globalLock.release()

    count = 0

    for peer in listPeers:

        ipv4, ipv6, port = Util.ip_deformatting(peer[0],peer[1])
        con = Conn(ipv4, ipv6, port)
        
        if con.connection():

            count += 1
            con.s.send(pack.encode())
            printLog("Richiesta SUPE a vicino ::: " + ipv4)
            con.deconnection()
        
        else:
            printLog("Richiesta SUPE fallita per ::: " + ipv4)

    if count == 0:

        print("                              .-.                                         ")
        print("                             (  o)-.                                      ")
        print("                              ) )\|\)                                     ")
        print("                           _./ (,_                                        ")
        print("                          ( '**\"  )                                      ")
        print("                          \\\\\   ///                                     ")
        print("                           \\\\\|///                                      ")
        print("                     _______//|\\\\____________               .           ")
        print("                   ,'______///|\\\\\________,'|            \  :  /        ")
        print("     _ _           |  ____________________|,'             ' _ '           ")
        print("    ' Y ' _ _      | ||              |                -= ( (_) )=-        ")
        print("    _ _  ' Y '     | ||              |                    .   .           ")
        print("   ' Y '_ _        | ||              |                   /  :  \          ")
        print("       ( Y )       | ||              8                      '             ")
        print("                   | ||              8                                    ")
        print("                   | ||        /\/\  8                                    ")
        print("                   | ||      .'   ``/|                                    ")
        print("                   | ||      | x   ``|                                    ")
        print("                   | ||      |  /. `/`                                    ")
        print("                   | ||      '_/|  /```                 .-.               ")
        print("                   | ||        (_,' ````                |.|               ")
        print("  |J               | ||         |       \             /)|`|(\             ")
        print(" L|                | ||       ,'         \           (.(|'|)`)            ")
        print("  |                | ||     ,','| .'      \           `\`'./'             ")
        print("~~~~~~~~~~~~~~~~~~~| ||~~~~~||~~||.        \~~~~~~~~~~~~|.|~~~~~~~~~~~    ")
        print("                   | ||     ||  || \        \          ,|`|.              ")
        print("  ~~               | ||     \"\"  \"\"  \        \          \"'\"   ~~    ")
        print("                   | ||              )   .   )                            ")
        print("                   | ||             / ,   ),'|      ~~                    ")
        print("             ~~    | ||         ___/ /   ,'  |              (_)           ")
        print("      ((__))       | ||   ~~   I____/  ,'    |              /\"/          ")
        print("      ( 0 0)       | ||         I____,'      *             ^~^            ")
        print("       `\_\\\\       | ||                          ~~                     ")
        print("         \"'\"'      | ||                                                 ")
        print("  ~~               | ||         ~~                          ~~            ")
        print("                   |_|/                                                   ")
        print("                                                                          ")

        print('\nNobody found after update. Sorry, you\'re on your own\n')
        exit()

    cond = Condition()
    cond.acquire()
    cond.wait(20)
    cond.release()

    globalLock.acquire()
    statusRequest[idPacket] = False
    globalLock.release()

    globalLock.acquire()
    Util.mode = mode
    globalLock.release()

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