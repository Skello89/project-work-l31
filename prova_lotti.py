from mrp.lotti import lotto_l4l, lotto_foq, lotto_poq

print("--- L4L ---")
print("Fabbisogno netto 35 -> ordino", lotto_l4l(35))

print("\n--- FOQ (lotto 100) ---")
print("Fabbisogno netto 35 -> ordino", lotto_foq(35,100))
print("Fabbisogno netto 100 -> ordino", lotto_foq(100, 100))
print("Fabbisogno netto 130 -> ordino", lotto_foq(130, 100))

print("\n--- POQ (P = 3) ---")

fabbisogni: dict[int,float] = {1: 55, 2: 25, 3: 60, 4: 30, 5: 65, 6: 35, 7: 70, 8: 40}
arrivi: dict[int, float] = {4: 50}
disponibile = 60

q= lotto_poq(fabbisogni, arrivi, disponibile, scorta=30, settimana=3, periodo=3, orizzonte=8)

disponibile = disponibile + q
for s in [3, 4, 5]:
    disponibile = disponibile + arrivi.get(s, 0) - fabbisogni[s]
    print("  fine settimana", s, ":", disponibile)

q= lotto_poq(fabbisogni, arrivi, disponibile=30, scorta=30, settimana=7, periodo=3, orizzonte=8)
print("Ordine in settimana 7 (finestra tagliata a fine orizzonte) ->", q)

