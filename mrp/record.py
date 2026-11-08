from mrp.lotti import calcola_quantita

#calcolo del record MRP del singolo articolo sull'orizzonte di pianificazione
def calcola_record(
    articolo: dict,
    fabbisogni_lordi: dict[int, float],
    orizzonte: int,
    regola: str | None = None,
) -> dict:

    # restituisce record MRP articolo: riga -> voce, colonna -> settimana, ed elenco ordini pianificati
    # fabbisogni_lordi -> settimana:quantita -> richiesti dall'articolo
    # regola, se indicata sostituisce la regola dell'articolo

    if regola is None:
        regola = str(articolo["regola"])

    arrivi_programmati = articolo["arrivi_programmati"]
    scorta = articolo["scorta_sicurezza"]
    lead_time = articolo["lead_time"]

    #liste contenenti valore per settimana
    riga_lordi: list[float] = []
    riga_programmati: list[float] = []
    riga_disponibile: list[float] = []
    riga_netti: list[float] = []
    riga_pianificati: list[float] = []
    emissioni: dict[int, float] = {}
    ordini: list[dict] = []

    disponibile = articolo["giacenza_iniziale"]

    for t in range(1, orizzonte + 1):
        lordo = fabbisogni_lordi.get(t, 0)
        programmato = arrivi_programmati.get(t, 0)

        disponibile_senza_ordine = disponibile + programmato - lordo #disponibilità prima di ordini
        #se scendo sotto la scorta di sicurezza necessito di fabbisogno netto
        netto = 0
        pianificato = 0
        if disponibile_senza_ordine < scorta:
            netto = round(scorta - disponibile_senza_ordine, 3)
            pianificato = calcola_quantita(
                regola, articolo, netto, fabbisogni_lordi, disponibile, t, orizzonte
        )
            pianificato = round(pianificato, 3)

        disponibile = round(disponibile_senza_ordine + pianificato, 3) #disponibilità finale della settimana

        if pianificato > 0:
            settimana_emissione = t - lead_time
            emissioni[settimana_emissione] = emissioni.get(settimana_emissione, 0) + pianificato
            ordini.append({
                "codice": articolo["codice"],
                "descrizione": articolo["descrizione"],
                "quantita": pianificato,
                "settimana_emissione": settimana_emissione,
                "settimana_arrivo": t,
                "provenienza": articolo["provenienza"],
                "da_sollecitare": settimana_emissione < 1,
            })

        riga_lordi.append(lordo)
        riga_programmati.append(programmato)
        riga_disponibile.append(disponibile)
        riga_netti.append(netto)
        riga_pianificati.append(pianificato)

    #riga emissione ordini sulle settimane orizzonte
    riga_emissioni: list[float] = []
    for t in range(1, orizzonte + 1):
        riga_emissioni.append(emissioni.get(t, 0))

    return {
        "codice": articolo["codice"],
        "regola": regola,
        "giacenza_iniziale": articolo["giacenza_iniziale"],
        "fabbisogni_lordi": riga_lordi,
        "arrivi_programmati": riga_programmati,
        "disponibile_previsto": riga_disponibile,
        "fabbisogni_netti": riga_netti,
        "arrivi_pianificati": riga_pianificati,
        "emissione_ordini": riga_emissioni,
        "emissioni": emissioni,
        "ordini": ordini,
    }




