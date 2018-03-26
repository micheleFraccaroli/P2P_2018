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
        self.selfP  = data.getint('self','selfP')
        
        self.root1V4 = data['roots']['root1V4']
        self.root1V6 = data['roots']['root1V6']
        self.root1P  = data.getint('roots','root1P')

        self.root2V4 = data['roots']['root2V4']
        self.root2V6 = data['roots']['root2V6']
        self.root2P  = data.getint('roots','root2P')

        self.ttl = data.getint('DEFAULT','ttl')
        self.maxNear = data.getint('DEFAULT','maxNear')
        self.timeResearch = data.getint('DEFAULT','timeResearch')
        self.timeIdPacket = data.getint('DEFAULT','timeIdPacket')