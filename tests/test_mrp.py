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
