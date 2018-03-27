import sqlite3 as sq3

con = sq3.connect("P2P.db")
c = sq3.cursor()

for row in c.execute("SELECT * FROM neighbors"):
    print("--- VICINI ---\n")
    print(row)

for row in c.execute("SELECT * FROM requests"):
    print("\n--- RICHIESTE ---\n")
    print(row)

for row in c.execute("SELECT * FROM responses"):
    print("\n--- RISPOSTE ---")
    print(row)

con.close()