import sqlite3 as sq3

con = sq3.connect("P2P.db")
c = con.cursor()


print("   ___  ___    ___                   ")      
print("  / _ \/ _ )  / _ \__ ____ _  ___    ")
print(" / // / _  | / // / // /  ' \/ _ \   ")
print("/____/____/ /____/\_,_/_/_/_/ .__/   ")
print("                           /_/       \n")

                                                    

print("--- VICINI ---\n")
for row in c.execute("SELECT * FROM neighborhood"):
    print(row)

print("\n--- RICHIESTE ---\n")
for row in c.execute("SELECT * FROM requests"):
    print(row)

print("\n--- RISPOSTE ---\n")
for row in c.execute("SELECT * FROM responses"):
    print(row)

print("\n--- ERRORI ---\n")
for row in c.execute("SELECT * FROM errors"):
    print(row)

con.close()