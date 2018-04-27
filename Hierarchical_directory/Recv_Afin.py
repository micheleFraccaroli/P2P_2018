import socket
import os
import sys
import threading as th
import ipaddress as ipaddr
from Download import Download

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
        self.listPeers = []
        for i in range(self.nMd5):
            data = self.other_peersocket.recv(135)  # Ricevo md5, descrizione e numero di copie
            self.bytes_read = len(data)

            while (self.bytes_read < 135):
                data += self.other_peersocket.recv(135 - self.bytes_read)
                self.bytes_read = len(data)

            self.listPeers.insert(i, [data[:32].decode(), data[32:132].decode().strip(), int(data[132:].decode()), []])
            for j in range(0, self.listPeers[i][2]):  # Per ogni copia dello specifico file
                data = self.other_peersocket.recv(60)  # Ricevo IP e porta del prossimo peer
                data = data.decode()
                IPv4, IPv6 = data[:55].split('|')
                self.listPeers[i][3].append([IPv4, IPv6, int(data[55:])])

        self.other_peersocket.close()
        self.stampaRicerca()