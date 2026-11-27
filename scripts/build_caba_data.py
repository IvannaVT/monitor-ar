"""Genera data/caba_data.json (pestaña CABA de index.html) desde data/bases/nivel2_extracto_caba.tsv.

Cada valor sale de una fila del extracto (fila = fila de nivel2_indicadores). No se promedia ni se
completa nada. Uso: python3 scripts/build_caba_data.py [--check]
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / 'data' / 'bases' / 'nivel2_extracto_caba.tsv'
OUT = ROOT / 'data' / 'caba_data.json'
MES = {'2026_09': 'Sep', '2026_10': 'Oct', '2026_11': 'Nov'}
SEC = {2307, 2308, 2309}  # Oct: Larreta, García Moritán, Otro vía encuestas-argentinas.com (fuente original DC)

rows = []
with open(TSV, encoding='utf-8', newline='') as fh:
    for r in csv.DictReader(fh, delimiter='\t'):
        r['fila'] = int(r['fila']); r['resultado'] = float(r['resultado'])
        r['mes'] = MES[r['id_informe'][len('DCCONSULTORES_'):len('DCCONSULTORES_') + 7]]
        rows.append(r)


def get(mes, ind, cat):
    c = [r for r in rows if r['mes'] == mes and r['id_indicador'] == ind and r['categoria'].startswith(cat)]
    if len(c) != 1:
        raise SystemExit(f'{mes} {ind} {cat}: {len(c)} filas')
    return c[0]


def serie(nombre, ind, cats, meses, **kw):
    out = []
    for lab, cat in cats:
        pts = {}
        for m in meses:
            try:
                r = get(m, ind, cat)
            except SystemExit:
                continue
            pts[m] = {'v': r['resultado'], 'fila': r['fila']}
            if r['fila'] in SEC:
                pts[m]['sec'] = True
        out.append({'nombre': lab, 'puntos': pts})
    return {'titulo': nombre, 'series': out, **kw}


JD = 'CONV_DCCAB_JDEG_CANDIDATOS_CABA'; JN = 'VOTO_CABA_JEFATURA_GOBIERNO_ESCENARIO_NOV_DC'
jef = []
for lab, co, cn in [('Patricia Bullrich', 'Patricia Bullrich', 'Patricia Bullrich'), ('Jorge Macri', 'Jorge Macri', 'Jorge Macri'),
                    ('Leandro Santoro', 'Leandro Santoro', 'Leandro Santoro'), ('Horacio Rodríguez Larreta', 'Horacio', 'Horacio'),
                    ('Roberto García Moritán', 'Roberto', 'Roberto'), ('Otro', 'Otro', 'Otro')]:
    pts = {}
    for m, ind, c in (('Oct', JD, co), ('Nov', JN, cn)):
        r = get(m, ind, c); pts[m] = {'v': r['resultado'], 'fila': r['fila']}
        if r['fila'] in SEC: pts[m]['sec'] = True
    jef.append({'nombre': lab, 'puntos': pts})

CC = 'VOTO_CABA_CONTINUIDAD_CAMBIO_2027'
cambio = serie('Continuidad o cambio · 2027', CC, [('Cambio de rumbo total', 'Cambio'), ('Continuidad de J. Macri y PRO', 'Continuidad de Jorge'), ('Continuidad de la LLA (sin J. Macri)', 'Continuidad pero')], ['Sep', 'Oct', 'Nov'])

ES = 'CONV_DCCAB_VOTO_ESPACIO_CABA'; EN = 'VOTO_CABA_ESPACIO_2027_DC'
esp = []
for lab, co, cn in [('La Libertad Avanza', 'La Libertad', 'La Libertad'), ('PRO', 'PRO', 'PRO'), ('Peronismo', None, 'Peronismo'), ('Kirchnerismo', None, 'Kirchnerismo'), ('Otro / indefinidos', None, 'Otro')]:
    pts = {}
    if co:
        r = get('Oct', ES, co); pts['Oct'] = {'v': r['resultado'], 'fila': r['fila']}
    r = get('Nov', EN, cn); pts['Nov'] = {'v': r['resultado'], 'fila': r['fila']}
    esp.append({'nombre': lab, 'puntos': pts})

img = []
for lab, key in [('Patricia Bullrich', 'PATRICIA_BULLRICH'), ('Sandra Pettovello', 'SANDRA_PETTOVELLO'), ('Javier Milei', 'JAVIER_MILEI'),
                 ('Victoria Villarruel', 'VICTORIA_VILLARRUEL'), ('Jorge Macri', 'JORGE_MACRI'), ('Axel Kicillof', 'AXEL_KICILLOF')]:
    d = {'nombre': lab, 'pos': {}, 'neg': {}}
    for m in ('Sep', 'Nov'):
        for k, suf in (('pos', 'POSITIVA'), ('neg', 'NEGATIVA')):
            try:
                r = get(m, f'IMG_{key}_{suf}_CABA_DC', ''); d[k][m] = {'v': r['resultado'], 'fila': r['fila']}
            except SystemExit:
                pass
    img.append(d)

prob = []
for lab, key in [('Javier Milei', 'MILEI'), ('Patricia Bullrich', 'BULLRICH'), ('Leandro Santoro', 'SANTORO'), ('Jorge Macri', 'JORGE_MACRI'),
                 ('Axel Kicillof', 'KICILLOF'), ('Horacio Rodríguez Larreta', 'LARRETA'), ('Cristina Kirchner', 'CFK'), ('Sandra Pettovello', 'PETTOVELLO')]:
    r = get('Nov', f'PROB_VOTO_{key}_CABA_DC', ''); prob.append({'nombre': lab, 'v': r['resultado'], 'fila': r['fila']})

data = {'jefatura': {'series': jef}, 'cambio': cambio, 'espacio': {'series': esp}, 'imagen': img, 'prob_voto': prob}
txt = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
if '--check' in sys.argv:
    if OUT.read_text(encoding='utf-8') != txt:
        raise SystemExit('caba_data.json desactualizado')
    print('caba_data.json OK')
else:
    OUT.write_text(txt, encoding='utf-8'); print('escrito', OUT.name)
