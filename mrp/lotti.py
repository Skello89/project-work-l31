import math
PERIODO_POQ = 3

# L4L: ordino esattamente quello che manca
# FOQ: ordino una quantità fissa, lotti interi necessari per coprire il fabbisogno netto
# POQ: ordino in base al periodo fisso, con un solo ordine copro settimane

def lotto_l4l(fabbisogno_netto: float) -> float:
    return fabbisogno_netto

def lotto_foq(fabbisogno_netto: float, lotto: float) -> float:
    numero_lotti = math.ceil(fabbisogno_netto / lotto) #arrotondo per eccesso il risultato con la funzione ceil
    return numero_lotti * lotto

def lotto_poq(
    fabbisogni_lordi: dict[int, float], 
    arrivi: dict[int, float], 
    disponibile: float, 
    scorta: float, 
    settimana: int, 
    periodo: int, 
    orizzonte: int,
    ) -> float:
    ultima_settimana = min(settimana + periodo -1, orizzonte)

    totale_lordi = 0
    totale_arrivi = 0
    for s in range(settimana, ultima_settimana + 1):
        totale_lordi = totale_lordi + fabbisogni_lordi.get(s, 0)
        totale_arrivi = totale_arrivi + arrivi.get(s, 0)

    quantita = totale_lordi - totale_arrivi - disponibile + scorta
    return quantita

# scelgo la regola di lotto con restituzione quantità da ordinare
def calcola_quantita(
    regola: str,
    articolo: dict,
    fabbisogno_netto: float,
    fabbisogni_lordi: dict[int, float],
    disponibile_precedente: float,
    settimana: int,
    orizzonte: int,
) -> float:
    if regola == "L4L":
        quantita = lotto_l4l(fabbisogno_netto)
    elif regola == "FOQ":
        quantita = lotto_foq(fabbisogno_netto, articolo["lotto"])
    elif regola == "POQ":
        periodo = articolo["periodo_P"]
        if periodo is None:
            periodo = PERIODO_POQ
        quantita = lotto_poq(
            fabbisogni_lordi,
            articolo["arrivi_programmati"],
            disponibile_precedente,
            articolo["scorta_sicurezza"],
            settimana,
            periodo,
            orizzonte,
        )
    else:
        raise ValueError(f"Regola sconosciuta per {articolo['codice']}: {regola}") #controllo che il campo regola venga scritto correttamente

    return max(quantita, fabbisogno_netto)

