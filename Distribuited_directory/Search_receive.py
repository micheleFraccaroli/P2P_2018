# object for response of research

class Search_res:
    def __init__(self, pktid, ip, port, md5, filename):
        self.pktid = pktid
        self.ip = ip
        self.port = port
        self.md5 = md5
        self.filename = filename