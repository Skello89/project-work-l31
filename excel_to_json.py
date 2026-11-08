#conversione del file Excel distinta base (fogli "BOM" e "Articoli") nel Json che verrà letto dal motore MRP.

#struttura del JSON:
#progetto, orizzonte_settimane, prodotto_finito, fabbisogni_lordi_prodotto_finito
#articoli: anagrafica (archivio articoli), un elemento per codice
#distinte: una voce per ogni articolo padre con i suoi componenti diretti

#vengono fatti controlli di coerenza e vincoli della traccia prima della scrittura file
#il file non viene generato se vengono trovati errori
#gli avvisi sono solo segnalati



import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
import pandas as pd



# Parametri del progetto (valori vincolati calcolati dai parametri personali)
# a=0, b=0, c=8, d=4, N=6, C=9
ORIZZONTE = 8
FABBISOGNI_LORDI = [55, 25, 60, 30, 65, 35, 70, 40]   # FL(t) = 50 + 5a + 5*(((t(d+3)+b) mod 13) - 6)
LOTTO_PF = 100                                       # 100 + 10b
GIACENZA_PF = 140                                    # 100 + 5c
SCORTA_SICUREZZA = 30                                # 5N  (prodotto finito e acquistati)
PERIODO_POQ = 3                                      # C dispari -> 3
MIN_ACQUISTATI = 3                                   # 3 + (a mod 3)

COLONNE_BOM = {
    "Livello": "livello",
    "Codice Padre": "padre",
    "Codice": "codice",
    "Descrizione": "descrizione",
    "Unità Misura": "um",
    "Quantità": "quantita",
}
COLONNE_ARTICOLI = {
    "Codice": "codice",
    "Descrizione": "descrizione",
    "Unità Misura": "um",
    "Provenienza": "provenienza",
    "Lead Time": "lead_time",
    "Regola": "regola",
    "Lotto": "lotto",
    "Periodo P": "periodo_P",
    "Giacenza iniziale": "giacenza_iniziale",
    "Scorta di sicurezza": "scorta_sicurezza",
    "Arrivo progr. Settimana": "arrivo_settimana",
    "Arrivo progr. Quantità": "arrivo_quantita",
}


def numero(x):
    if pd.isna(x):
        return None
    x = float(x)
    return int(x) if x.is_integer() else x


def testo(x):
    return None if pd.isna(x) else str(x).strip()


def leggi_excel(percorso: Path):
    bom = pd.read_excel(percorso, sheet_name="BOM")
    art = pd.read_excel(percorso, sheet_name="Articoli")

    for df, mappa, foglio in ((bom, COLONNE_BOM, "BOM"), (art, COLONNE_ARTICOLI, "Articoli")):
        mancanti = [c for c in mappa if c not in df.columns]
        if mancanti:
            sys.exit(f"ERRORE: nel foglio '{foglio}' mancano le colonne {mancanti}")
    bom = bom.rename(columns=COLONNE_BOM)[list(COLONNE_BOM.values())]
    art = art.rename(columns=COLONNE_ARTICOLI)[list(COLONNE_ARTICOLI.values())]

    #elimina righe completamente vuote
    bom = bom.dropna(how="all")
    art = art.dropna(how="all")
    return bom, art


def costruisci_articoli(art: pd.DataFrame):
    articoli = []
    for r in art.itertuples(index=False):
        arrivi = []
        if not pd.isna(r.arrivo_settimana) or not pd.isna(r.arrivo_quantita):
            arrivi.append({"settimana": numero(r.arrivo_settimana),
                           "quantita": numero(r.arrivo_quantita)})
        articoli.append({
            "codice": testo(r.codice),
            "descrizione": testo(r.descrizione),
            "um": testo(r.um),
            "provenienza": (testo(r.provenienza) or "").lower(),
            "lead_time": numero(r.lead_time),
            "regola": (testo(r.regola) or "").upper(),
            "lotto": numero(r.lotto),
            "periodo_P": numero(r.periodo_P),
            "giacenza_iniziale": numero(r.giacenza_iniziale),
            "scorta_sicurezza": numero(r.scorta_sicurezza),
            "arrivi_programmati": arrivi,
        })
    return articoli


#raggruppamento righe per padre
def costruisci_distinte(bom: pd.DataFrame):
    distinte = defaultdict(list)
    for r in bom.itertuples(index=False):
        padre = testo(r.padre)
        if padre is None:          
            continue
        distinte[padre].append({"figlio": testo(r.codice), "quantita": numero(r.quantita)})
    return [{"padre": p, "componenti": c} for p, c in distinte.items()]


def trova_radici(bom: pd.DataFrame):
    return [testo(c) for c in bom.loc[bom["padre"].isna(), "codice"]]


def controlla(articoli, distinte, bom, prodotto_finito):
    errori, avvisi = [], []
    anagrafica = {}
    for a in articoli:
        if a["codice"] in anagrafica:
            errori.append(f"Codice duplicato in Articoli: {a['codice']}")
        anagrafica[a["codice"]] = a

    
    figli_di = {d["padre"]: d["componenti"] for d in distinte}
    codici_bom = {testo(c) for c in bom["codice"]}
    for c in sorted(codici_bom - anagrafica.keys()):
        errori.append(f"{c} è nella BOM ma non in Articoli")
    for c in sorted(anagrafica.keys() - codici_bom):
        avvisi.append(f"{c} è in Articoli ma non compare nella BOM")
    for padre, comp in figli_di.items():
        if padre not in anagrafica:
            errori.append(f"Il padre {padre} non esiste in Articoli")
        visti = set()
        for c in comp:
            if c["figlio"] in visti:
                errori.append(f"{c['figlio']} compare più volte sotto {padre}: unisci le righe")
            visti.add(c["figlio"])
            if c["quantita"] is None or c["quantita"] <= 0:
                errori.append(f"Quantità non valida per {padre} -> {c['figlio']}")

    
    livello_max = {}

    def visita(codice, livello, percorso):
        if codice in percorso:
            errori.append("Ciclo nella distinta: " + " -> ".join(percorso + [codice]))
            return
        livello_max[codice] = max(livello_max.get(codice, 0), livello)
        for c in figli_di.get(codice, []):
            visita(c["figlio"], livello + 1, percorso + [codice])

    visita(prodotto_finito, 0, [])
    for c in sorted(anagrafica.keys() - livello_max.keys()):
        avvisi.append(f"{c} non è raggiungibile dal prodotto finito")

    
    for a in articoli:
        c = a["codice"]
        if a["provenienza"] not in ("produzione", "acquisto"):
            errori.append(f"{c}: provenienza '{a['provenienza']}' non valida (produzione/acquisto)")
        if a["regola"] not in ("FOQ", "POQ", "L4L"):
            errori.append(f"{c}: regola '{a['regola']}' non valida (FOQ/POQ/L4L)")
        if a["lead_time"] is None or not 1 <= a["lead_time"] <= 3:
            errori.append(f"{c}: lead time {a['lead_time']} fuori dall'intervallo 1-3")
        if a["regola"] == "FOQ" and not a["lotto"]:
            errori.append(f"{c}: regola FOQ senza lotto")
        if a["regola"] != "FOQ" and a["lotto"] is not None:
            avvisi.append(f"{c}: lotto indicato ma la regola è {a['regola']} (verrà ignorato)")
        if a["regola"] == "POQ" and a["periodo_P"] != PERIODO_POQ:
            errori.append(f"{c}: POQ con periodo P={a['periodo_P']}, deve essere {PERIODO_POQ}")
        if a["regola"] != "POQ" and a["periodo_P"] is not None:
            avvisi.append(f"{c}: periodo P indicato ma la regola è {a['regola']} (verrà ignorato)")
        if a["giacenza_iniziale"] is None or a["giacenza_iniziale"] < 0:
            errori.append(f"{c}: giacenza iniziale mancante o negativa")
        if a["scorta_sicurezza"] is None or a["scorta_sicurezza"] < 0:
            errori.append(f"{c}: scorta di sicurezza mancante o negativa")
        if a["provenienza"] == "acquisto" and a["scorta_sicurezza"] != SCORTA_SICUREZZA:
            errori.append(f"{c}: articolo acquistato con scorta {a['scorta_sicurezza']}, deve essere {SCORTA_SICUREZZA}")
        if (a["giacenza_iniziale"] or 0) < (a["scorta_sicurezza"] or 0):
            avvisi.append(f"{c}: giacenza iniziale inferiore alla scorta di sicurezza")
        for arr in a["arrivi_programmati"]:
            if arr["settimana"] is None or not 1 <= arr["settimana"] <= ORIZZONTE or not arr["quantita"]:
                errori.append(f"{c}: arrivo programmato incompleto o fuori orizzonte {arr}")
        if a["provenienza"] == "produzione" and c not in figli_di:
            pass

    #vincoli traccia
    pf = anagrafica.get(prodotto_finito)
    if pf:
        if pf["provenienza"] != "produzione":
            errori.append("Il prodotto finito deve essere di produzione")
        if pf["regola"] != "FOQ" or pf["lotto"] != LOTTO_PF:
            errori.append(f"Prodotto finito: richiesto FOQ con lotto {LOTTO_PF}")
        if pf["giacenza_iniziale"] != GIACENZA_PF:
            errori.append(f"Prodotto finito: giacenza iniziale richiesta {GIACENZA_PF}")
        if pf["scorta_sicurezza"] != SCORTA_SICUREZZA:
            errori.append(f"Prodotto finito: scorta di sicurezza richiesta {SCORTA_SICUREZZA}")

    n_livelli = max(livello_max.values(), default=0) + 1
    tutti_coeff = [c["quantita"] for comp in figli_di.values() for c in comp]
    n_padri = defaultdict(set)
    for p, comp in figli_di.items():
        for c in comp:
            n_padri[c["figlio"]].add(p)
    regole = {a["regola"] for a in articoli}
    vincoli = {
        "Distinta con almeno 3 livelli": (n_livelli >= 3, f"{n_livelli} livelli"),
        "Almeno 8 articoli": (len(articoli) >= 8, f"{len(articoli)} articoli"),
        "Coefficiente di impiego > 1": (any(q > 1 for q in tutti_coeff),
                                        f"{sum(q > 1 for q in tutti_coeff)} legami"),
        "Componente comune a due padri": (any(len(s) > 1 for s in n_padri.values()),
                                          f"{sum(len(s) > 1 for s in n_padri.values())} componenti"),
        "Articoli prodotti e acquistati": (
            {"produzione", "acquisto"} <= {a["provenienza"] for a in articoli}, ""),
        f"Almeno {MIN_ACQUISTATI} articoli acquistati": (
            sum(a["provenienza"] == "acquisto" for a in articoli) >= MIN_ACQUISTATI,
            f"{sum(a['provenienza'] == 'acquisto' for a in articoli)} acquistati"),
        "FOQ, POQ e L4L usate almeno una volta": ({"FOQ", "POQ", "L4L"} <= regole, ", ".join(sorted(regole))),
        "Almeno 2 articoli con arrivo programmato": (
            sum(bool(a["arrivi_programmati"]) for a in articoli) >= 2,
            f"{sum(bool(a['arrivi_programmati']) for a in articoli)} articoli"),
    }
    for nome, (ok, _) in vincoli.items():
        if not ok:
            errori.append(f"Vincolo della traccia non rispettato: {nome}")
    return errori, avvisi, vincoli


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Converte la BOM Excel in JSON per il motore MRP")
    parser.add_argument("--excel", type=Path, default=base / "data" / "Bom_Articoli.xlsx")
    parser.add_argument("--out", type=Path, default=base / "data" / "prodotto.json")
    args = parser.parse_args()

    bom, art = leggi_excel(args.excel)
    radici = trova_radici(bom)
    if len(radici) != 1:
        sys.exit(f"ERRORE: serve esattamente un prodotto finito (riga senza padre), trovati: {radici}")
    prodotto_finito = radici[0]

    articoli = costruisci_articoli(art)
    distinte = costruisci_distinte(bom)
    errori, avvisi, vincoli = controlla(articoli, distinte, bom, prodotto_finito)

    print(f"Prodotto finito: {prodotto_finito}")
    print(f"Articoli: {len(articoli)}  |  Distinte (padri): {len(distinte)}  |  "
          f"Legami: {sum(len(d['componenti']) for d in distinte)}\n")
    print("Vincoli della traccia:")
    for nome, (ok, dettaglio) in vincoli.items():
        print(f"  [{'OK' if ok else 'NO'}] {nome}" + (f"  ({dettaglio})" if dettaglio else ""))
    if avvisi:
        print(f"\nAvvisi ({len(avvisi)}):")
        for a in avvisi:
            print("  -", a)
    if errori:
        print(f"\nERRORI ({len(errori)}) - JSON non generato:")
        for e in errori:
            print("  -", e)
        sys.exit(1)

    dati = {
        "progetto": "PW27 - Distinta base e MRP",
        "orizzonte_settimane": ORIZZONTE,
        "prodotto_finito": prodotto_finito,
        "fabbisogni_lordi_prodotto_finito": FABBISOGNI_LORDI,
        "articoli": articoli,
        "distinte": distinte,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    print(f"\nJSON creato: {args.out}")


if __name__ == "__main__":
    main()
