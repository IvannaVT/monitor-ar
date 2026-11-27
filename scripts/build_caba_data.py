"""Genera data/caba_data.json (pestaña CABA de index.html) desde data/bases/nivel2_extracto_caba.tsv.

Cada valor sale de una fila del extracto (fila = fila de nivel2_indicadores). No se promedia ni se
completa nada. Uso: python3 scripts/build_caba_data.py [--check]
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / 'data' / 'bases' / 'nivel2_extracto_caba.tsv'
OUT = ROOT / 'data' / 'caba_data.json'
MES = {'2026_08': 'Ago', '2026_09': 'Sep', '2026_10': 'Oct', '2026_11': 'Nov'}
VERIF = {2313, 2314, 2315}  # Oct espacio: cifras de N1, verificar categorías
SEC = {2307, 2308, 2309}  # Oct: Larreta, García Moritán, Otro vía encuestas-argentinas.com (fuente original DC)

rows = []
with open(TSV, encoding='utf-8', newline='') as fh:
    for r in csv.DictReader(fh, delimiter='\t'):
        r['fila'] = int(r['fila']); r['resultado'] = float(r['resultado'])
        import re as _re
        r['mes'] = MES[_re.search(r'_(2026_\d\d)', r['id_informe']).group(1)]
        r['cons'] = r['id_informe'].split('_')[0]
        rows.append(r)


def get(mes, ind, cat, cons='DCCONSULTORES'):
    c = [r for r in rows if r['cons'] == cons and r['mes'] == mes and r['id_indicador'] == ind and r['categoria'].startswith(cat)]
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
for lab, co, cn in [('La Libertad Avanza', 'La Libertad', 'La Libertad'), ('PRO', 'PRO', 'PRO'), ('Peronismo', 'Peronismo', 'Peronismo'), ('Kirchnerismo', 'Kirchnerismo', 'Kirchnerismo'), ('Otro / indefinidos', 'Otro', 'Otro')]:
    pts = {}
    if co:
        r = get('Oct', ES, co); pts['Oct'] = {'v': r['resultado'], 'fila': r['fila']}
    if co and pts['Oct']['fila'] in VERIF: pts['Oct']['ver'] = True
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


def val(cons, mes, ind):
    r = get(mes, ind, '', cons)
    return r['resultado'], r['fila']

COB = [
    {'consultora': 'DC Consultores', 'tipo': 'CONV', 'informes': [
        {'mes': 'Jul', 'campo': '19–22/07', 'muestra': '1.360 · ±2,7', 'carga': 'Solo imagen 50/50 de Macri y Milei', 'estado': 'Parcial', 'serie': 'No comparable: escala sin «regular» ni «no lo conozco»'},
        {'mes': 'Ago', 'campo': '23–27/08', 'muestra': '918 · ±2,5', 'carga': '3 cifras de clima (casa porteña, esperanza, desolación)', 'estado': 'Parcial', 'serie': 'Sin imagen ni voto cargados'},
        {'mes': 'Sep', 'campo': '22–27/09', 'muestra': 'Pendiente de ficha', 'carga': 'Imagen de 13 dirigentes, continuidad/cambio, clima', 'estado': 'Cargado', 'serie': 'Imagen y continuidad/cambio: ALTA con nov'},
        {'mes': 'Oct', 'campo': '22–26/10', 'muestra': '1.360 · ±2,5', 'carga': 'Voto por espacio, Jefatura, continuidad/cambio', 'estado': 'Cargado', 'serie': 'Continuidad/cambio ALTA; Jefatura y espacio MEDIA'},
        {'mes': 'Nov', 'campo': '18–22/11', 'muestra': 'Ver informe', 'carga': 'Voto, Jefatura, imagen, emociones, probabilidad de voto', 'estado': 'Cargado', 'serie': 'Cierra las series sep–nov'},
    ]},
    {'consultora': 'CB Global Data', 'tipo': 'CONV', 'informes': [
        {'mes': 'Sep', 'campo': '21–25/09', 'muestra': '', 'carga': 'Imagen positiva del Jefe de Gobierno de CABA', 'valor': val('CBGLOBALDATA', 'Sep', 'IMG_JEFEGOBIERNO_CABA_POSITIVA_CBGLOBALDATA'), 'serie': 'Un corte; ranking de alcaldes de América Latina'},
        {'mes': 'Nov', 'campo': '08–13/11', 'muestra': '', 'carga': 'Imagen positiva de Milei, Bullrich y Kicillof en CABA', 'valor': None, 'serie': 'Un corte; no se mezcla con DC'},
    ]},
    {'consultora': 'OPSA UBA', 'tipo': 'CONV', 'informes': [
        {'mes': 'Ago', 'campo': '25/08–01/09', 'muestra': '1.258 residentes CABA', 'carga': 'Calificación 1–10 al Gobierno de la Ciudad', 'valor': val('OPSA', 'Ago', 'GESTION_CABA_CALIFICACION_1A10'), 'serie': 'Un corte; escala distinta de la aprobación'},
    ]},
    {'consultora': 'CIF / UTDT', 'tipo': 'CONV', 'informes': [
        {'mes': 'Jul–Nov', 'campo': 'mensual', 'muestra': '', 'carga': 'ICC con apertura CABA', 'serie': 'Serie mensual propia (expectativas)'},
    ]},
    {'consultora': 'IDECBA', 'tipo': 'TEM', 'informes': [
        {'mes': 'Abr–Oct', 'campo': 'mensual', 'muestra': '', 'carga': 'IPCBA', 'serie': 'Serie mensual propia (dato duro)'},
    ]},
]

data = {'cobertura': COB, 'jefatura': {'series': jef}, 'cambio': cambio, 'espacio': {'series': esp}, 'imagen': img, 'prob_voto': prob}
txt = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
if '--check' in sys.argv:
    if OUT.read_text(encoding='utf-8') != txt:
        raise SystemExit('caba_data.json desactualizado')
    print('caba_data.json OK')
else:
    OUT.write_text(txt, encoding='utf-8'); print('escrito', OUT.name)
