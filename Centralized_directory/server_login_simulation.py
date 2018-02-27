import socket                                     

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

host = 'localhost'                           
port = 50000                                           

serversocket.bind((host, port))                                  

serversocket.listen(5)                                           

while True:
   clientsocket,addr = serversocket.accept()      

   print("Connesso a %s" % str(addr))
    
   msg = 'qwert12345yuiop5'+ "\r\n"
   clientsocket.send(msg.encode('ascii'))
   clientsocket.close()