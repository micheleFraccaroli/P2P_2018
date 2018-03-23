import ipaddress as ip
import re

def ip_formatting(ipv4,ipv6,port):
    
    # formattazione ipv4
    split_ip_4 = ipv4.split(".")

    # formattazione ipv6
    ip_6 = ''
    for ip in ipv6.split(':'):
        if ip == '':
            ip_6 += (ip.zfill(4)+':')*5
        else:
            ip_6 += ip.zfill(4)+':'
    ip_6 = ip_6[:-1]
    ip_6 = '0000:0000:0000:0000:0000:0000:0000:0001'
    p2p = ''.join(ipp.zfill(3)+'.' for ipp in split_ip_4[:3])+split_ip_4[3].zfill(3)+'|'+ip_6

    # formattazione porta
    pp2p=str(port).zfill(5)
    return p2p+pp2p

def ip_deformatting(ipv4,ipv6,port):
	
    f_ipv4 = re.sub('[.]0+','.',ipv4)
    
    ipv6 = re.sub('([:]0{4,4}){1,5}',':',ipv6)
    f_ipv6 = re.sub('([:]0{1,3})',':',ipv6)

    f_port = int(port)

    return f_ipv4, f_ipv6, f_port

# Per Test
if __name__=='__main__':
    a,b,c=ip_deformatting('192.168.088.100','fc00:0000:0000:0000:0000:0000:0010:0009','05000')
    print(a,b,c)
    d=ip_formatting(a,b,c)
    print(d)

# Definizione variabili globali
def define_g():
    global diz
    diz={}