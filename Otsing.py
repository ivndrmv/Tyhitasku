import sqlite3
from pathlib import Path

def otsi_tooteid(otsing):

    otsing = otsing.strip()

    if otsing = "":
        return []
    
    andmebaas = Path(__file__).resolve().parent / "tooted.db"


    if not andmebaas.is_file():
        print("Andmebaasi ei leitud!")
        return []
    
    conn = sqlite3.connect(andmebaas)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ("%" + otsing + "%",)
    )

    tulemused = cursor.fetchall()

    conn.close()

    tooted = []

    for toode in tulemused:
        tooted.append(dict(toode))
    
    return tooted 

#if __name__ == "__main__":
#    otsing = input("Sisesta toote nimi: ")
#
#    tulemused = otsi_tooteid(otsing)
#
#    for toode in tulemused:
#        print(toode["name"], toode["discount_price"], "€")
#
#    print("Leitud tooteid:", len(tulemused))
