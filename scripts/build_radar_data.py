"""Genera data/radar_data.json para el Radar (index.html) a partir de las bases.

Entradas (todas en el repositorio, sin red):
  data/bases/radar_historico_publicado_b43fcb8.json  series ya publicadas (extraídas del index.html de b43fcb8)
  data/bases/nivel2_extracto_radar.tsv                filas de nivel2_indicadores usadas por el Radar
  data/bases/base_maestra_extracto_oct_nov.tsv        filas de base_maestra_2026 (oct–nov)
  data/bases/base_maestra_resultados_clave.tsv        texto literal de resultados_clave (N1) usado como fuente
  data/radar_mapping.json                             qué fila alimenta cada celda (no contiene valores)

Salidas:
  data/radar_data.json         datos que consume index.html
  data/radar_trazabilidad.csv  una fila por valor nuevo, corregido o retirado

Uso: python3 scripts/build_radar_data.py [--check]
--check no escribe: falla si radar_data.json no coincide con lo que se generaría.
"""
from __future__ import annotations
import copy, csv, io, json, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASES = ROOT / 'data' / 'bases'
MESES = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
TAB_DE_MODULO = {
    'IPC Nación': 'indicadores', 'IPCBA CABA': 'indicadores', 'ICC': 'indicadores', 'ICG': 'indicadores',
    'Economía percibida': 'indicadores', 'Expectativas': 'indicadores', 'Clima / rumbo': 'indicadores',
    'Gestión nacional': 'imagen', 'Imagen Milei': 'imagen', 'Imagen otros dirigentes': 'imagen',
    'Intención de voto': 'voto', 'Agenda pública': 'agenda', 'Conversación digital': 'sl', 'Territorio': 'semaforo',
}
SL_TIPO = {'315': 'Evento puntual', '342': 'Evento puntual', '317': 'Audiencias (PDM)', '355': 'Audiencias (PDM)',
           '345': 'Monitoreo sectorial', '360': 'Escucha de búsquedas', '362': 'Pendiente de relevar', '364': 'Pendiente de relevar'}


class BuildError(Exception):
    pass


def tsv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def num(text):
    t = str(text).strip().replace(',', '.')
    try:
        return float(t) if '.' in t else int(t)
    except ValueError:
        raise BuildError(f'Valor no numérico en la base: {text!r}')


def etiqueta_mes(mes, anio=2026):
    return f'{MESES[int(mes)]}-{str(anio)[2:]}'


def mes_de_fecha(fecha):
    return etiqueta_mes(int(fecha[5:7]), int(fecha[:4]))


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()
    return ' '.join(s.replace('.', ' ').split())


def resolver(D, ruta, crear=None):
    """Devuelve (contenedor, clave) para una ruta tipo 'IMG.Zuban.pos' o 'CONS.Eq. Mide.lla'."""
    raiz, _, resto = ruta.partition('.')
    if not resto:
        return D, raiz
    grupo = D[raiz]
    if '.' in resto:
        nombre, campo = resto.rsplit('.', 1)
    else:
        nombre, campo = resto, None
    if campo is None:
        return grupo, nombre
    if nombre not in grupo:
        if crear is None:
            raise BuildError(f'Serie inexistente: {ruta}')
        grupo[nombre] = crear
    return grupo[nombre], campo


def construir():
    hist = json.loads((BASES / 'radar_historico_publicado_b43fcb8.json').read_text(encoding='utf-8'))
    cfg = json.loads((ROOT / 'data' / 'radar_mapping.json').read_text(encoding='utf-8'))
    n2 = {r['fila']: r for r in tsv(BASES / 'nivel2_extracto_radar.tsv')}
    n1 = {r['fila']: r for r in tsv(BASES / 'base_maestra_extracto_oct_nov.tsv')}
    rc = {r['fila']: r for r in tsv(BASES / 'base_maestra_resultados_clave.tsv')}
    D = copy.deepcopy(hist)
    traza = []
    # GAP CONV–SL sin intención de voto (SL no mide voto): se retiran 'voto LLA' y 'escenario 2027' (posiciones 9 y 10)
    D['GAP_STATUS'] = D['GAP_STATUS'][:cfg.get('gap_n_indicadores', len(D['GAP_STATUS']))]

    # 1. ejes nuevos (noviembre, corte parcial)
    for eje, spec in cfg['extender_ejes'].items():
        if spec['mes'] in D[eje]:
            continue
        D[eje].append(spec['mes'])
        for s in spec.get('series', []):
            D[s].append(None)
        for g in spec.get('grupos', []):
            for serie in D[g].values():
                for k, v in serie.items():
                    if isinstance(v, list):
                        v.append(None)

    # 2. series nuevas (consultoras que no estaban en el Radar publicado)
    for ruta, spec in cfg['nuevas_series'].items():
        raiz, nombre = ruta.split('.', 1)
        eje = {'IMG': 'MI', 'GESTION': 'MG', 'CONS': 'MV'}[raiz]
        if nombre not in D[raiz]:
            D[raiz][nombre] = {'color': spec['color'], **{c: [None] * len(D[eje]) for c in spec['campos']}}

    def poner(ruta, eje, mes, valor, origen):
        cont, campo = resolver(D, ruta)
        if mes not in D[eje]:
            raise BuildError(f'{ruta}: el mes {mes} no está en el eje {eje}')
        serie = cont[campo]
        i = D[eje].index(mes)
        if len(serie) != len(D[eje]):
            raise BuildError(f'{ruta}: largo {len(serie)} ≠ eje {eje} ({len(D[eje])})')
        anterior = serie[i]
        serie[i] = valor
        estado = 'sin cambio' if anterior == valor else ('nuevo' if anterior is None else ('retirado' if valor is None else 'corregido'))
        traza.append({'ruta': ruta, 'mes': mes, 'valor': valor, 'anterior': anterior, 'estado': estado, **origen})

    def secundaria(f, r, a):
        # Parte XVI: un dato de fuente secundaria debe llegar rotulado y nunca como ALTA
        if not r['archivo_fuente_file_id'].startswith('No aplica (fuente secundaria)'):
            return ''
        rot = a.get('rotulo', '')
        if not rot.startswith('FUENTE SECUNDARIA · '):
            raise BuildError(f'Fila N2 {f}: fuente secundaria sin rótulo en el mapping')
        return rot

    def valor_de(a):
        if 'fila' in a:
            f = str(a['fila'])
            if f not in n2:
                raise BuildError(f'Fila N2 {f} no está en el extracto')
            r = n2[f]
            if r['estado_fila'] != 'ok':
                raise BuildError(f'Fila N2 {f} marcada {r["estado_fila"]}: no puede alimentar el Radar')
            anio = 2025 if '_2025_' in r['id_informe'] else 2026
            mes = mes_de_fecha(r['fecha_campo_inicio']) if a.get('mes_por_campo') else etiqueta_mes(r['mes'], anio)
            if a.get('mes_por_campo') and r['fecha_campo_fin'] and mes_de_fecha(r['fecha_campo_fin']) != mes:
                raise BuildError(f'Fila {f}: campo cruza meses; no se puede asignar por campo')
            return num(r['resultado']), mes, {
                'base': 'nivel2_indicadores', 'fila': int(f), 'id_informe': r['id_informe'], 'id_indicador': r['id_indicador'],
                'consultora': r['consultora'], 'categoria': r['categoria_respuesta'], 'unidad': r['unidad'],
                'campo': f"{r['fecha_campo_inicio']}→{r['fecha_campo_fin']}".strip('→'),
                'file_id': r['archivo_fuente_file_id'], 'nota': a.get('nota', ''),
                'secundaria': secundaria(f, r, a)}
        f = str(a['fila_n1'])
        texto = rc[f]['resultados_clave']
        if a['texto'] not in texto or a['valor_texto'] not in a['texto']:
            raise BuildError(f'N1 fila {f}: «{a["texto"]}» no figura en resultados_clave')
        fila1 = n1.get(f, {})
        return num(a['valor_texto']), a['mes'], {
            'base': 'base_maestra_2026', 'fila': int(f), 'id_informe': '', 'id_indicador': 'resultados_clave',
            'consultora': rc[f]['consultora'], 'categoria': a['texto'], 'unidad': '%', 'campo': '',
            'file_id': fila1.get('file_id', ''), 'nota': a.get('nota', 'valor citado en resultados_clave de N1; sin fila N2')}

    # 3. asignaciones desde las bases
    for a in cfg['asignaciones']:
        v, mes, origen = valor_de(a)
        poner(a['ruta'], a['eje'], mes, v, {'modulo': a['modulo'], **origen})

    # 4. retiros (valores publicados sin fuente o reubicados)
    for r in cfg['retiros']:
        poner(r['ruta'], r['eje'], r['mes'], None, {'modulo': r['modulo'], 'base': '', 'fila': '', 'consultora': '', 'file_id': '', 'nota': r['motivo']})

    # 5. correcciones documentadas en el repositorio
    for c in cfg['correcciones_documentadas']:
        poner(c['ruta'], c['eje'], c['mes'], c['valor'], {'modulo': c['modulo'], 'base': 'corrección documentada', 'fila': '',
                                                         'consultora': 'Isasi-Burdman', 'file_id': '1Phw7mb5Dy9q7of8G-5wbfxUqy2lwxKgT',
                                                         'nota': c['motivo'] + ' Fuente: ' + c['fuente']})
    D['CROSS']['gestAprob']['label'] = 'Aprobación gestión (Isasi-Burdman) ↓'
    D['CROSS']['gestDesaprob']['label'] = 'Desaprobación gestión (Isasi-Burdman) →'

    # 6. derivados
    D['BRECHA'] = []
    for m in D['MBRECHA']:
        i = D['MINFL'].index(m)
        a, b = D['IPCBA_FULL'][i], D['IPC_FULL'][i]
        D['BRECHA'].append(None if a is None or b is None else round(a - b, 1))
    for i, m in enumerate(D['MIPCACUM']):
        a, b = D['IPCBA_ACUM_FULL'][i], D['IPC_ACUM'][i]
        if D['BRECHA_ACUM'][i] is None and a is not None and b is not None:
            D['BRECHA_ACUM'][i] = round(a - b, 1)
            traza.append({'ruta': 'BRECHA_ACUM', 'mes': m, 'valor': D['BRECHA_ACUM'][i], 'anterior': None, 'estado': 'nuevo',
                          'modulo': 'IPCBA CABA', 'base': 'derivado', 'fila': '', 'consultora': 'IDECBA / INDEC', 'file_id': '',
                          'nota': 'brecha calculada: IPCBA acumulado − IPC Nación acumulado (p.p.), Parte XIV.42'})
    publ = {r['name'].split(' (')[0]: r for r in hist['lastRows']}
    filas = []
    for nombre, s in D['CONS'].items():
        idx = [i for i, v in enumerate(s['lla']) if v is not None]
        if not idx:
            continue
        i = idx[-1]
        prev = s['lla'][idx[-2]] if len(idx) > 1 else None
        p = publ.get(nombre, {})
        filas.append({'name': p.get('name', nombre), 'p': D['MV'][i], 'lla': s['lla'][i], 'pj': s['pj'][i],
                      'd': None if prev is None else round(s['lla'][i] - prev, 1), 'n': p.get('n', '—'), 'met': p.get('met', '—')})
    D['lastRows'] = filas

    # Registro SL: oct–nov se regenera desde base_maestra (capa SL, sin duplicados)
    D['SL_INFORMES'] = [r for r in D['SL_INFORMES'] if r['mes'] not in ('Oct-26', 'Nov-26')]
    # vínculo de los informes ene–sep con su archivo en Drive (base_maestra, capa SL)
    import difflib
    reg = tsv(BASES / 'base_maestra_sl_registro.tsv')
    sr = cfg['sl_registro']
    usados = set(sr['forzar'].values())
    for it in D['SL_INFORMES']:
        if it['titulo'] in sr['forzar']:
            it['file_id'] = sr['forzar'][it['titulo']]
            continue
        if it['titulo'] in sr['sin_vinculo']:
            continue
        def sc(x):
            return difflib.SequenceMatcher(None, norm(it['titulo']), norm(x['informe_titulo'])).ratio()
        cands = [x for x in reg if etiqueta_mes(x['mes']) == it['mes'] and norm(it['consultora']).split()[0][:5] in norm(x['consultora'])
                 and x['file_id'] not in usados]
        best = max(cands, key=sc, default=None)
        if best and sc(best) + 0.5 >= 1.0:
            it['file_id'] = best['file_id']
            usados.add(best['file_id'])
    for f, r in sorted(n1.items(), key=lambda kv: int(kv[0])):
        if r['capa_analitica'] == 'SL' and r['mes'] in ('10', '11') and 'Duplicado' not in r['estado_ficha']:
            D['SL_INFORMES'].append({'mes': etiqueta_mes(r['mes']), 'consultora': r['consultora'].upper(), 'titulo': r['informe_titulo'],
                                     'tipo': SL_TIPO.get(f, 'Ad hoc temático'), 'fila_n1': int(f), 'file_id': r['file_id']})
    if 'Nov-26' not in D['MSL_MES']:
        D['MSL_MES'].append('Nov-26')
    D['SL_POR_MES'] = [sum(1 for r in D['SL_INFORMES'] if r['mes'] == m) for m in D['MSL_MES']]
    etiquetas = [l for l in D['SL_CONSULT_LABELS'] if l != 'Otros']
    claves = {l: norm(l) for l in etiquetas}
    vals = {l: 0 for l in etiquetas}
    otros = 0
    for r in D['SL_INFORMES']:
        c = norm(r['consultora'])
        hit = next((l for l, k in claves.items() if c == k), None)
        if hit:
            vals[hit] += 1
        else:
            otros += 1
    D['SL_CONSULT_VALS'] = [vals[l] for l in etiquetas] + [otros]
    D['SL_CONSULT_LABELS'] = etiquetas + ['Otros']

    # 7. novedades por pestaña y mes (puntuales + valores de serie nuevos/corregidos/retirados)
    UPD = {}
    def agregar(tab, mes, item):
        UPD.setdefault(tab, {}).setdefault(mes, []).append(item)
    for t in traza:
        if t['estado'] == 'sin cambio' and t['mes'] not in ('Oct-26', 'Nov-26') and not t.get('secundaria'):
            continue
        tab = TAB_DE_MODULO[t['modulo']]
        agregar(tab, t['mes'], {'tipo': 'serie', 'modulo': t['modulo'], 'etiqueta': t['ruta'].replace('.', ' · '), 'valor': t['valor'],
                                 'anterior': t['anterior'], 'estado': t['estado'], 'consultora': t.get('consultora', ''),
                                 'fila': t.get('fila', ''), 'base': t.get('base', ''), 'file_id': t.get('file_id', ''),
                                 'campo': t.get('campo', ''), 'unidad': t.get('unidad', ''), 'nota': t.get('nota', ''),
                                 'secundaria': t.get('secundaria', ''), 'categoria': t.get('categoria', '')})
    EVOL = {}
    orden_mes = lambda m: (int(m[4:]), [v for v in MESES.values()].index(m[:3]))
    for g in cfg['evolucion']:
        filas, meses = [], set()
        for fdef in g['filas']:
            celdas = {}
            for c in fdef['celdas']:
                v, mes, origen = valor_de(c)
                if mes in celdas:
                    raise BuildError(f'Evolución «{fdef["etiqueta"]}»: dos valores para {mes}')
                celdas[mes] = {'v': v, 'fila': origen['fila'], 'base': origen['base'], 'file_id': origen['file_id'],
                               'campo': origen.get('campo', ''), 'secundaria': origen.get('secundaria', ''), 'unidad': origen.get('unidad', '')}
                meses.add(mes)
                traza.append({'ruta': 'evolucion:' + fdef['etiqueta'], 'mes': mes, 'valor': v, 'anterior': None, 'estado': 'serie de evolución',
                              'modulo': g['modulo'], **origen})
            orden = sorted(celdas, key=orden_mes)
            delta = round(celdas[orden[-1]]['v'] - celdas[orden[-2]]['v'], 2) if len(orden) > 1 else None
            filas.append({'etiqueta': fdef['etiqueta'], 'consultora': fdef['consultora'], 'celdas': celdas, 'n': len(orden),
                          'delta': delta, 'evidencia': fdef.get('evidencia', 'ALTA' if len(orden) > 2 else 'MEDIA' if len(orden) == 2 else 'BAJA'),
                          'nota': fdef.get('nota', '')})
        EVOL.setdefault(g['tab'], []).append({'titulo': g['titulo'], 'modulo': g['modulo'], 'nota': g.get('nota', ''),
                                             'meses': sorted(meses, key=orden_mes), 'filas': filas})
    for p in cfg['pendientes']:
        agregar(TAB_DE_MODULO[p['modulo']], p['mes'], {'tipo': 'pendiente', 'modulo': p['modulo'], 'etiqueta': p['texto'], 'necesita': p['necesita']})

    # 8. cobertura sección × mes y tabla de control
    COB = []
    for sec in cfg['secciones_cobertura']:
        fila = {'seccion': sec}
        for mes in ('Oct-26', 'Nov-26'):
            datos = [t for t in traza if t['modulo'] == sec and t['mes'] == mes and t['valor'] is not None]
            fuentes = sorted({t['consultora'] for t in datos if t.get('consultora')})
            pend = [p for p in cfg['pendientes'] if p['modulo'] == sec and p['mes'] == mes] + \
                   [{'texto': f"{c['nombre']} {c['periodo']}: publicación prevista {c['fecha']} ({c['metodo']}).", 'necesita': '—'}
                    for c in cfg['calendario'] if c['modulo'] == sec and c['mes'] == mes]
            retir = [t for t in traza if t['modulo'] == sec and t['mes'] == mes and t['estado'] == 'retirado']
            estado = ('parcial' if pend or retir else 'con datos') if fuentes else ('pendiente' if pend or retir else 'sin dato')
            fila[mes] = {'estado': estado, 'n_fuentes': len(fuentes), 'fuentes': fuentes,
                         'filas': sorted({f"{t['base'][:2].upper()}:{t['fila']}" for t in datos if t.get('fila')}),
                         'pendiente': [p['texto'] + (' Necesita: ' + p['necesita'] if p['necesita'] != '—' else '') for p in pend] + [t['nota'] for t in retir]}
        bases = sorted({t['base'] for t in traza if t['modulo'] == sec and t.get('base') and t['mes'] in ('Oct-26', 'Nov-26')})
        fila['bases'] = bases
        COB.append(fila)

    # 9. KPIs ligados al HTML
    def ultimo(serie, eje):
        for i in range(len(serie) - 1, -1, -1):
            if serie[i] is not None:
                return serie[i], D[eje][i]
        return None, None
    icc, icc_m = ultimo(D['ICC'], 'MESI')
    icg, icg_m = ultimo(D['ICG'], 'MESI')
    i_icg = D['MESI'].index(icg_m)
    gest_oct = {n: s['aprob'][D['MG'].index('Oct-26')] for n, s in D['GESTION'].items() if s['aprob'][D['MG'].index('Oct-26')] is not None}
    rango = round(max(gest_oct.values()) - min(gest_oct.values()), 1) if len(gest_oct) > 1 else None
    D['KPI'] = {
        'ICC': {'valor': icc, 'mes': icc_m, 'oct_pendiente': D['ICC'][D['MESI'].index('Oct-26')] is None},
        'ICG': {'valor': icg, 'mes': icg_m, 'anterior': D['ICG'][i_icg - 1],
                'max12': max(v for v in D['ICG'][-13:] if v is not None), 'min12': min(v for v in D['ICG'][-13:] if v is not None)},
        'GESTION_OCT': {'n': len(gest_oct), 'min': min(gest_oct.values()), 'max': max(gest_oct.values()), 'rango': rango,
                        'semaforo': ('🔴' if rango and rango > 15 else '🟡' if rango and rango > 10 else '🟢'), 'por_consultora': gest_oct},
    }
    # valores de fuente secundaria (Parte XVI), para rotularlos en la sección que completan
    D['SECUNDARIA'] = [{'ruta': t['ruta'], 'mes': t['mes'], 'valor': t['valor'], 'fila': t['fila'], 'rotulo': t['secundaria'],
                        'modulo': t['modulo'], 'fuente_original': t.get('consultora', '')}
                       for t in traza if t.get('secundaria')]
    def ult(serie, eje):
        for i in range(len(D[serie]) - 1, -1, -1):
            if D[serie][i] is not None:
                return D[serie][i], D[eje][i]
        return None, None
    TL = []
    for t in cfg['encabezado_publicados']:
        if 'serie' in t:
            v, m = ult(t['serie'], t['eje'])
            sec = next((x['rotulo'] for x in D['SECUNDARIA'] if x['ruta'] == t['serie'] and x['mes'] == m), '')
            TL.append({**t, 'valor': v, 'periodo': m.lower(), 'secundaria': sec})
        else:
            TL.append(t)
    D['ENCABEZADO'] = {'publicados': TL, 'proximos': cfg['calendario']}
    D['EVOL'] = EVOL
    # SL: tono entre cuentas reales por tramo (Reputación Digital, informe sep–nov)
    D['SL_TRAMOS'] = []
    for t in cfg['sl_tramos']:
        r = n2[str(t['fila'])]
        D['SL_TRAMOS'].append({'tramo': t['etiqueta'], 'valor': num(r['resultado']), 'fila': t['fila'], 'file_id': r['archivo_fuente_file_id']})
        traza.append({'ruta': 'SL_TRAMOS', 'mes': t['etiqueta'], 'valor': num(r['resultado']), 'anterior': None, 'estado': 'nuevo', 'modulo': 'Conversación digital',
                      'base': 'nivel2_indicadores', 'fila': t['fila'], 'consultora': r['consultora'], 'file_id': r['archivo_fuente_file_id'], 'nota': 'tramo del informe sep–nov'})
    # SL: tarjetas de estudios puntuales con valores de la base
    D['SL_ESTUDIOS'] = []
    for c in cfg['sl_estudios']:
        mets = []
        for mt in c['metricas']:
            r = n2[str(mt['fila'])]
            v = num(r['resultado'])
            mets.append({**mt, 'valor': v})
            traza.append({'ruta': 'SL_ESTUDIOS.' + c['titulo'], 'mes': c['mes'], 'valor': v, 'anterior': None, 'estado': 'nuevo',
                          'modulo': 'Conversación digital', 'base': 'nivel2_indicadores', 'fila': mt['fila'], 'consultora': r['consultora'],
                          'file_id': r['archivo_fuente_file_id'], 'nota': mt['lbl']})
        D['SL_ESTUDIOS'].append({**c, 'metricas': mets})
    # Agenda: inflación como problema, puntos nuevos por consultora
    ai = cfg['agenda_inflacion']
    D['AGENDA_INFL'] = {'meses': ai['meses'], 'series': []}
    for sdef in ai['series']:
        data = [None] * len(ai['meses'])
        for c in sdef['celdas']:
            v, mes, origen = valor_de(c)
            data[ai['meses'].index(mes)] = v
            traza.append({'ruta': 'AGENDA_INFL.' + sdef['label'], 'mes': mes, 'valor': v, 'anterior': None, 'estado': 'nuevo', 'modulo': 'Agenda pública', **origen})
        D['AGENDA_INFL']['series'].append({'label': sdef['label'], 'color': sdef['color'], 'data': data, 'nota': sdef['nota']})
    # nota metodológica general: un renglón por dato de fuente secundaria (sin repetir ruta)
    ETQ = {'IPC': 'IPC Nación mensual', 'IPC_FULL': 'IPC Nación mensual', 'IPC_IA': 'IPC Nación interanual', 'IPC_IA_9': 'IPC Nación interanual',
           'IPC_ACUM': 'IPC Nación acumulado'}
    vistos, NS = set(), []
    for x in D['SECUNDARIA']:
        k = (x['fila'], x['mes'])
        if k in vistos:
            continue
        vistos.add(k)
        NS.append({'indicador': ETQ.get(x['ruta'], x['ruta']), 'mes': x['mes'], 'valor': x['valor'], 'fila': x['fila'], 'rotulo': x['rotulo']})
    for e in cfg['nota_secundaria_extra']:
        r = n2[str(e['fila'])]
        NS.append({'indicador': e['etiqueta'], 'mes': etiqueta_mes(r['mes']), 'valor': num(r['resultado']), 'fila': e['fila'], 'rotulo': e['rotulo']})
    D['NOTA_SECUNDARIA'] = NS
    D['UPD'] = UPD
    D['COBERTURA'] = COB
    D['META'] = {'corte': cfg['corte'], 'generado_por': 'scripts/build_radar_data.py',
                 'entradas': ['data/bases/radar_historico_publicado_b43fcb8.json', 'data/bases/nivel2_extracto_radar.tsv',
                              'data/bases/base_maestra_extracto_oct_nov.tsv', 'data/bases/base_maestra_resultados_clave.tsv', 'data/radar_mapping.json'],
                 'valores_trazados': len(traza),
                 'nuevos': sum(t['estado'] == 'nuevo' for t in traza), 'corregidos': sum(t['estado'] == 'corregido' for t in traza),
                 'retirados': sum(t['estado'] == 'retirado' for t in traza), 'puntuales': 0, 'en_series_de_evolucion': sum(t['estado'] == 'serie de evolución' for t in traza),
                 'fuente_secundaria': sorted({t['secundaria'] for t in traza if t.get('secundaria')})}
    return D, traza


def serializar(D, traza):
    js = json.dumps(D, ensure_ascii=False, indent=1) + '\n'
    out = io.StringIO()
    cols = ['modulo', 'ruta', 'mes', 'estado', 'valor', 'anterior', 'base', 'fila', 'id_informe', 'id_indicador', 'consultora', 'categoria', 'campo', 'file_id', 'nota', 'secundaria']
    w = csv.DictWriter(out, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    for t in traza:
        w.writerow({k: ('' if t.get(k) is None else t.get(k, '')) for k in cols})
    return js, out.getvalue()


def main():
    try:
        D, traza = construir()
    except BuildError as e:
        sys.exit('ERROR: ' + str(e))
    js, tr = serializar(D, traza)
    dst, dst_t = ROOT / 'data' / 'radar_data.json', ROOT / 'data' / 'radar_trazabilidad.csv'
    if '--check' in sys.argv:
        ok = dst.exists() and dst.read_text(encoding='utf-8') == js and dst_t.exists() and dst_t.read_text(encoding='utf-8') == tr
        sys.exit(0 if ok else 'radar_data.json desactualizado: correr python3 scripts/build_radar_data.py')
    dst.write_text(js, encoding='utf-8')
    dst_t.write_text(tr, encoding='utf-8')
    m = D['META']
    print(f"radar_data.json: {m['valores_trazados']} valores trazados · nuevos {m['nuevos']} · corregidos {m['corregidos']} · retirados {m['retirados']} · puntuales {m['puntuales']}")


if __name__ == '__main__':
    main()
