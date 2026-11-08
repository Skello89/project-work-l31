from pathlib import Path
from mrp.loader import carica_dati
from mrp.motore import esegui_mrp
from mrp.stampa import stampa_record

percorso = Path(__file__).parent / "data" / "prodotto.json"
modello = carica_dati(percorso)
orizzonte = modello["orizzonte"]

risultato = esegui_mrp(modello)
tutti_i_record = risultato["record"]
ordini = risultato["ordini"]

da_sollecitare = 0
for ordine in ordini:
    if ordine["da_sollecitare"]:
        da_sollecitare += 1
print("Articoli elaborati:", len(tutti_i_record))
print("Ordini pianificati", len(ordini))
print("Ordini da sollecitare", da_sollecitare)

#controllo di un componente comune: CD99000 (chiavetta)
print("\nEmissioni del padre GRPPIEDEDX:   ", tutti_i_record["GRPPIEDEDX"]["emissione_ordini"])
print("\nEmissioni del padre GRPLAVRUOTEDX:", tutti_i_record["GRPLAVRUOTEDX"]["emissione_ordini"])
stampa_record(tutti_i_record["CD17000"], orizzonte)

#primi 5 ordini da sollecitare
print("\nPrimi 5 ordini da sollecitare:")
contatore = 0
for ordine in ordini:
    if ordine["da_sollecitare"] and contatore < 5:
        print(f"  {ordine['codice']}: {ordine['quantita']} pezzi, emissione settimana "
              f"{ordine['settimana_emissione']}, arrivo settimana {ordine['settimana_arrivo']}")
        contatore += 1