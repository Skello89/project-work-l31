from pathlib import Path
from mrp.loader import carica_dati
from mrp.livelli import calcola_livelli, ordina_per_livello

percorso = Path(__file__).parent / "data" / "prodotto.json"
modello = carica_dati(percorso)
distinte = modello["distinte"]
livelli = calcola_livelli(modello["prodotto_finito"], distinte)

conteggio = {}
for codice in livelli:
    livello = livelli[codice]
    conteggio[livello] = conteggio.get(livello, 0) + 1
print("Articoli per livello (codice di livello più basso):")
for livello in sorted(conteggio):
    print("  livello", livello,  ":", conteggio[livello], "articoli")


codice_esempio = "CD18004"
print("\nIl", codice_esempio, "compare sotto questi padri:")
for padre in distinte:
    for componente in distinte[padre]:
        if componente["figlio"] == codice_esempio:
            print("  ", padre, "(livello", livelli[padre], ")")
print("Livello assegnato a", codice_esempio, ":", livelli[codice_esempio])

ordine = ordina_per_livello(livelli)
print("\nPrimi 5 da elaborare:", ordine[:5])
print("Ultimi 5 da elaborare:", ordine [-5:])
print("Totale articoli:", len(ordine))
