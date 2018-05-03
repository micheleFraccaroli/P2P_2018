import socket
import os
import sys
import threading as th
import ipaddress as ipaddr
from Download import Download
import curses
import Util

class Recv_Afin(th.Thread):
    def __init__(self, numMD5, other_peersocket):
        th.Thread.__init__(self)
        self.nMd5 = numMD5
        self.other_peersocket = other_peersocket

    def stampaRicerca(self):

        print('Risultati ricerca:')
        for index in range(0, len(self.listPeers)):
            print('\n', index + 1, '- descrizione: ', self.listPeers[index][1])

        # Formato listPeers:
        #						0		 1			2						3
        #														0			1			2
        #                    [ md5 | nome_file | n_copie [ peer_IPv4 | peer_IPv6 | peer_porta ] ]

        flag = True
        while flag:
            flag = False
            print('\nIndicare quale si desidera scaricare (0 per annullare):')
            choice = int(input())
            if choice == 0:
                flag=False
            elif not choice in range(1, len(self.listPeers) + 1):
                print('La risorsa non esiste, ritenta')
                flag = True
            else:
                self.index_md5 = choice
                for copy in range(len(self.listPeers[choice - 1][3])):
                    print('\n', copy + 1, '- \n\tIPv4P2P: \t', self.listPeers[index][3][copy][0], '\n\tIPv6P2P: \t',
                          self.listPeers[index][3][copy][1], '\n\tPP2P: \t\t', self.listPeers[index][3][copy][2])

                #Formattazione IPv4 eliminando gli zeri non necessari
                self.split_ip = self.listPeers[index][3][copy][0].split(".")
                self.ipp2p = self.split_ip[0].lstrip('0') + '.' + self.split_ip[1].lstrip('0') + '.' + self.split_ip[2].lstrip('0') + '.' + self.split_ip[3].lstrip('0')

                self.ipp2p_6 = str(ipaddr.ip_address(self.listPeers[index][3][copy][1]))

                flag = True
                while flag:
                    flag = False

                    print('Indicare da quale peer scaricare il file selezionato (0 per annullare):')
                    choicePeer = int(input())
                    if choicePeer == 0:
                        print('Abortito')
                        flag=False
                        os.system('clear')
                    elif not choicePeer in range(1, len(self.listPeers[choice - 1][3]) + 1):
                        print('Il peer non esiste, ritenta')
                        flag = True
                    else:
                        print(self.ipp2p, self.ipp2p_6,
                                        self.listPeers[self.index_md5-1][3][choicePeer-1][2],
                                        self.listPeers[self.index_md5-1][0], self.listPeers[self.index_md5-1][1],
                                        )
                        down = Download(self.ipp2p, self.ipp2p_6,
                                        str(self.listPeers[self.index_md5-1][3][choicePeer-1][2]),
                                        str(self.listPeers[self.index_md5-1][0]), str(self.listPeers[self.index_md5-1][1]),
                                        )
                        down.download()

    def run(self):

        listPeers = []

        for i in range(0, self.nMd5*2, 2): # Ciclo gli indici pari contenenti l'opzione da visualizzare nel menu

            data = self.other_peersocket.recv(135)  # Ricevo md5, descrizione e numero di copie
            bytes_read = len(data)

            while (bytes_read < 135):

                data += self.other_peersocket.recv(135 - bytes_read)
                bytes_read = len(data)

            md5 = data[:32].decode()
            desc = data[32:132].decode().strip()
            nCopy = int(data[132:].decode())

            listPeers.append(desc) # Inserisco descrizione
            listPeers.append([])                    # Inserisco lista dei peers

            for j in range(nCopy):  # Per ogni copia dello specifico file

                data = self.other_peersocket.recv(60)  # Ricevo IP e porta del prossimo peer
                bytes_read = len(data)

                while (bytes_read < 60):

                    data += self.other_peersocket.recv(60 - bytes_read)
                    bytes_read = len(data)

                ipV4, ipV6 , port = Util.ip_deformatting(data[:55].decode(), data[55:].decode())

                listPeers[i+1].append(socket.getfqdn(ipV4) + ' (' + ipV4 + ')')
                listPeers[i+1].append((ipV4, ipV6, port, md5, desc))

        self.other_peersocket.close()

        b = curses.wrapper(Util.menu, listPeers, ['Select a file:','Select a peer:'], 6) # L'ultimo parametro basta sia diverso da None

        if b != None:

            down = Download(b[0], b[1], b[2], b[3], b[4])
            down.download()

        else:
            Util.waitMenu.acquire()
            Util.waitMenu.notify()
            Util.waitMenu.release()

if __name__ == '__main__':

    import Util

    peersocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    peersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    peersocket.bind(('', 3000))

    peersocket.listen(20)

    while True:

        Util.printLog("IN ATTESA DI UNA RICHIESTA ")
        other_peersocket, addr = peersocket.accept()
        Util.printLog(str(other_peersocket))

        if addr[0] == "::1": # Localhost
            addrPack = addr[0]
            Util.printLog("Richiesta in arrivo da: "+addrPack)

        elif addr[0][:2] == "::":
            addrPack = addr[0][7:]
            Util.printLog("Richiesta in arrivo da: "+addrPack)

        else:
            addrPack=addr[0]
            Util.printLog("Richiesta in arrivo da: "+addrPack)

        recv_type = other_peersocket.recv(4)
        if(len(recv_type) != 0):
            bytes_read = len(recv_type)
            while (bytes_read < 4):

                recv_type += other_peersocket.recv(4 - bytes_read)
                bytes_read = len(recv_type)

            if(recv_type.decode() == "AFIN"):
                recv_packet = other_peersocket.recv(3) # numero di md5 ottenuti
                bytes_read = len(recv_packet)
                while (bytes_read < 3):
                    recv_packet += other_peersocket.recv(3 - bytes_read)
                    bytes_read = len(recv_packet)

                Util.printLog("RICEVUTO AFIN")
                recv_afin = Recv_Afin(int(recv_packet.decode()), other_peersocket)
                recv_afin.start()
            else:
                Util.printLog('Pacchetto sconosciuto')
                other_peersocket.close()
