from pathlib import Path
from mrp.loader import carica_dati


# percorso Json costruito a partire dalla cartella file:
percorso = Path(__file__).parent / "data" / "prodotto.json"
modello = carica_dati(percorso)

anagrafica = modello["anagrafica"]
distinte = modello["distinte"]

print("Prodotto finito:", modello["prodotto_finito"])
print("Orizzonte:", modello["orizzonte"], "settimane")
print("Fabbisogni lordi:", modello["fabbisogni_lordi"])
print("Numero articoli:", len(anagrafica))
print("Numero distinte (padri):", len(distinte))

print("\nScheda del disco lavaruote:")
print(anagrafica["CD73000"])

print("\nComponenti diretti del prodotto finito (primi 5):")
for componente in distinte[modello["prodotto_finito"]][:5]:
    codice = componente["figlio"]
    descrizione = anagrafica[codice]["descrizione"]
print(" ", codice, "x", componente["quantita"], "-", descrizione)


#conteggio articoli acquistati
acquistati = 0
for articolo in anagrafica.values():
    if articolo["provenienza"] == "acquisto":
        acquistati += 1
print("\nArticoli acquistati:", acquistati)


