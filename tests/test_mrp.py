#test_mrp
#test automatici del motore MRP, confrontano i risultati del programma con valori calcolati a mano
#vengono lanciati con il comando: pytest


from pathlib import Path
from mrp.loader import carica_dati
from mrp.livelli import calcola_livelli
from mrp.lotti import lotto_l4l, lotto_foq, lotto_poq
from mrp.record import calcola_record
from mrp.motore import esegui_mrp

PERCORSO_JSON = Path(__file__).parent.parent / "data" / "prodotto.json"

#carica dati progetto
def carica_modello() -> dict:
    return carica_dati(PERCORSO_JSON)


#regole di lotto
def test_l4l_ordina_esattamente_il_fabbisogno():
    assert lotto_l4l(35) == 35


def test_foq_arrotonda_al_lotto():
    assert lotto_foq(35, 100) == 100
    assert lotto_foq(100, 100) == 100
    assert lotto_foq(130, 100) == 200


#(60 + 30 + 65) - 0 - 60 + 30 = 125
def test_poq_copre_tre_settimane():
    fabbisogni: dict[int, float] = {3: 60, 4: 30, 5: 65}
    assert lotto_poq(fabbisogni, {}, 60, 30, settimana=3, periodo=3, orizzonte=8) == 125


#(60 + 30 + 65) - 50 - 60 + 30 = 75
def test_poq_con_arrivo_programmato():
    fabbisogni: dict[int, float] = {3:60, 4:30, 5:65}
    arrivi: dict[int, float] = {4:50}
    assert lotto_poq(fabbisogni, arrivi, 60, 30, settimana=3, periodo=3, orizzonte=8) == 75


#in settimana 7 copro solo 7 e 8 -> (70 + 40) - 0 - 30 + 30 = 110
def test_poq_finestra_tagliata_fine_orizzonte():
    fabbisogni: dict[int, float] = {7: 70, 8: 40}
    assert lotto_poq(fabbisogni, {}, 30, 30, settimana=7, periodo=3, orizzonte=8) == 110


#livelli distinta
def test_livelli_componenti_comuni():
    modello = carica_modello()
    livelli = calcola_livelli(modello["prodotto_finito"], modello["distinte"])
    assert livelli["GRPPIEDEDX"] == 0
    assert livelli["CD99000"] == 2   #compare ai livelli 1,2 -> vale il più profondo
    assert livelli["CD17000"] == 4   #compare ai livelli 1,2,3,4
    assert len(livelli) == 202       #tutti gli articoli sono raggiungibili


#record MRP di un singolo articolo
def test_record_prodotto_finito_foq():
    modello = carica_modello()
    pf = modello["anagrafica"]["GRPPIEDEDX"]
    fabbisogni: dict[int, float] = {1: 55, 2: 25, 3: 60, 4: 30, 5: 65, 6: 35, 7: 70, 8: 40}
    record = calcola_record(pf, fabbisogni, 8)

    assert record ["disponibile_previsto"] == [85, 60, 100, 70, 105, 70, 100, 60]
    assert record ["arrivi_pianificati"] == [0, 0, 100, 0, 100, 0, 100, 0]
    assert record ["emissione_ordini"] == [0, 100, 0, 100, 0, 100, 0, 0]

    #la disponibilità non scende mai sotto la scorta di sicurezza
    assert min (record["disponibile_previsto"]) >= pf["scorta_sicurezza"]


def test_ordine_da_sollecitare():
    modello = carica_modello()
    disco = modello["anagrafica"]["CD73000"]    #L4L, lead time 3, arrivo 60 in settimana 1
    record = calcola_record(disco, {2:100, 5: 100}, 8)

    primo_ordine = record["ordini"][0]
    assert primo_ordine["quantita"] == 20
    assert primo_ordine["settimana_emissione"] == -1
    assert primo_ordine["da_sollecitare"] is True


#esplosione MRP completa
def test_fabbisogno_lordo_componente_comune():
    #CD17000 in settimana 2: 8x100 (dal prodotto finito) + 4x66 (da AS1004) = 1064
    risultato = esegui_mrp(carica_modello())
    assert risultato["record"]["CD17000"]["fabbisogni_lordi"][1] == 1064


def test_nessuna_disponibilita_sotto_scorta():
    #su ogni articolo e in ogni settimana la disponibilità deve restare >= della scorta di sicurezza
    modello = carica_modello()
    risultato = esegui_mrp(modello)
    for codice, record in risultato["record"].items():
        scorta = modello["anagrafica"][codice]["scorta_sicurezza"]
        for valore in record["disponibile_previsto"]:
            assert valore >= scorta, f"{codice} scende sotto la scorta"


def test_scenario_l4l_genera_piu_ordini_del_poq():
    modello = carica_modello()
    ordini_l4l = len(esegui_mrp(modello, "L4L")["ordini"])
    ordini_poq = len(esegui_mrp(modello, "POQ")["ordini"])
    assert ordini_l4l > ordini_poq
    
                     

