import json
from pathlib import Path


# leggo il file json
def carica_json(percorso: str | Path) -> dict:
    with open(percorso, "r", encoding="utf-8") as file:
        dati = json.load(file)
    return dati


# trasformazione lista articoli del json in dizionario
def crea_anagrafica(dati: dict) -> dict[str, dict]:
    anagrafica: dict[str, dict] = {}
    for art in dati["articoli"]:
        articolo = dict(art)

    # in Json gli arrivi sono liste
    # trasformazione arrivi in dizionario
        arrivi: dict[int, float]= {}
        for arrivo in art["arrivi_programmati"]:
            settimana = arrivo["settimana"]
            arrivi[settimana] = arrivi.get(settimana, 0) + arrivo["quantita"]
        articolo["arrivi_programmati"] = arrivi

        anagrafica[articolo["codice"]] = articolo
    return anagrafica


# trasformazione lista distinte Json in un dizionario
def crea_distinte(dati: dict) -> dict[str, list[dict]]:
    distinte: dict[str, list[dict]] = {}
    for distinta in dati["distinte"]:
        padre = distinta["padre"]
        distinte[padre] = distinta["componenti"]
    return distinte


# Funzione main: legge il Json e restituisce tutto ciò che serve
def carica_dati(percorso: str | Path) -> dict:
    dati = carica_json(percorso)
    return {
        "orizzonte": dati["orizzonte_settimane"],
        "prodotto_finito": dati["prodotto_finito"],
        "fabbisogni_lordi": dati["fabbisogni_lordi_prodotto_finito"],
        "anagrafica": crea_anagrafica(dati),
        "distinte": crea_distinte(dati),
    }