import socket
import os
import Util
import threading as th
from Response import thread_Response

class Retr(th.Thread):
    def __init__(self, port, config):
        th.Thread.__init__(self) # thread istance first level
        self.port = port
        self.time = config.timeResearch

    def run(self):
        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.port))
        peersocket.settimeout(self.time)
        peersocket.listen(5)

        while True:
            try:
                other_peersocket, addr = peersocket.accept()
                thread = thread_Response(other_peersocket)
                thread.start()
            except OSError as e:
                exit(0)