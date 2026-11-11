#confronto tra scenario base e gli scenari con una sola regola di lotto per tutti gli articoli

import pandas as pd
from mrp.motore import esegui_mrp
from mrp.tabelle import calcola_indicatori


#scenario --> regola da forzare --> None = ogni articolo usa la sua regola
SCENARI = {
    "Base (regole da archivio)": None,
    "Tutto L4L": "L4L",
    "Tutto POQ": "POQ",
}

#Esegue l'MRP per ogni scenario e mette a confronto gli indicatori
def confronta_scenari(modello: dict) -> pd.DataFrame:
    righe = []
    for nome_scenario, regola in SCENARI.items():
        risultato = esegui_mrp(modello, regola)
        indicatori = calcola_indicatori(risultato)
        riga = {"Scenario": nome_scenario}
        riga.update(indicatori)
        righe.append(riga)
    return pd.DataFrame(righe)

