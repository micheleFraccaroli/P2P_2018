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
    #ip_6 = '0000:0000:0000:0000:0000:0000:0000:0001'

    # formattazione ipv4
    split_ip_4 = ipv4.split(".")

    p2p = ''.join(ipp.zfill(3)+'.' for ipp in split_ip_4[:3])+split_ip_4[3].zfill(3)+'|'+ipv6

    # formattazione porta
    pp2p=str(port).zfill(5)
    return p2p+pp2p

def ip_deformatting(ip,port,ttl):
	
    ipv4, ipv6 = ip.split('|')
    
    f_ipv4 = re.sub('[.]0+','.',ipv4)
    
    ipv6 = re.sub('([:]0{4,4}){1,5}',':',ipv6)
    f_ipv6 = re.sub('([:]0{1,3})',':',ipv6)

    f_port = int(port)
    
    if(ttl != None):
        f_ttl = int(ttl)
    else:
        f_ttl = None

    return f_ipv4, f_ipv6, f_port, f_ttl

# DA CONFIGURARE COL DATABASE
'''
def ip_packet16_validation(packet16,packetWait):

    res = ip_packet16_is_known(packet16)
    if res:
        #print(int(time()) - ipPacket16[packet16])
        return ((int(time()) - ipPacket16[packet16]) > packetWait)
    else:
        return True

def ip_packet16_is_known(packet16):

    if packet16 in ipPacket16: # PacketId già presente in memoria
        return True
    else:
        ipPacket16[packet16]=int(time())
        return False
'''
def ip_packet16():

    # Per 16 volte scelgo un char casuale tra lower_case, upper_case o digit
    rand=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
    return rand

def initializeFiles():

    f = open('errors.log','w')
    f.write('#### Error file launched on {:%d-%m-%Y %H:%M:%S} ####'.format(datetime.now())+'\n\n')
    f.close()
    '''
    f = open('logs.log','w')
    f.write('#### File log avviato {:%d-%m-%Y %H:%M:%S} ####'.format(datetime.now())+'\n\n')
    f.close()
    '''
def printError(desc):

    f = open('errors.log','a')
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now())+desc+'\n')
    f.close()
'''
def printLog(log):

    f = open('logs.log','a')
    f.write('Timestamp: {:%d-%m-%Y %H:%M:%S} #### '.format(datetime.now())+log+'\n')
    f.close()
'''