from threading import Semaphore, Lock
# Grafica

rows = [] # Lista di tags dei file in download
uniqueIdRow = 0

# Dimensioni rettangoli e linee
widthPart = 3
heightPart = 50
offset = 50
nameFileHeight = 20
heightLine = 15

heightRow = heightPart + offset + nameFileHeight + heightLine # Altezza di una barra di un file

# Testo
LeftPaddingText = 2

activeDownload = 3
dSem = Semaphore(activeDownload)
lockGraphics = Lock()