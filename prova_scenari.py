import pandas as pd
from pathlib import Path
from mrp.loader import carica_dati
from mrp.motore import esegui_mrp
from mrp.scenari import confronta_scenari
from mrp.tabelle import tabella_record

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

modello = carica_dati(Path(__file__).parent / "data" / "prodotto.json")

#tabella di confronto tra i 3 scenari
confronto = confronta_scenari(modello)
print("Confronto tra scenari:")
print(confronto)

#stesso articolo nei 3 scenari, il prodotto finito
for regola in [None, "L4L", "POQ"]:
    risultato = esegui_mrp(modello, regola)
    print(f"\nProdotto finito - regola forzata: {regola}")
    print(tabella_record(risultato["record"]["GRPPIEDEDX"]))


confronto.to_excel(Path(__file__).parent /"confronto_scenari.xlsx", index=False)
