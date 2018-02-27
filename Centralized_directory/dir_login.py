import socket

def dir_login(host, port):
   # create a socket object
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
   s.connect((host, port))                               

   # Receive no more than 16 bytes
   msg = s.recv(16)
   return (msg.decode('ascii'))