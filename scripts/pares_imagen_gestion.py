#!/usr/bin/env python3
"""Pares imagen de Milei × valoración de la gestión nacional.

Lee data/bases/nivel2_extracto_pares.tsv (extracto de Nivel 2 con pregunta, universo y link)
y devuelve el bloque PARES de radar_data.json. No contiene valores cargados a mano.

Reglas (todas verificables en la auditoría):
- Ola = misma consultora + mismo mes enunciado + mismas fechas de campo (si ambas figuran);
  sin fecha de campo, solo se agrupa dentro del mismo archivo fuente.
- Par favorable = imagen positiva + aprobación; par desfavorable = imagen negativa + desaprobación.
  Cada comparación es independiente. No se completa una cifra faltante.
- Mismo universo (texto normalizado) obligatorio; si difiere, el par se excluye.
- Cambio = diferencia entre dos olas consecutivas de la misma consultora, ambas con par completo;
  si entre ellas hay una ola intermedia con alguna de las dos medidas sin par, el cambio se excluye.
"""
import csv
import datetime
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MESES = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

CANON = [('ATLAS', 'AtlasIntel'), ('ANALOG', 'Analogías'), ('CELAG', 'CELAG'), ('ALESSIO', "D'Alessio"),
         ('DC CONSULT', 'DC Consultores'), ('EQUIPO MIDE', 'Equipo Mide'), ('ESPOP', 'ESPOP (UdeSA)'),
         ('GIACOBBE', 'Giacobbe'), ('ISASI', 'Isasi-Burdman'), ('MANAGEMENT', 'Management & Fit'),
         ('MYF', 'Management & Fit'), ('MANAGFIT', 'Management & Fit'), ('OPSA', 'OPSA (UBA)'),
         ('OPINA', 'Opina Argentina'), ('PROYECC', 'Proyección'), ('PULSO', 'Pulso Research'),
         ('QMONITOR', 'QMonitor'), ('QSOCIAL', 'QSocial'), ('REAL', 'Reale Dalla Torre'),
         ('RDT', 'Reale Dalla Torre'), ('SYNOPSIS', 'Synopsis'), ('TRENDS', 'Trends'),
         ('ZENTRIX', 'Zentrix'), ('ZUBAN', 'Zuban Córdoba'), ('INNOVA', 'INNOVA'), ('EXPLANANS', 'Explanans')]

SUF = r'(_NAC|_DC|_GIACOBBE|_UDESA|_SYNOPSIS)?'
GSUF = r'(_(MILEI_ICP|MILEI|PROYECCION|QMONITOR|ATLASINT|MANAGFIT|UDESA|SYNOPSIS))?'
RE_ROL = [
    ('img_pos', re.compile(r'^IMG_MILEI_POSITIVA' + SUF + '$')),
    ('img_neg', re.compile(r'^IMG_MILEI_NEGATIVA' + SUF + '$')),
    ('gest_aprob', re.compile(r'^GESTION_NAC(IONAL)?_(APROBACION|POSITIVA)' + GSUF + '$')),
    ('gest_desaprob', re.compile(r'^GESTION_NAC(IONAL)?_(DESAPROBACION|NEGATIVA)' + GSUF + '$')),
]


def canon(c):
    u = unicodedata.normalize('NFKD', c).encode('ascii', 'ignore').decode().upper()
    for k, v in CANON:
        if k in u:
            return v
    return c.strip()


def norm_txt(s):
    s = unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', s).split())


def norm_univ(s):
    t = norm_txt(s).replace('anios', 'anos')
    t = re.sub(r'\b(residentes )?(en )?(la )?(republica )?argentina\b', ' ', t)
    return ' '.join(t.split())


def a_num(t):
    t = str(t).strip().replace(',', '.')
    try:
        return round(float(t), 2)
    except ValueError:
        return None


def a_fecha(s):
    s = str(s).strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        return s
    m = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', s)
    if m:
        return f'{m[3]}-{m[2]}-{m[1]}'
    if re.fullmatch(r'\d{5}', s):  # serial de planilla
        return (datetime.date(1899, 12, 30) + datetime.timedelta(int(s))).isoformat()
    return ''


def a_mes(s):
    m = re.search(r'CORRECCION[^:]*:\s*(\d+)', s)
    if m:
        return int(m[1])
    m = re.match(r'\s*(\d+)', s)
    return int(m[1]) if m else None


def cargar(path=None):
    path = path or ROOT / 'data' / 'bases' / 'nivel2_extracto_pares.tsv'
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def construir_pares(filas, meses_eje):
    obs = []
    for r in filas:
        rol = next((k for k, rx in RE_ROL if rx.match(r['id_indicador'])), None)
        if not rol:
            continue
        o = dict(fila=int(r['fila']), rol=rol, cons=canon(r['consultora']), mes=a_mes(r['mes']),
                 ci=a_fecha(r['fecha_campo_inicio']), cf=a_fecha(r['fecha_campo_fin']),
                 val=a_num(r['resultado']), raw=r['resultado'], cat=r['categoria_respuesta'],
                 preg=r['pregunta_original'], univ=r['universo'], muestra=r['muestra'],
                 file=r['archivo_fuente_file_id'], link=r['link'], titulo=r['informe_titulo'],
                 idinf=r['id_informe'].split(' | ')[0], iddic=r['id_indicador'])
        obs.append(o)
    # ── olas ──
    olas = defaultdict(list)
    for o in obs:
        if o['ci'] and o['cf']:
            k = (o['cons'], o['mes'], o['ci'], o['cf'])
        else:
            k = (o['cons'], o['mes'], 'sin_campo', o['file'])
        olas[k].append(o)
    res_olas = []
    for k, lst in olas.items():
        ola = dict(cons=k[0], mes=k[1], ci=k[2] if k[2] != 'sin_campo' else '', cf=k[3] if k[2] != 'sin_campo' else '',
                   sin_campo=(k[2] == 'sin_campo'), medidas={}, conflictos=[], filas=[o['fila'] for o in lst])
        por_rol = defaultdict(list)
        for o in lst:
            por_rol[o['rol']].append(o)
        for rol, os_ in por_rol.items():
            num = [o for o in os_ if o['val'] is not None]
            if not num:
                ola['conflictos'].append(f"{rol}: sin cifra publicada en la base (fila {os_[0]['fila']}: «{os_[0]['raw']}»)")
                continue
            vals = {o['val'] for o in num}
            if max(vals) - min(vals) > 0.051:
                ola['conflictos'].append(f"{rol}: cifras discrepantes {sorted(vals)} (filas {[o['fila'] for o in num]})")
                continue
            # preferida: con fuente en Drive y menor fila
            num.sort(key=lambda o: (o['file'].startswith('No aplica'), o['fila']))
            p = num[0]
            ola['medidas'][rol] = dict(val=p['val'], fila=p['fila'], cat=p['cat'], preg=p['preg'], univ=p['univ'],
                                       file=p['file'], link=p['link'], titulo=p['titulo'], idinf=p['idinf'],
                                       muestra=p['muestra'], filas_dup=[o['fila'] for o in num[1:]],
                                       secundaria=p['file'].startswith('No aplica'))
        res_olas.append(ola)
    fechadas = defaultdict(list)
    for a in res_olas:
        if not a['sin_campo']:
            fechadas[(a['cons'], a['mes'])].append(a)
    replicas = []
    vivas = []
    for a in res_olas:
        rep = None
        if a['sin_campo'] and a['medidas'] and not a['conflictos']:
            for b in fechadas[(a['cons'], a['mes'])]:
                if all(r in b['medidas'] and abs(b['medidas'][r]['val'] - mm['val']) < 0.051 for r, mm in a['medidas'].items()):
                    rep = b
                    break
        if rep:
            for r, mm in a['medidas'].items():
                rep['medidas'][r]['filas_dup'] = sorted(set(rep['medidas'][r]['filas_dup'] + [mm['fila']]))
            replicas.append(dict(cons=a['cons'], mes=a['mes'], filas=a['filas'], de=rep['ci']))
        else:
            vivas.append(a)
    res_olas = vivas
    res_olas.sort(key=lambda a: (a['cons'], a['mes'] or 0, a['ci'] or '9', a['medidas'].get('img_pos', a['medidas'].get('gest_aprob', {})).get('file', '')))
    # ── pares por ola ──
    mes_con = defaultdict(list)
    for a in res_olas:
        mes_con[(a['cons'], a['mes'])].append(a)
    audit = []
    for a in res_olas:
        m = a['medidas']
        for panel, ri, rg, ni, ng in (('fav', 'img_pos', 'gest_aprob', 'imagen positiva', 'aprobación'),
                                       ('des', 'img_neg', 'gest_desaprob', 'imagen negativa', 'desaprobación')):
            ent = dict(cons=a['cons'], mes=a['mes'], panel=panel, ci=a['ci'], cf=a['cf'], clave=_clave(a), estado=None, motivo='',
                       imagen=None, gestion=None)
            have_i, have_g = ri in m, rg in m
            if have_i:
                ent['imagen'] = m[ri]
            if have_g:
                ent['gestion'] = m[rg]
            if have_i and have_g:
                ui, ug = norm_univ(m[ri]['univ']), norm_univ(m[rg]['univ'])
                if ui != ug:
                    ent['estado'] = 'excluido'
                    ent['motivo'] = 'redacción de universo distinta entre imagen y gestión (verificar en el informe): «%s» vs «%s»' % (m[ri]['univ'], m[rg]['univ'])
                else:
                    ent['estado'] = 'incluido'
                    sec = m[ri]['secundaria'] or m[rg]['secundaria']
                    if sec:
                        ent['motivo'] = 'incluye una cifra de fuente secundaria (evidencia máx. MEDIA)'
                    ent['gap'] = round(m[rg]['val'] - m[ri]['val'], 1)
            elif not have_i and not have_g:
                continue
            else:
                faltante, presente = (ni, ng) if have_g else (ng, ni)
                otras = [b for b in mes_con[(a['cons'], a['mes'])] if b is not a and ((rg if have_i else ri) in b['medidas'])]
                conf = [c for c in a['conflictos'] if c.startswith(rg if not have_g else ri)]
                if conf:
                    mot = f'falta {faltante}: {conf[0]}'
                elif otras:
                    mot = (f'falta {faltante} en esta ola; la publica otra medición del mismo mes sin campo coincidente'
                           f' (misma ola no confirmable)')
                else:
                    mot = f'falta {faltante} publicada en la ola; solo está {presente}'
                ent['estado'] = 'incompleto'
                ent['motivo'] = mot
            audit.append(ent)
    # ── cambios ──
    cambios = []
    cambios_excl = []
    fam = {'fav': ('img_pos', 'gest_aprob'), 'des': ('img_neg', 'gest_desaprob')}
    por_cons = defaultdict(list)
    for a in res_olas:
        por_cons[a['cons']].append(a)
    estado = {(e['cons'], e['mes'], e['ci'], e['panel'], e['clave']): e for e in audit}
    for cons, lst in por_cons.items():
        for panel, (ri, rg) in fam.items():
            seq = [a for a in lst if ri in a['medidas'] or rg in a['medidas']]
            for x, y in zip(seq, seq[1:]):
                ex, ey = estado.get((cons, x['mes'], x['ci'], panel, _clave(x))), estado.get((cons, y['mes'], y['ci'], panel, _clave(y)))
                if not (ex and ey and ex['estado'] == 'incluido' and ey['estado'] == 'incluido'):
                    # cambio entre olas consecutivas sin par completo: no se calcula
                    continue
                cambios.append(_cambio(cons, panel, x, y, ri, rg))
            # cambios que saltean una ola intermedia sin par
            comp = [a for a in seq if estado.get((cons, a['mes'], a['ci'], panel, _clave(a)), {}).get('estado') == 'incluido']
            for x, y in zip(comp, comp[1:]):
                if seq.index(y) - seq.index(x) > 1:
                    cambios_excl.append(dict(cons=cons, panel=panel, desde=_etq(x), hasta=_etq(y),
                                             motivo='saltea una ola intermedia con alguna medida sin par comparable'))
    return dict(obs=obs, olas=res_olas, audit=audit, cambios=cambios, cambios_excl=cambios_excl, replicas=replicas)


def _clave(a):
    return '' if not a['sin_campo'] else next(iter(a['medidas'].values()))['file'] if a['medidas'] else ''


def _etq(a):
    return f"{MESES[a['mes']]}-26"


def _cambio(cons, panel, x, y, ri, rg):
    mi0, mi1, mg0, mg1 = x['medidas'][ri], y['medidas'][ri], x['medidas'][rg], y['medidas'][rg]
    d_img, d_ges = round(mi1['val'] - mi0['val'], 1), round(mg1['val'] - mg0['val'], 1)
    dias = None
    if x['ci'] and y['ci']:
        dias = (datetime.date.fromisoformat(y['ci']) - datetime.date.fromisoformat(x['ci'])).days

    def sg(v):
        return 0 if abs(v) < 0.05 else (1 if v > 0 else -1)
    si, sgn = sg(d_img), sg(d_ges)
    if si == 0 or sgn == 0:
        tipo = 'estable'
    elif si == sgn:
        tipo = 'misma_direccion'
    else:
        tipo = 'opuesta'
    return dict(cons=cons, panel=panel, desde=_etq(x), hasta=_etq(y), mes0=x['mes'], mes1=y['mes'],
                ci0=x['ci'], cf0=x['cf'], ci1=y['ci'], cf1=y['cf'], dias=dias, meses=y['mes'] - x['mes'],
                img0=mi0['val'], img1=mi1['val'], ges0=mg0['val'], ges1=mg1['val'], d_img=d_img, d_ges=d_ges,
                tipo=tipo, fila_img0=mi0['fila'], fila_img1=mi1['fila'], fila_ges0=mg0['fila'], fila_ges1=mg1['fila'],
                link0=mi0['link'] or mg0['link'], link1=mi1['link'] or mg1['link'])


# ───────────── bloque serializable para radar_data.json ─────────────
def _fmt(v):
    return f'{v:.1f}'.replace('.', ',')


def _pp(v):
    return ('+' if v > 0 else '−' if v < 0 else '') + _fmt(abs(v)).replace(',0', '') + ' pp'


def _lectura(panel, cambios, pares, umbral_cambios=12, umbral_cons=5):
    cs = [c for c in cambios if c['panel'] == panel]
    ps = [p for p in pares if p['panel'] == panel]
    ncons = len({c['cons'] for c in cs})
    if not cs:
        return ['Sin cambios entre olas consecutivas comparables: no hay lectura de co-movimiento.']

    def lista(tipo):
        por = defaultdict(list)
        for c in cs:
            if c['tipo'] == tipo:
                por[c['cons']].append(f"{c['desde'][:3].lower()}–{c['hasta'][:3].lower()}")
        return ', '.join(f"{k} ({', '.join(v)})" for k, v in sorted(por.items()))
    n = len(cs)
    k = {t: sum(1 for c in cs if c['tipo'] == t) for t in ('misma_direccion', 'opuesta', 'estable')}
    segs = []
    for t, et in (('misma_direccion', 'en la misma dirección'), ('opuesta', 'en direcciones opuestas'),
                  ('estable', 'con una medida sin variación')):
        if k[t]:
            segs.append(f"{k[t]} {et} ({lista(t)})")
    l1 = f"{n} cambios entre olas consecutivas de {ncons} consultoras: " + '; '.join(segs) + '.'
    por = defaultdict(list)
    for p in ps:
        por[p['cons']].append(p['gap'])
    multi = {c: g for c, g in por.items() if len(g) >= 2}
    est = sorted(c for c, g in multi.items() if max(g) - min(g) <= 2.0)
    var = sorted(c for c, g in multi.items() if max(g) - min(g) > 2.0)
    todos = [p['gap'] for p in ps]
    l2 = (f"Brecha gestión − imagen de {_fmt(min(todos))} a {_fmt(max(todos))} pp ({len(ps)} olas); estable (rango ≤2 pp) en "
          f"{len(est)} de {len(multi)} consultoras con 2 o más olas"
          + (f"; varía en {', '.join(var)}." if var else '.'))
    if n >= umbral_cambios and ncons >= umbral_cons:
        l3 = 'Cobertura suficiente para estimar correlación intra-consultora (ver nota metodológica).'
    else:
        l3 = (f"Cobertura insuficiente para correlación ({n} cambios, {ncons} consultoras; mínimo {umbral_cambios} y {umbral_cons}). "
              "Lectura sobre porcentajes agregados, no sobre personas.")
    return [l1, l2, l3]


def bloque(filas, meses_eje):
    R = construir_pares(filas, meses_eje)
    audit = []
    for e in R['audit']:
        im, ge = e['imagen'], e['gestion']
        ent = dict(cons=e['cons'], mes=meses_eje[e['mes'] - 5] if False else f"{MESES[e['mes']]}-26", panel=e['panel'],
                   campo_ini=e['ci'], campo_fin=e['cf'], estado=e['estado'], motivo=e['motivo'])
        for pref, m in (('img', im), ('ges', ge)):
            if m:
                ent.update({pref + '_valor': m['val'], pref + '_fila': m['fila'], pref + '_cat': m['cat'],
                            pref + '_pregunta': m['preg'], pref + '_universo': m['univ'], pref + '_informe': m['titulo'],
                            pref + '_id_informe': m['idinf'], pref + '_link': m['link'], pref + '_dup': m['filas_dup'],
                            pref + '_secundaria': m['secundaria']})
        if 'gap' in e:
            ent['gap'] = e['gap']
        audit.append(ent)
    pares = [dict(cons=e['cons'], panel=e['panel'], mes=e['mes'], campo_ini=e['ci'], campo_fin=e['cf'],
                  imagen=e['imagen']['val'], gestion=e['gestion']['val'], gap=e['gap'],
                  fila_img=e['imagen']['fila'], fila_ges=e['gestion']['fila'],
                  link=e['imagen']['link'] or e['gestion']['link'], nota=e['motivo'])
             for e in R['audit'] if e['estado'] == 'incluido']
    for p in pares:
        p['mes'] = f"{MESES[p['mes']]}-26"
    cambios = R['cambios']
    cons_con_par = sorted({p['cons'] for p in pares})
    resumen = {}
    for panel in ('fav', 'des'):
        ps = [p for p in pares if p['panel'] == panel]
        cs = [c for c in cambios if c['panel'] == panel]
        inc = [e for e in R['audit'] if e['panel'] == panel]
        resumen[panel] = dict(
            consultoras=len({p['cons'] for p in ps}), olas_pareadas=len(ps), cambios=len(cs),
            olas_con_alguna_medida=len(inc),
            incompletas=sum(1 for e in inc if e['estado'] == 'incompleto'),
            excluidas=sum(1 for e in inc if e['estado'] == 'excluido'),
            falta_gestion=sum(1 for e in inc if e['estado'] == 'incompleto' and e['imagen'] and not e['gestion']),
            falta_imagen=sum(1 for e in inc if e['estado'] == 'incompleto' and e['gestion'] and not e['imagen']),
            lectura=_lectura(panel, cs, ps))
    # desfavorable: qué dato falta para ampliar cobertura
    falt = defaultdict(list)
    for e in R['audit']:
        if e['panel'] == 'des' and e['estado'] == 'incompleto' and e['imagen'] and not e['gestion']:
            falt['desaprobación'].append(f"{e['cons']} {MESES[e['mes']]}-26")
    resumen['des']['dato_faltante_desaprobacion'] = sorted(falt['desaprobación'])
    return dict(consultoras=cons_con_par, pares=pares, cambios=cambios, cambios_excluidos=R['cambios_excl'],
                replicas=R['replicas'], auditoria=audit, resumen=resumen,
                reglas=['Ola = misma consultora, mismo mes enunciado y mismas fechas de campo; sin fecha de campo solo se agrupa dentro del mismo archivo fuente.',
                        'Par favorable = imagen positiva + aprobación; par desfavorable = imagen negativa + desaprobación; se evalúan por separado.',
                        'Se usa la desaprobación publicada; si no figura, el par queda incompleto (no se completa por diferencia).',
                        'Universo con redacción distinta entre ambas preguntas: el par se excluye hasta verificar en el informe.',
                        'Cambio = diferencia entre dos olas consecutivas de la misma consultora con par completo; si entre ellas hay una ola con alguna medida sin par, se excluye.',
                        'Brecha = gestión − imagen en puntos porcentuales (favorable: aprobación − positiva; desfavorable: desaprobación − negativa).'],
                fuente='data/bases/nivel2_extracto_pares.tsv')
