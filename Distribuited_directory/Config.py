import configparser as config
from Util import *
from ipaddress import ip_address

class Config:
    
    def __init__(self):
        
        dataSections = ['general','self','roots']

        data = config.ConfigParser() # Parser del file di configurazione
        try:
            data.read_file(open('config.ini'))
        except IOError as e:
            print(e.errno)
            exit()
        if len(data) == 0:
            exit()    

        initializeFiles()

        for dato in data.sections(): 
            if dato not in dataSections:
                printError('Sezione '+dato+' non utilizzata: ignorata')
                for par in list(data[dato]):
                    printError('Parametro '+par+' della sezione '+dato+': ignorato')

        errors = False

        try:
            self.selfV4 = ip_address(data['self']['selfV4'])
        except ValueError as e:
            printError('Parametro selfV4 non valido')
            errors = True
        try:
            self.selfV6 = ip_address(data['self']['selfV6'])
        except ValueError as e:
            printError('Parametro selfV6 non valido')
            errors = True
        try:
            self.selfP  = data.getint('self','selfP')
        except ValueError as e:
            printError('Parametro selfP non valido')
            errors = True
        try:
            self.root1V4 = ip_address(data['roots']['root1V4'])
        except ValueError as e:
            printError('Parametro root1V4 non valido')
            errors = True
        try:
            self.root1V6 = ip_address(data['roots']['root1V6'])
        except ValueError as e:
            printError('Parametro root1V6 non valido')
            errors = True
        try:
            self.root1P  = data.getint('roots','root1P')
        except ValueError as e:
            printError('Parametro root1P non valido')
            errors = True
        try:
            self.root2V4 = ip_address(data['roots']['root2V4'])
        except ValueError as e:
            printError('Parametro root2V4 non valido')
            errors = True
        try:
            self.root2V6 = ip_address(data['roots']['root2V6'])
        except ValueError as e:
            printError('Parametro root2V6 non valido')
            errors = True
        try:
            self.root2P  = data.getint('roots','root2P')
        except ValueError as e:
            printError('Parametro root2P non valido')
            errors = True
        try:
            self.ttl = data.getint('general','ttl')
        except ValueError as e:
            printError('Parametro ttl non valido')
            errors = True
        try:
            self.maxNear = data.getint('general','maxNear')
        except ValueError as e:
            printError('Parametro maxNear non valido')
            errors = True
        try:
            self.timeResearch = data.getint('general','timeResearch')
        except ValueError as e:
            printError('Parametro timeResearch non valido')
            errors = True
        try:
            self.timeIdPacket = data.getint('general','timeIdPacket')
        except ValueError as e:
            printError('Parametro timeIdPacket non valido')
            errors = True

        if errors == True:
            print('Caricamento configurazione fallito. Errori rilevati. Aborto programma forzato.')
            exit()

    def create(self):

        f = open('config.ini','w')
        f.write('[general]\n\nttl =\nmaxNear =\ntimeResearch =\ntimeIdPacket =\n\n')
        f.write('[self]\n\nselfV4 =\nselfV6 =\nselfP =\n\n')
        f.write('[roots]\n\nroot1V4 =\nroot1V6 =\nroot1P =\n\nroot2V4 =\nroot1V6 =\nroot2P =')
        f.close()

if __name__=='__main__':
    c=Config()
    c.create()