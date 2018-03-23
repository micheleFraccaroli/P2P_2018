import configparser as config
from Util import *

class Config:
    def __init__(self):
        
        data = config.ConfigParser() # Parser del file di configurazione
        data.read('config.ini')
        
        self.listNode = []
        self.listNode.insert(0,[data['roots']['root1V4'],data['roots']['root1V6'],data.getint('roots','root1P')])
        self.listNode.insert(1,[data['roots']['root2V4'],data['roots']['root2V6'],data.getint('roots','root2P')])
       
        self.selfV4 = data['self']['selfV4']
        self.selfV6 = data['self']['selfV6']
        self.selfP = data['self']['selfP']

        self.ttl = data.getint('general','ttl')
        self.maxNear = data.getint('general','maxNear')
        self.timeResearch = data.getint('general','timeResearch')
        self.timeIdPacket = data.getint('general','timeIdPacket')

    def pissi(self):
        print('lol')
        ip_deformatting()