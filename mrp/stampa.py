#funzioni di stampa a terminale usate nei file come test per verificare i dati

def stampa_record(record: dict, orizzonte: int) -> None:
    print(f"\nRecord MRP di {record['codice']} (regola {record['regola']}, "
          f"giacenza iniziale {record['giacenza_iniziale']})")
    intestazione = f"{'Settimana':<22}"
    for t in range(1, orizzonte + 1):
        intestazione += f"{t:>7}"
    print(intestazione)
    voci = [
        ("Fabbisogno lordo", "fabbisogni_lordi"),
        ("Arrivi programmati", "arrivi_programmati"),
        ("Disponibile previsto", "disponibile_previsto"),
        ("Fabbisogno netto", "fabbisogni_netti"),
        ("Arrivi pianificati", "arrivi_pianificati"),
        ("Emissione ordini", "emissione_ordini"),
    ]
    for nome, chiave in voci:
        riga = f"{nome:<22}"
        for valore in record[chiave]:
            riga += f"{valore:>7}"
        print(riga)
    print("Ordini:")
    for ordine in record["ordini"]:
        nota = "  <-- DA SOLLECITARE" if ordine["da_sollecitare"] else ""
        print(f"  {ordine['quantita']} pezzi: emissione settimana {ordine['settimana_emissione']}, "
              f"arrivo settimana {ordine['settimana_arrivo']}{nota}")

