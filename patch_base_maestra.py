#!/usr/bin/env python3
"""Patch two RD rows in base_maestra_work.csv"""
import sys

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'r', encoding='utf-8', newline='') as f:
    content = f.read()

# --- Row 1: IDN Q2 Junio ---
old1 = ('2026_06,2026,06,REPUTACION DIGITAL,Indice de Disonancia Narrativa (Junio),'
        'No informado en el documento,pdf,2026-07-03,1jpHqehxYG6UncLXhOifvamXQolHEPJRC,'
        'https://drive.google.com/file/d/1jpHqehxYG6UncLXhOifvamXQolHEPJRC/view,SL,,,,,,,,,,,,')
new1 = ('2026_06,2026,06,REPUTACION DIGITAL,Indice de Disonancia Narrativa (Junio),'
        'No informado en el documento,pdf,2026-07-03,1jpHqehxYG6UncLXhOifvamXQolHEPJRC,'
        'https://drive.google.com/file/d/1jpHqehxYG6UncLXhOifvamXQolHEPJRC/view,'
        'SL,,2026-04-01,2026-06-30,Nacional,'
        '"Conversacion digital (redes sociales y radio en streaming)",'
        '"+6.5M menciones generales; 550k depuradas (Filtro Sudor)",'
        '"NLP + LLM propia (sentimiento y emocion tropicalizados)",'
        ',,,'
        '"Estudio Q2 2026 version preliminar. IDN=61 (umbral divorcio). Dataset definitivo pendiente.",'
        'procesado')

# --- Row 2: Scaloneta Julio ---
old2 = ('2026_07,2026,07,REPUTACION DIGITAL,'
        '"La Scaloneta le da aire al gobierno (Julio, raiz carpeta Julio)",'
        'No informado en el documento,pdf,2026-07-14,1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR,'
        'https://drive.google.com/file/d/1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR/view,SL,,,,,,,,,,,,')
new2 = ('2026_07,2026,07,REPUTACION DIGITAL,'
        '"La Scaloneta le da aire al gobierno (Julio, raiz carpeta Julio)",'
        'No informado en el documento,pdf,2026-07-14,1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR,'
        'https://drive.google.com/file/d/1SPR2bb31TVH7vV_5o5VCKaxSEhztGmHR/view,'
        'SL,,2026-07-01,2026-07-08,Nacional,'
        '"Conversacion digital (Twitter/X y otras plataformas)",'
        '"162.000 menciones (corpus 1-8 julio 2026)",'
        '"NLP + LLM propia",'
        ',,,'
        '"Corpus 1-8 julio 2026. ISN futbol+politica=-72.2; ISN Casa Rosada=-80.5; ISN Milei=-66.9; ira 36% asco 31% alegria 3%.",'
        'procesado')

if old1 not in content:
    print("ERROR: old1 not found", file=sys.stderr)
    sys.exit(1)
if old2 not in content:
    print("ERROR: old2 not found", file=sys.stderr)
    sys.exit(1)

content = content.replace(old1, new1, 1)
content = content.replace(old2, new2, 1)

with open(outfile, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("Done. Patched 2 rows.")
