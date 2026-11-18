#!/usr/bin/env python3
"""Normalización de id_indicador: de la grafía escrita a la canónica.

Por qué: un ID nombra una pregunta. La consultora ya es columna propia de
Nivel 2, así que meterla adentro del ID parte la serie en tantos pedazos como
consultoras la midan. Hoy conviven VOTO_ESPACIO_LLA con _PROYECCION, _SYNOPSIS,
_ESPOP, _EQUIPOMIDE y _DC: seis IDs para una misma pregunta.

Qué hace, y qué NO hace:
  · Unifica grafías del mismo término (GESTION_NAC_ / GESTION_NACIONAL_,
    BALLOTAGE / BALOTAJE, IMG_CRISTINA_KIRCHNER / IMG_CFK).
  · Quita el sufijo de consultora, pero SOLO cuando la columna consultora de
    esas filas lo confirma. Sin confirmación no se toca: una coincidencia de
    nombre no alcanza para borrar parte de un identificador.
  · NO quita sufijos territoriales. Parecen redundantes con la columna
    jurisdiccion y a veces lo son, pero a veces distinguen preguntas distintas:
    ICC_CIF_CABA, _GBA e _INTERIOR son subíndices regionales del índice, no
    jurisdicciones, y colapsarlos destruiría tres series. Se listan aparte
    para resolverlos a mano contra el informe.

El ID original NUNCA se borra: esto produce una equivalencia, no un reemplazo.

Uso:
  python3 scripts/normalizar_indicador.py            → informe sobre el extracto
  python3 scripts/normalizar_indicador.py ID [ID…]   → canónico de cada uno
"""
import csv
import io
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DICC = RAIZ / 'data' / 'diccionario_indicadores.json'
EXTRACTO = RAIZ / 'data' / 'bases' / 'nivel2_extracto_radar.tsv'


def cargar():
    return json.loads(DICC.read_text(encoding='utf-8'))


def _clave(s):
    """Nombre de consultora a token comparable: sin tildes, sin paréntesis, sin espacios."""
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'\(.*?\)', ' ', s)
    return re.sub(r'[^A-Z]', '', s.upper())


def confirma(token, consultoras_fila, alias=None):
    """¿El sufijo del ID se corresponde con la consultora que firma esas filas?"""
    if not consultoras_fila:
        return False
    t = _clave((alias or {}).get(token, token))
    return all(t and (t in _clave(c) or _clave(c).startswith(t[:6])) for c in consultoras_fila)


def canonico(ident, dicc, consultoras_fila=None):
    """Devuelve (canónico, quitado, territorio_pendiente)."""
    if ident in set(dicc['excepciones']):
        return ident, [], None

    out = ident
    for viejo in sorted(dicc['sinonimos'], key=len, reverse=True):
        nuevo = dicc['sinonimos'][viejo]
        if out == viejo or out.startswith(viejo + '_'):
            out = nuevo + out[len(viejo):]
        elif ('_' + viejo + '_') in out:
            out = out.replace('_' + viejo + '_', '_' + nuevo + '_')
        elif out.endswith('_' + viejo):
            out = out[:-len(viejo)] + nuevo

    quitado, partes = [], out.split('_')
    cons = set(dicc['consultoras'])
    while len(partes) > 2 and partes[-1] in cons:
        if consultoras_fila is not None and not confirma(partes[-1], consultoras_fila, dicc.get('alias_consultoras')):
            break
        quitado.insert(0, partes.pop())

    terr = partes[-1] if partes[-1] in set(dicc['territorios']) and len(partes) > 2 else None
    return '_'.join(partes), quitado, terr


def main():
    dicc = cargar()
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            c, q, t = canonico(i, dicc)
            extra = f'   (fuera: {", ".join(q)})' if q else '   (sin cambios)'
            if t:
                extra += f'   [sufijo territorial «{t}» sin resolver]'
            print(f'{i}\n  → {c}{extra}')
        return 0

    filas = {}
    with io.open(EXTRACTO, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if r.get('id_indicador'):
                filas.setdefault(r['id_indicador'], set()).add(r.get('consultora', ''))

    grupos, territorio, sin_confirmar = {}, {}, []
    for i in sorted(filas):
        c, q, t = canonico(i, dicc, filas[i])
        grupos.setdefault(c, []).append(i)
        if t:
            territorio.setdefault(t, []).append(i)
        libre, _, _ = canonico(i, dicc)
        if libre != c:
            sin_confirmar.append((i, libre))

    colapsan = {c: v for c, v in grupos.items() if len(v) > 1}
    print(f'{len(filas)} id_indicador en el extracto → {len(grupos)} canónicos\n')
    print(f'{len(colapsan)} familias que se unifican:\n')
    for c, v in sorted(colapsan.items()):
        print(f'  {c}')
        for i in v:
            print(f'     ← {i}')
    cambian = sum(1 for i in filas if canonico(i, dicc, filas[i])[0] != i)
    print(f'\n{cambian} de {len(filas)} IDs cambian de grafía · '
          f'{len(filas) - len(grupos)} dejan de existir por duplicar la misma pregunta')

    if sin_confirmar:
        print(f'\nNO se tocaron {len(sin_confirmar)}: el sufijo parece consultora pero la '
              f'columna consultora no lo confirma')
        for i, l in sin_confirmar[:8]:
            print(f'  · {i} (habría quedado {l})')

    if territorio:
        n = sum(len(v) for v in territorio.values())
        print(f'\n{n} IDs con sufijo territorial, sin resolver automáticamente '
              f'(hay que mirar el informe: puede ser jurisdicción o parte de la pregunta):')
        for t, v in sorted(territorio.items(), key=lambda x: -len(x[1])):
            print(f'  _{t}: {len(v)} → {", ".join(v[:3])}{" …" if len(v) > 3 else ""}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
