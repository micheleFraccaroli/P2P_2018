import threading as th
import Util
from dataBase import dataBase

class rifleDict(th.Thread):
    def __init__(self):
        th.Thread.__init__(self)
        self.dict = Util.globalDict.copy()

    def run(self):
        db = dataBase()
        Util.globalDict = {}
        rifleList = []
        for k in self.dict.keys():
            sid = k[:16]
            md5 = k[16:]
            db.updatePart(md5, sid, self.dict[k])