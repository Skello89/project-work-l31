from mrp.livelli import calcola_livelli, ordina_per_livello
from mrp.record import calcola_record

#MRP completa, elabora tutti gli articoli per livello
def esegui_mrp(modello: dict, regola_forzata: str | None = None) -> dict:
    anagrafica = modello["anagrafica"]
    distinte = modello["distinte"]
    orizzonte = modello["orizzonte"]
    prodotto_finito = modello["prodotto_finito"]

    #elaborazione dal livello 0 al più profondo
    livelli = calcola_livelli(prodotto_finito, distinte)
    ordine = ordina_per_livello(livelli)

    #fabbisogni lordi vuoti per tutti tranne per prodotto finito
    fabbisogni: dict[str, dict[int, float]] = {}
    for codice in anagrafica:
        fabbisogni[codice] = {}

    settimana = 1
    for quantita in modello["fabbisogni_lordi"]:
        fabbisogni[prodotto_finito][settimana] = quantita
        settimana += 1

    #artioli elaborati uno alla volta in base ai livelli
    tutti_i_record: dict[str, dict] = {}
    tutti_gli_ordini: list[dict] = []
    
    for codice in ordine:
        articolo = anagrafica[codice]

        record = calcola_record(articolo, fabbisogni[codice], orizzonte, regola_forzata,)
        record["livello"] = livelli[codice]
        tutti_i_record[codice] = record
        tutti_gli_ordini.extend(record["ordini"])

        #emissione ordine ai componenti diretti
        for componente in distinte.get(codice, []):
            figlio = componente["figlio"]
            coefficiente = componente["quantita"]
            for settimana_emissione, quantita in record["emissioni"].items():
                if settimana_emissione >= 1:
                    gia_richiesto = fabbisogni[figlio].get(settimana_emissione, 0)
                    fabbisogni[figlio][settimana_emissione] = round(
                        gia_richiesto + quantita * coefficiente, 3
                    )
    return {"record": tutti_i_record, "ordini": tutti_gli_ordini}
