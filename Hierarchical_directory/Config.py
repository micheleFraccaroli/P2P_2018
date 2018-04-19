import configparser as config
import Util
from ipaddress import ip_address
from tqdm import tqdm
import time
import random as ran

class Config:
    
    def __init__(self):
        whiteList = {'general':{'ttl':self.validateInt,'maxNear':self.validateInt,'timeResearch':self.validateInt,'timeIdPacket':self.validateInt},
                     'self':{'selfV4':self.validateIP,'selfV6':self.validateIP,'selfP':self.validateInt},
                     'roots':{'root1V4':self.validateIP,'root1V6':self.validateIP,'root1P':self.validateInt,'root2V4':self.validateIP,'root2V6':self.validateIP,'root2P':self.validateInt}
                    }
        '''
        whiteList = {'general':{'ttl':self.validateInt,'maxNear':self.validateInt,'timeResearch':self.validateInt,'timeIdPacket':self.validateInt},
                     'self':{'selfV4':self.validateIP,'selfV6':self.validateIP,'selfP':self.validateInt},
                     'roots':{'root1V4':self.validateIP,'root1V6':self.validateIP,'root1P':self.validateInt}
                    }
        '''
        print('\nLoading config file......\n')
        time.sleep(2)
        data = config.ConfigParser() # Parser del file di configurazione
        data.optionxform = str # Case sensitive
        
        try:
            data.read_file(open('config.ini'))
        except IOError:
            print('Missing config file........ Autogenerating empty configuration file.')
            self.create()
            exit() 
        except config.DuplicateOptionError:
            print('Duplicated parameter in same section. Aborted.')
            exit()
        except config.MissingSectionHeaderError:
            print('Parameter found without section. Aborted.')
            exit()

        Util.initializeFiles()

        # Barra di caricamento con la tempistica configurabile

        lenWhiteList = sum(len(par) for par in data.values())
        pbar = tqdm(total = lenWhiteList)
        sleepA = 0.1
        sleepB = 0.1

        # errors:
        # 0: OK
        # 1: Errors
        # 2: Warnings

        errors = 0

        for section in data.sections():

            time.sleep(ran.uniform(sleepA,sleepB))
            pbar.set_description('Processing section %s' % section)
            if section in whiteList:
                for par in data[section]:
                    
                    #pbar.set_description('Processing parameter %s in section %s' % (par, section))
                    if par in whiteList[section]:
                        if not hasattr(self,par): # Parametro non settato, lo creo
                            try:
                                setattr(self,par,whiteList[section][par](data[section][par]))
                            except ValueError:
                                Util.printError("Parameter \'"+par+"\'' of section \'"+section+"\' invalid.")
                                errors = 1
                        else: # Avverrebbe sovrascrizione, lo evito
                            Util.printError("Conflit detected on parameter \'"+par+"\'. Parameter is defined in multiple sections.")
                            errors = 1
                        del whiteList[section][par] # Per il controllo dei parametri mancanti
                        if len(whiteList[section]) == 0:
                            del whiteList[section]
                    else:
                        Util.printError("Parameter \'"+par+"\' unnecessary in section \'"+section+"\': ignored.")
                        errors = 2
                    time.sleep(ran.uniform(sleepA,sleepB))
                    pbar.update(1)
            else:
                Util.printError("Section \'"+section+"\' unnecessary: ignored.")
                errors = 2
                for par in list(data[section]):
                    
                    Util.printError("Parameter \'"+par+"\'' of section \'"+section+"\': ignored.")
                    time.sleep(ran.uniform(sleepA,sleepB))
                    pbar.update(1)

        pbar.set_description('Done')
        
        # Per parametri mancanti
        if len(whiteList) != 0:
            errors = 1
            for section in whiteList:
                for par in whiteList[section]:
                    Util.printError("Missing parameter \'"+par+"\' in section \'"+section+"\'.")
        
        if errors == 1:
            print("\n\nConfiguration loading failed. Errors detected. Please check the file \'errors.log\' for more details.")
            exit()
        elif errors == 2:
            print("\n\nConfiguration loading complete. Unnecessary parameters detected. Please check the file \'errors.log\' for more details.\n")
        else:
            print("\n\nConfiguration loading complete.\n")
    
    def validateInt(self,num):
        
        return int(num)      

    def validateIP(self,ip):

        return str(ip_address(ip))

    def create(self):

        f = open('config.ini','w')
        f.write('[general]\n\nttl =\nmaxNear =\ntimeResearch =\ntimeIdPacket =\n\n')
        f.write('[self]\n\nselfV4 =\nselfV6 =\nselfP =\n\n')
        f.write('[roots]\n\nroot1V4 =\nroot1V6 =\nroot1P =\n\nroot2V4 =\nroot2V6 =\nroot2P =')
        f.close()

if __name__=='__main__':
    c=Config()


    print(c.__dict__)
   
    for el in c.__dict__:
        print(el,c.__dict__[el])
   # c.create()