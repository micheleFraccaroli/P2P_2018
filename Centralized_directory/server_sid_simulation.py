import socket               # Import socket module
from Crypto import Random

iv = Random.new().read(16)

s = socket.socket()         # Create a socket object
host = '127.0.0.1'          # Get local machine name
port = 50000                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
while True:
   c, addr = s.accept()     # Establish connection with client.
   print('Got connection from', addr)
   c.send("Ciao")