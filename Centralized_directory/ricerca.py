import socket
import hashlib
import sys
from Centralized_directory.Conn import Conn
from Centralized_directory.download import Download


class Ricerca:
    def __init__(self, sessionid, ipp2p_dir):
        self.ipp2p_dir = ipp2p_dir
        self.sID = sessionid
        self.pack = 'FIND' + '.' + sessionid + '.'
        self.con = Conn(self.ipp2p_dir, 3000)

    def cerca(self):

        print('Inserisci una sequenza di caratteri per iniziare la ricerca! ')

        flag = True
        while flag:
            flag = False
            fileFind = input() # Stringa di ricerca

            lenFile = len(fileFind)

            if lenFile == 0:
                print('Errore, non è stato inserito alcun nominativo file!')
                flag = True

            elif lenFile > 20:
                print(
                    'Il nome da ricercare è troppo lungo, verranno mantenuti solo i primi 20 caratteri per effettuare la ricerca!')
                fileFind = fileFind[:20]

            elif lenFile < 20:
                fileFind += " " * (20 - lenFile)

        self.pack = self.pack + fileFind
        print('Ecco il pacchetto pronto da inviare al server: ', self.pack, 'lunghezza totale file: ', len(fileFind))

        self.con.connection()
        self.s.send(self.pack.encode('ascii'))

        msg = self.s.recv(7)  # Ricevo identificativo pacchetto e numero di md5
        msg = msg.decode()

        if msg[:4] == 'AFIN':
            nFile = int(msg[4:])  # Numero di md5 ottenuti
            if nFile == 0:
                print('File richiesto non trovato')
                self.s.recv(1024)  # Butto via i dati in eccesso
                sys.exit(0)
        else:
            print('errore codice pacchetto')
            self.con.deconnection()
            sys.exit(0)

        self.listPeers = []
        for i in range(0, nFile):
            data = self.s.recv(135)  # Ricevo md5, descrizione e numero di copie
            data = data.decode()
            self.listPeers.insert(i, [data[:32], data[32:132], int(data[132:]), []])
            for j in range(0, self.listPeers[i][2]):  # Per ogni copia dello specifico file
                data = self.s.recv(60)  # Ricevo IP e porta del prossimo peer
                data = data.decode()
                IPv4, IPv6 = data[:55].split('|')
                self.listPeers[i][3].append([IPv4, IPv6, int(data[55:])])

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
                sys.exit(0)
            elif not choice in range(1, len(self.listPeers) + 1):
                print('La risorsa non esiste, ritenta')
                flag = True
            else:
                self.index_md5 = choice
                for copy in range(0, len(self.listPeers[choice - 1][3])):
                    print('\n', copy + 1, '- \n\tIPv4P2P: \t', self.listPeers[index][3][copy][0], '\n\tIPv6P2P: \t',
                          self.listPeers[index][3][copy][1], '\n\tPP2P: \t\t', self.listPeers[index][3][copy][2])

                flag = True
                while flag:
                    flag = False

                    print('Indicare da quale peer scaricare il file selezionato (0 per annullare):')
                    choicePeer = int(input())
                    if choicePeer == 0:
                        print('Abortito')
                        sys.exit(0)
                    elif not choicePeer in range(1, len(self.listPeers[choice - 1][3]) + 1):
                        print('Il peer non esiste, ritenta')
                        flag = True
                    else:
                        down = Download(self.sID, self.listPeers[self.index_md5][3][choicePeer][0],
                                        self.listPeers[self.index_md5][3][choicePeer][2],
                                        self.listPeers[self.index_md5][0], self.listPeers[self.index_md5][1],
                                        self.ipp2p_dir)
                        down.download()
                        print('Scaricato!')
