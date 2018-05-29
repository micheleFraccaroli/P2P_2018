import threading as th
import Util
import math
from dataBase import dataBase

class rifleDict(th.Thread):
    def __init__(self,globalDict,key,flag):
        th.Thread.__init__(self)
        self.globalDict = globalDict
        self.key = key
        self.flag = flag

    def run(self):
        db = dataBase()
        infoFile = db.retrieveInfoFile(self.key[16:])
        if(self.flag):
            Util.printLog("SONO DENTRO A RIFLE DICT --------------------------> " + str(Util.globalDict))
            #Util.globalDict.pop(self.key, None)
        else:
            Util.globalDict[self.key] = {}
            for i in range(math.ceil(infoFile[0]/8)):
                Util.globalDict[self.key][i] = 0

        rifleList = []
        for k in self.globalDict.keys():
            sid = k[:16]
            md5 = k[16:]
            db.updatePart(md5, sid, self.globalDict[k])