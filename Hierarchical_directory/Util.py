import ipaddress as ipa
import re
import random
import string
from time import time
from datetime import datetime
from threading import Lock

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
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now())+desc+'\n')
    f.close()

def printError(desc):

    f = open('errors.log','a')
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now())+desc+'\n')
    f.close()

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
