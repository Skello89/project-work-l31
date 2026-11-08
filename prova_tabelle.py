import pandas as pd
from pathlib import Path
from mrp.loader import carica_dati
from mrp.motore import esegui_mrp
from mrp.tabelle import (
    tabella_record,
    tabella_ordini,
    tabella_articoli,
    calcola_indicatori,
    esporta_excel,
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

cartella = Path(__file__).parent
modello = carica_dati(cartella / "data" /"prodotto.json")
risultato = esegui_mrp(modello)

#record MRP prodotto finito come tabella
print("Record MRP del prodotto finito:")
print(tabella_record(risultato["record"]["GRPPIEDEDX"]))

#ordini -> prime 10 righe
ordini = tabella_ordini(risultato["ordini"])
print("\nPiano ordini (prime 10 righe di", len(ordini), "):")
print(ordini.head(10))

#riepilogo articolo -> i 5 con più ordini
articoli = tabella_articoli(risultato, modello["anagrafica"])
print("\nArticoli con più ordini:")
print(articoli.sort_values("N. Ordini", ascending=False).head(5))

#indicatori di sintesi
indicatori = calcola_indicatori(risultato)
print("\nIndicatori:")
for nome, valore in indicatori.items():
    print(" ", nome, ":", valore)

#export in Excel
percorso_excel = cartella / "risultati_mpr.xlsx"
esporta_excel(percorso_excel, ordini, articoli, indicatori)
print("\nFile Excel creato:", percorso_excel)

senza_ordini = articoli[articoli["N. Ordini"] == 0]
print("\nArticoli senza ordini:", len(senza_ordini))


