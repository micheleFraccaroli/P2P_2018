import socket
import os
import threading as th
from Response import thread_Response

class Retr:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def Spawn_thread(self):
        peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peersocket.bind(('', self.port))
        peersocket.settimeout(300)
        peersocket.listen(5)

        while True:
            try:
                other_peersocket, addr = peersocket.accept()
            except OSError as e:
                print("Ricerca terminata per timeout")
                print(e)
                exit(0)
                
            thread = thread_Response(other_peersocket)
            thread.start()
            thread.join()