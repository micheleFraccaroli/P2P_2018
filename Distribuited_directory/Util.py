import ipaddress as ip
import re
import random
import string
from time import time

def ip_formatting(ipv4,ipv6,port):

    # formattazione ipv6
    ip_6 = ''
    for ip in ipv6.split(':'):
        if ip == '':
            ip_6 += (ip.zfill(4)+':')*5
        else:
            ip_6 += ip.zfill(4)+':'
    ip_6 = ip_6[:-1]
    #ip_6 = '0000:0000:0000:0000:0000:0000:0000:0001'

    # formattazione ipv4
    split_ip_4 = ipv4.split(".")

    p2p = ''.join(ipp.zfill(3)+'.' for ipp in split_ip_4[:3])+split_ip_4[3].zfill(3)+'|'+ip_6

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

def ip_packet16():

    # Per 16 volte scelgo un char casuale tra lower_case, upper_case o digit
    rand=''.join(random.choice(string.ascii_letters+string.digits) for _ in range(16))
    return rand

def decrease_ttl(ttl):

    return ttl-1

# Definizione variabili globali
def define_g():

    global diz,ipPacket16
    diz={}
    ipPacket16={}

# Per Test
if __name__=='__main__':
    #define_g()
    ip_packet16_validation(ip_packet16())
    print(ipPacket16)