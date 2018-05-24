import threading as th
import Util

class rifleDict(th.Thread):
    def __init__(self):
        th.Thread.__init__(self)
        self.dict = Util.globalDict.copy()

    def run(self):
        Util.globalDict = {}
        db.updatePart(part, recv_packet[16:48].decode(), recv_packet[:16].decode(), up)