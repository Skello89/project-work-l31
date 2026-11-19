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


#impostazioni della pagina e barra laterale
st.set_page_config(page_title="MRP - Project Work 27", layout="wide")
st.title("Pianificazione dei fabbisogni di materiale (MRP)")

modello = carica_modello()
anagrafica = modello["anagrafica"]
orizzonte = modello["orizzonte"]

st.sidebar.header("Impostazioni")
nome_scenario = st.sidebar.radio("Scenario di calcolo", list(SCENARI_DASHBOARD.keys()))
regola_forzata = SCENARI_DASHBOARD[nome_scenario]
st.sidebar.write(f"**Prodotto finito:** {modello['prodotto_finito']}")
st.sidebar.write(f"**Orizzonte:** {orizzonte} settimane")
st.sidebar.write(f"**Articoli:** {len(anagrafica)}")

risultato = calcola_mrp(regola_forzata)
ordini = tabella_ordini(risultato["ordini"])
indicatori = calcola_indicatori(risultato)


#indicatori di sintesi
st.subheader(f"Indicatori di sintesi - {nome_scenario}")
colonna1, colonna2, colonna3, colonna4 = st.columns(4)
colonna1.metric("Ordini pianificati", indicatori["N. Ordini"])
colonna2.metric("Da sollecitare", indicatori["Ordini da sollecitare"])
colonna3.metric("Quantità totale ordinata", indicatori["Quantità totale ordinata"])
colonna4.metric("Scorta media", indicatori["Scorta Media"])


#schede
scheda_bom, scheda_archivio, scheda_record, scheda_ordini, scheda_scenari = st.tabs([
    "Distinta base",
    "Archivio articoli",
    "Record MRP",
    "Piano ordini",
    "Confronto scenari",
])


#distinta base
with scheda_bom:
    st.write("Legami padre -> figlio con coefficiente d'impiego.")
    st.dataframe(tabella_distinta(modello), hide_index=True)


#archivio articoli
with scheda_archivio:
    provenienza = st.radio("Mostra", ["tutti", "produzione", "acquisto"], horizontal=True)
    archivio = tabella_anagrafica(anagrafica)
    if provenienza != "tutti":
        archivio = archivio[archivio["Provenienza"] == provenienza]
    st.write(f"{len(archivio)} articoli")
    st.dataframe(archivio, hide_index=True)


#record MRP di un articolo
with scheda_record:
    codici = list(risultato["record"].keys())
    codice = st.selectbox(
        "Articolo",
        codici,
        format_func=lambda c: f"{c} - {anagrafica[c]['descrizione']}",
    )
    record = risultato["record"][codice]
    articolo = anagrafica[codice]

    info1, info2, info3, info4, info5 = st.columns(5)
    info1.metric("Livello", record["livello"])
    info2.metric("Provenienza", articolo["provenienza"])
    info3.metric("Regola", record["regola"])
    info4.metric("Lead time", f"{articolo['lead_time']} sett.")
    info5.metric("Scorta di sicurezza", articolo["scorta_sicurezza"])

    st.dataframe(tabella_record(record))








