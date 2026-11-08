from pathlib import Path
import pandas as pd

#trasformazione del motore MRP in tabelle Pandas
#record MRP: una riga per voce e una colonna per settimana
def tabella_record(record: dict) -> pd.DataFrame:
    voci = {
        "Fabbisogno lordo": record["fabbisogni_lordi"],
        "Arrivi programmati": record["arrivi_programmati"],
        "Disponibile previsto": record["disponibile_previsto"],
        "Fabbisogno netto": record["fabbisogni_netti"],
        "Arrivi pianificati": record["arrivi_pianificati"],
        "Emissione ordini": record["emissione_ordini"],
    }
    tabella = pd.DataFrame(voci).transpose()

    tabella.columns = [f"Sett. {t}" for t in range(1, len(tabella.columns) +1)]
    return tabella

#ordini organizzati per settimana di emissione
def tabella_ordini(ordini: list[dict]) -> pd.DataFrame:
    tabella = pd.DataFrame(ordini)
    tabella = tabella.rename(columns={
        "codice": "Codice",
        "descrizione": "Descrizione",
        "quantita": "Quantità",
        "settimana_emissione": "Settimana Emissione",
        "settimana_arrivo": "Settimana Arrivo",
        "da_sollecitare": "Da sollecitare",
    })
    tabella = tabella.sort_values(["Settimana Emissione", "Codice"])
    tabella = tabella.reset_index(drop=True)
    return tabella

#riga per articolo con dati principali e risultati MRP
def tabella_articoli(risultato: dict, anagrafica: dict[str, dict]) -> pd.DataFrame:
    righe = []
    for codice, record in risultato["record"].items():
        articolo = anagrafica[codice]
        disponibilita = record["disponibile_previsto"]
        quantita_ordinata = 0
        for ordine in record["ordini"]:
            quantita_ordinata = quantita_ordinata + ordine["quantita"]
        righe.append({
            "Codice": codice,
            "Decrizione": articolo["descrizione"],
            "Livello": record["livello"],
            "Provenienza": articolo["provenienza"],
            "Regola": record["regola"],
            "Lead Time": articolo["lead_time"],
            "N. Ordini": len(record["ordini"]),
            "Quantità Ordinata": round(quantita_ordinata, 3),
            "Scorta Media": round(sum(disponibilita) / len(disponibilita), 1),
        })
    return pd.DataFrame(righe)


#indicatori di sintesi
def calcola_indicatori(risultato: dict) -> dict:
    ordini = risultato["ordini"]
    numero_ordini = len(ordini)
    da_sollecitare = 0
    quantita_totale = 0
    for ordine in ordini:
        quantita_totale = quantita_totale + ordine["quantita"]
        if ordine["da_sollecitare"]:
            da_sollecitare = da_sollecitare + 1

    #scorta media, media disponibilità prevista su tutti gli articoli e settimane
    somma_disponibilita = 0
    numero_valori = 0
    for record in risultato["record"].values():
        somma_disponibilita = somma_disponibilita + sum(record["disponibile_previsto"])
        numero_valori = numero_valori + len(record["disponibile_previsto"])
    scorta_media = somma_disponibilita / numero_valori

    return {
        "N. Ordini": numero_ordini,
        "Ordini da sollecitare": da_sollecitare,
        "Quantità totale ordinata": round(quantita_totale, 1),
        "Scorta Media": round(scorta_media, 1),
    }


#salvo piano ordini, riepilogo articoli e indicatori in un file Excel
def esporta_excel(
        percorso: str | Path,
        ordini: pd.DataFrame,
        articoli: pd.DataFrame,
        indicatori: dict,
) -> None:
    tabella_indicatori = pd.DataFrame(list(indicatori.items()), columns=["Indicatore", "Valore"])
    with pd.ExcelWriter(percorso) as file_excel:
        ordini.to_excel(file_excel, sheet_name="Piano Ordini", index=False)
        articoli.to_excel(file_excel, sheet_name="Articoli", index=False)
        tabella_indicatori.to_excel(file_excel, sheet_name="Indicatori", index=False)








