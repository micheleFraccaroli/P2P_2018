import sqlite3 as sq3

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


con = sq3.connect("P2P.db")
c = con.cursor()

print(bcolors.MAGENTA + "   ___  ___    ___                   " + bcolors.ENDC)      
print(bcolors.MAGENTA + "  / _ \/ _ )  / _ \__ ____ _  ___    " + bcolors.ENDC)
print(bcolors.OKBLUE + " / // / _  | / // / // /  ' \/ _ \   " + bcolors.ENDC)
print(bcolors.CYAN + "/____/____/ /____/\_,_/_/_/_/ .__/   " + bcolors.ENDC)
print(bcolors.CYAN + "                           /_/       \n" + bcolors.ENDC)


print(bcolors.HEADER + "\nLOGIN |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM login"):
    print(row)

print(bcolors.HEADER + "VICINI |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM peers"):
    print(row)

print(bcolors.HEADER + "\nRICHIESTE |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM requests"):
    print(row)

print(bcolors.HEADER + "\nRISPOSTE |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM responses"):
    print(row)

print(bcolors.HEADER + "\nFILE |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM file"):
    print(row)

print(bcolors.HEADER + "\nCONFIG |------------------------------------------------\n" + bcolors.ENDC)
for row in c.execute("SELECT * FROM config"):
    print(row)

con.close()