import ipaddress as ipa
import re
import random
import string
from Conn import Conn
import time
from datetime import datetime
from threading import *
from dataBase import *

# Variabili globali
mode = None # Modalità di utilizzo del programma: 'normal', 'super', 'update', 'logged'
statusRequest = {} # Dizionario per lo stato delle richieste: true: valida false: invalida
listPeers = [] # Lista dei peers utilizzata durante l'aggiornamento delle tabelle dei peers
lock = Lock()
globalLock = Lock()


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

def ip_deformatting(ip,port,ttl):
	
    ipv4, ipv6 = ip.split('|')
    
    f_ipv4 = re.sub('[.]0+','.',ipv4)
    
    f_ipv6 = str(ipa.ip_address(ipv6))

    f_port = int(port)
    
    if(ttl != None):
        f_ttl = int(ttl)
    else:
        f_ttl = None

    return f_ipv4, f_ipv6, f_port, f_ttl

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

def updatePeers():
    
    globalLock.acquire()
    mode = Util.mode
    Util.mode = 'update'
    globalLock.release()

    lock.acquire()
    db = dataBase()

    listNormal = db.retrievePeers() 
    listSuper = db.retrieveSuperPeers()

    db.deletePeers()
    db.deleteSuperPeers()
    
    config = db.retrieveConfig(('selfV4','selfV6','selfP','ttl'))
    idPacket = ip_packet16()
    ip = ip_formatting(config.selfV4, config.selfV6, config.selfP)

    db.insertRequest(idPacket, ip[:55],time.time())

    lock.release()

    pack = 'SUPE' + idPacket + ip + config.ttl.zfill(2)
    print('\n'+pack+'\n')

    listPeers = listSuper + list(set(listNormal) - set(listSuper))

    globalLock.acquire()
    statusRequest[idPacket] = True
    globalLock.release()

    count = 0
    for peer in listPeers:

        ipv4, ipv6, port, ttl = Util.ip_deformatting(peer[0],peer[1],None)
        con = Conn(ipv4, ipv6, port)
        
        if con.connection():

            count += 1
            con.s.send(pack.encode())
            printLog("Richiesta SUPE a vicino ::: " + str(ipv4))
            con.deconnection()
        
        else:
            printLog("Richiesta SUPE fallita per ::: " + str(ipv4))
    count = 1
    if count == 0:

        print("                              .-.                                                ")
        print("                             (  o)-.                                             ")
        print("                              ) )\|\)                                            ")
        print("                           _./ (,_                                               ")
        print("                          ( '**\"  )                                             ")
        print("                          \\\\\   ///                                            ")
        print("                           \\\\\|///                                             ")
        print("                     _______//|\\\\____________               .                  ")
        print("                   ,'______///|\\\\\________,'|            \  :  /               ")
        print("     _ _           |  ____________________|,'             ' _ '                  ")
        print("    ' Y ' _ _      | ||              |                -= ( (_) )=-               ")
        print("    _ _  ' Y '     | ||              |                    .   .                  ")
        print("   ' Y '_ _        | ||              |                   /  :  \                 ")
        print("       ( Y )       | ||              8                      '                    ")
        print("                   | ||              8                                           ")
        print("                   | ||        /\/\  8                                           ")
        print("                   | ||      .'   ``/|                                           ")
        print("                   | ||      | x   ``|                                           ")
        print("                   | ||      |  /. `/`                                           ")
        print("                   | ||      '_/|  /```                 .-.                      ")
        print("                   | ||        (_,' ````                |.|                      ")
        print("  |J               | ||         |       \             /)|`|(\                    ")
        print(" L|                | ||       ,'         \           (.(|'|)`)                   ")
        print("  |                | ||     ,','| .'      \           `\`'./'                    ")
        print("~~~~~~~~~~~~~~~~~~~| ||~~~~~||~~||.        \~~~~~~~~~~~~|.|~~~~~~~~~~~           ")
        print("                   | ||     ||  || \        \          ,|`|.                     ")
        print("  ~~               | ||     \"\"  \"\"  \        \          \"'\"   ~~           ")
        print("                   | ||              )   .   )                                   ")
        print("                   | ||             / ,   ),'|      ~~                           ")
        print("             ~~    | ||         ___/ /   ,'  |              (_)                  ")
        print("      ((__))       | ||   ~~   I____/  ,'    |              /\"/                 ")
        print("      ( 0 0)       | ||         I____,'      *             ^~^                   ")
        print("       `\_\\\\       | ||                          ~~                            ")
        print("         \"'\"'      | ||                                                        ")
        print("  ~~               | ||         ~~                          ~~                   ")
        print("                   |_|/                                                          ")
        print("                                                                                 ")

        print('\nSorry, you\'re on your own\n')
        exit()

    print('attendo')
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
    print('fatto')

    return listPeers

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