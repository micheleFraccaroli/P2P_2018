import configparser as config

class File:
    def __init__(self):
        
        data=config.ConfigParser() # Parser del file di configurazione
        data.read('config.ini')
        
        self.listNode=[]
        self.listNode.insert(0,[data['roots']['root1V4'],data['roots']['root1V6'],data.getint('roots','root1P')])
        self.listNode.insert(1,[data['roots']['root2V4'],data['roots']['root2V6'],data.getint('roots','root2P')])
       
        self.ttl=data.getint('general','ttl')
        self.maxNear=data.getint('general','maxNear')
        self.timeResearch=data.getint('general','timeResearch')
        self.timeIdPacket=data.getint('general','timeIdPacket')