import configparser as config
from Util import *

class Config:
    def __init__(self):
        
        data = config.ConfigParser() # Parser del file di configurazione
        try:
            data.read_file(open('config.ini'))
        except IOError as e:
            print(e.errno)
            exit()
        if len(data) == 0:
            exit()    

        dataSections=list(data)

        self.selfV4 = data['self']['selfV4']
        self.selfV6 = data['self']['selfV6']
        self.selfP = data.getint('self','selfP')
        
        self.listNode = []
        self.listNode.insert(0,[data['roots']['root1V4'],data['roots']['root1V6'],data.getint('roots','root1P')])
        self.listNode.insert(1,[data['roots']['root2V4'],data['roots']['root2V6'],data.getint('roots','root2P')])
       

        self.ttl = data.getint('DEFAULT','ttl')
        self.maxNear = data.getint('DEFAULT','maxNear')
        self.timeResearch = data.getint('DEFAULT','timeResearch')
        self.timeIdPacket = data.getint('DEFAULT','timeIdPacket')