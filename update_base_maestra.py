with open('/home/claude/monitor-ar/base_maestra_work.csv', 'r', encoding='utf-8') as f:
    content = f.read()

# Update 1: RD IDN Junio (1jpHqehxYG6UncLXhOifvamXQolHEPJRC)
old1 = '1jpHqehxYG6UncLXhOifvamXQolHEPJRC,https://drive.google.com/file/d/1jpHqehxYG6UncLXhOifvamXQolHEPJRC/view,SL,,,,,,,,,,,\r\n'
new1 = '1jpHqehxYG6UncLXhOifvamXQolHEPJRC,https://drive.google.com/file/d/1jpHqehxYG6UncLXhOifvamXQolHEPJRC/view,SL,,2026-04-01,2026-06-30,Nacional,"Conversacion digital (redes sociales y radio en streaming)","+6.5M menciones generales; 550k depuradas (Filtro Sudor)","NLP + LLM propia (sentimiento y emocion tropicalizados)",,,,\"Estudio Q2 2026 version preliminar. IDN=61 (umbral divorcio). Dataset definitivo pendiente.\",procesado\r\n'

# Update 2: RD Scaloneta Julio raiz (1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR)
old2 = '1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR,https://drive.google.com/file/d/1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR/view,SL,,,,,,,,,,,\r\n'
new2 = '1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR,https://drive.google.com/file/d/1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR/view,SL,,2026-07-01,2026-07-08,Nacional,"Conversacion digital (Twitter/X y otras plataformas)","162.000 menciones (corpus 1-8 julio 2026)","NLP + LLM propia",,,,\"Corpus 1-8 julio 2026. ISN futbol+politica=-72.2; ISN Casa Rosada=-80.5; ISN Milei=-66.9; ira 36% asco 31% alegria 3%.\",procesado\r\n'

count1 = content.count(old1)
count2 = content.count(old2)
print(f"Match 1 (IDN Junio): {count1}")
print(f"Match 2 (Scaloneta Julio): {count2}")

if count1 == 1:
    content = content.replace(old1, new1)
    print("Replaced IDN Junio OK")
else:
    print("ERROR: IDN Junio match not found or ambiguous")

if count2 == 1:
    content = content.replace(old2, new2)
    print("Replaced Scaloneta Julio OK")
else:
    print("ERROR: Scaloneta Julio match not found or ambiguous")

with open('/home/claude/monitor-ar/base_maestra_work.csv', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done. File written.")
