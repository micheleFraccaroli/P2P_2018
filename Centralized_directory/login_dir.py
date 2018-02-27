import socket

s = socket.socket()

def dir_connection(ip_addr, port):
    s.connect((ip_addr, port))
    return s.recv(1024)
    s.close()

if __name__ == '__main__':
    sid = dir_connection('127.0.0.1', 50000)
    print(sid)