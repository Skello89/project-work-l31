Project Work L-31 Università Pegaso - Distinta base e MRP

Progetto: Creazione di una distinta base multilivello e di un motore MRP in Python per la pianificazione ordini di acquisto e produzione, con gestione del Lead Time, regole di lotto e scorte


# Oggetto studio

Il prodotto analizzato è il gruppo piede destro (GRPPIEDEDX) di un portale di lavaggio Aquarama srl. 
La distinta reale, prima di essere utilizzata nel progetto, è stata esportata dal gestionale per poi essere ricodificata ed anonimizzata (codici e descrizioni).
L'azienda ha autorizzato la citazione del proprio nome.

> docs/Struttura_BOM.md --> struttura codici padre per livello
> docs/Legenda_Codici.xlsx --> elenco codici ricodificati suddivisi per distinta



# Struttura Progetto

mrp_project/
|------	data/
|	|--- Bom_Articoli.xlsx  --> fonte dati, distinta base e anagrafica articoli
|	|
|	|--- prodotto.json  	--> modello letto da motore MRP, generato da excel_to_json.py
|
|------ docs/
|------ mrp/
|       |--- loader.py		--> caricamento modello
|       |--- livelli.py		--> calcolo livello più basso
|       |--- lotti.py		--> regole di lotto FOQ - POQ - L4L
|       |--- record.py		--> record MRP singolo articolo
|       |--- motore.py		--> esplosione MRP su tutti i livelli
|       |--- tabelle.py		--> tabelle pandas da export Excel
|       |--- stampa.py		--> stampa dei record
|
|------ excel_to_json.py	--> conversione da Excel a Json con controlli
|------ prova_*.py		--> verifica dei singoli moduli
|------ requirements.txt



# Avvio

powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python Excel_to_json.py	    --> rigenera data/prodotto.json dall'Excel
python prova_tabelle.py     --> esegue l'MPR e crea risultati_mrp.xlsx



# Parametri principali

- Orizzonte pianificazione: 8 settimane
- Regole di lottizzazione: FOQ - Lotto fisso, POQ - Periodo fisso, L4L - lotto su lotto
- Articoli: oltre 200 tra acquistati e prodotti, su 4 livelli di distinta
			


# Stato sviluppo

>> Sviluppo iniziato il 20/10/2026 in locale. Su GitHub dal 8/11/2026

- [x] Distinta base e anagrafica articoli
- [x] Conversione Excel a Json con controlli
- [x] Calcolo livelli, regole di lotto, record MRP
- [x] Esplosione MRP completa
- [x] Tabelle sintesi ed export Excel
- [x] Scenari a confronto (tutto L4L / tutto POQ)
- [ ] Dashboard Streamlit
- [ ] Test automatici (pytest)
- [ ] Relazione finale


# Strumenti

Python, pandas, openpyxl, Streamlit, Plotly, pytest, VS Code, Git

Lo sviluppo è stato svolto con il supporto assistente AI (Claude) per la verifica del codice e scrittura guidata conversione da Excel a Json con controlli. Architettura, scelta del prodotto, costruzione e anonimizzazione della distinta base, parametri, scrittura moduli, esecuzione, test e analisi dei risultati sono stati svolti dallo studente. 