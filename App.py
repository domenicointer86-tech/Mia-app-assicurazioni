import datetime

class Piatto:
    def __init__(self, nome, prezzo):
        self.nome = nome
        self.prezzo = prezzo

class Tavolo:
    def __init__(self, numero):
        self.numero = numero
        self.ordinazioni = []
        self.occupato = False

    def aggiungi_ordine(self, piatto):
        self.ordinazioni.append(piatto)
        self.occupato = True

    def calcola_conto(self):
        totale = sum(p.prezzo for p in self.ordinazioni)
        return totale

    def libera_tavolo(self):
        self.ordinazioni = []
        self.occupato = False

# --- Configurazione Iniziale ---
menu = {
    "1": Piatto("Pasta al Forno", 10.0),
    "2": Piatto("Bistecca", 15.0),
    "3": Piatto("Acqua", 2.0),
    "4": Piatto("Caffè", 1.5)
}

tavoli = {n: Tavolo(n) for n in range(1, 6)} # Crea 5 tavoli

def mostra_interfaccia():
    while True:
        print(f"\n--- GESTIONALE RISTORANTE v1.0 | {datetime.date.today()} ---")
        print("1. Visualizza Tavoli")
        print("2. Prendi Ordine")
        print("3. Emetti Conto")
        print("4. Esci")
        
        scelta = input("\nSeleziona un'opzione: ")

        if scelta == "1":
            for n, t in tavoli.items():
                stato = "OCCUPATO" if t.occupato else "LIBERO"
                print(f"Tavolo {n}: {stato}")

        elif scelta == "2":
            n_tavolo = int(input("Numero tavolo: "))
            print("\n--- MENU ---")
            for k, v in menu.items():
                print(f"{k}. {v.nome} ({v.prezzo}€)")
            
            codice = input("Inserisci codice piatto (o '0' per finire): ")
            while codice != "0":
                if codice in menu:
                    tavoli[n_tavolo].aggiungi_ordine(menu[codice])
                    print(f"Aggiunto {menu[codice].nome}")
                codice = input("Altro piatto? ")

        elif scelta == "3":
            n_tavolo = int(input("Numero tavolo per conto: "))
            t = tavoli[n_tavolo]
            if t.ordinazioni:
                print(f"\n--- CONTO TAVOLO {n_tavolo} ---")
                for p in t.ordinazioni:
                    print(f"{p.nome}: {p.prezzo}€")
                print(f"TOTALE: {t.calcola_conto()}€")
                t.libera_tavolo()
            else:
                print("Il tavolo è già vuoto!")

        elif scelta == "4":
            break

if __name__ == "__main__":
    mostra_interfaccia()
