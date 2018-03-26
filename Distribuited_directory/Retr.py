import socket
import os
import threading as th
from Response import thread_Response
import Util

class Retr:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def spawn_thread(self):
        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.port))
        peersocket.settimeout(35)
        peersocket.listen(5)

        while True:
            try:
                other_peersocket, addr = peersocket.accept()
                thread = thread_Response(other_peersocket)
                thread.start()
            except OSError as e:
                print("Ricerca terminata per timeout")
                print(e)
                exit(0)