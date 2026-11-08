
# calcolo del codice dal livello più basso in modo crescente
# creazione dizionario livello più basso
# inserisco -1 e il primo livello trovato viene sempre registrato
# scendo nei componenti di livello più basso
# parto dal prodotto finito a livello 0
def calcola_livelli(prodotto_finito: str, distinte: dict[str, list[dict]]) -> dict[str, int]:
    livelli: dict[str, int] = {}
    
    def assegna_livello(codice: str, livello: int) -> None:
        if livello > livelli.get(codice, -1):
            livelli[codice] = livello
            for componente in distinte.get(codice, []):
                assegna_livello(componente["figlio"], livello + 1)

    assegna_livello(prodotto_finito, 0)
    return livelli

# ordino e restituisco lista codici dal livello 0 al più basso 
def ordina_per_livello(livelli: dict[str, int]) -> list[str]:
    return sorted(livelli, key=lambda codice: livelli[codice])





