#dashboard del progetto MRP
#avvio dal terminale, nella cartella del progetto: streamlit run app.py
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from mrp.loader import carica_dati
from mrp.motore import esegui_mrp
from mrp.scenari import confronta_scenari
from mrp.tabelle import (
    calcola_indicatori,
    tabella_anagrafica,
    tabella_articoli,
    tabella_distinta,
    tabella_ordini,
    tabella_record,
)

PERCORSO_JSON = Path(__file__).parent / "data" / "prodotto.json"

#scenari selezionabili: nome mostrato -> regola forzata -> None = regole archivio
SCENARI_DASHBOARD = {
    "Base (regole da archivio)": None,
    "Tutto L4L": "L4L",
    "Tutto POQ": "POQ",
}


#funzioni di supporto
#legge Json una sola volta, successivamente Streamlit riutilizza il risultato
@st.cache_data
def carica_modello() -> dict:
    return carica_dati(PERCORSO_JSON)


#esegue MRP per lo scenario scelto -> risultato memorizzato per ogni scenario
@st.cache_data
def calcola_mrp(regola_forzata: str | None) -> dict:
    return esegui_mrp(carica_modello(), regola_forzata)


#tabella di confronto tra i tre scenari
@st.cache_data
def calcola_confronto() -> pd.DataFrame:
    return confronta_scenari(carica_modello())


#righe ordini da sollecitare evidenziate di rosso
def evidenzia_solleciti(riga: pd.Series) -> list[str]:
    if riga["Da sollecitare"]:
        return ["background-color: #f8d7da"] * len(riga)
    return [""] * len(riga)


#converte una tabella in un file Excel tenuto in memoria
def in_excel(tabella: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    tabella.to_excel(buffer, index=False)
    return buffer.getvalue()





