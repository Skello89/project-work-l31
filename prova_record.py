from pathlib import Path
from mrp.loader import carica_dati
from mrp.record import calcola_record
from mrp.stampa import stampa_record


percorso = Path(__file__).parent / "data" / "prodotto.json"
modello = carica_dati(percorso)
anagrafica = modello["anagrafica"]
orizzonte = modello["orizzonte"]

#prodotto finito con fabbisogni lordi dei parametri personali
#trasformo la lista in un dizionario
fabbisogni_pf: dict[int, float] = {}
settimana = 1
for quantita in modello["fabbisogni_lordi"]:
    fabbisogni_pf[settimana] = quantita
    settimana += 1

pf = anagrafica[modello["prodotto_finito"]]
record_pf = calcola_record(pf, fabbisogni_pf, orizzonte)
stampa_record(record_pf, orizzonte)

#test disco lavaruote
#fabbisogni lordi inventati per simulare ordine da sollecitare
disco = anagrafica["CD73000"]
record_disco = calcola_record(disco, {2:100, 5:100}, orizzonte)
stampa_record(record_disco, orizzonte)


#stesso prodotto finito ma forzando la regola POQ
record_poq = calcola_record(pf, fabbisogni_pf, orizzonte, regola="POQ")
stampa_record(record_poq, orizzonte)




