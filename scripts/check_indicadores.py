#!/usr/bin/env python3
"""Impide que vuelva a fragmentarse una pregunta en varios id_indicador.

El problema que resuelve: VOTO_ESPACIO_LLA convive hoy con _PROYECCION,
_SYNOPSIS, _ESPOP, _EQUIPOMIDE y _DC. Seis IDs para una misma pregunta, cuando
la consultora ya es columna propia. La consecuencia no es estética: la serie no
se encadena, y cada consultora nueva que llega con su propio sufijo agrega un
pedazo más que nadie va a cruzar con los anteriores.

Regla: un ID tiene que estar en su forma canónica. El que no lo esté debe
figurar en data/diccionario_indicadores.json, bajo "pendientes_de_normalizar",
que es el backlog explícito de lo que ya estaba mal cuando se puso el control.
Un ID nuevo fuera de forma hace fallar la corrida.

Uso: python3 scripts/check_indicadores.py
"""
import csv
import io
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalizar_indicador import cargar, canonico, confirma  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EXTRACTO = RAIZ / 'data' / 'bases' / 'nivel2_extracto_radar.tsv'
DICC = RAIZ / 'data' / 'diccionario_indicadores.json'


def main():
    dicc = cargar()
    pendientes = set(dicc.get('pendientes_de_normalizar', []))

    filas, datos = {}, {}
    with io.open(EXTRACTO, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            i = r.get('id_indicador')
            if not i:
                continue
            filas.setdefault(i, set()).add(r.get('consultora', ''))
            clave = (r.get('consultora', ''), r.get('mes', ''), r.get('categoria_respuesta', ''))
            datos.setdefault(i, {}).setdefault(clave, set()).add((r.get('resultado', '') or '').strip())

    nuevos, resueltos, contradicen = [], [], []
    canon_de = {}
    cons = set(dicc['consultoras'])
    alias = dicc.get('alias_consultoras')
    for i in sorted(filas):
        c, quitado, _ = canonico(i, dicc, filas[i])
        canon_de[i] = c
        if c != i:
            (resueltos if i in pendientes else nuevos).append((i, c, quitado))
            continue
        # El sufijo parece consultora y la columna consultora no lo confirma: el ID
        # quedó igual sólo porque no se pudo verificar, no porque esté bien. Es una
        # contradicción entre el ID y los datos, y hay que resolverla en algún sentido.
        tok = i.split('_')[-1]
        if tok in cons and not confirma(tok, filas[i], alias) and i not in pendientes:
            contradicen.append((i, tok, sorted(filas[i])))

    familias = {}
    for i, c in canon_de.items():
        familias.setdefault(c, []).append(i)

    # Invariante: dos IDs que la normalización une tienen que ser la MISMA pregunta.
    # Prueba operativa, sin criterio humano de por medio: si los dos tienen filas de la
    # misma consultora, el mismo mes y la misma categoría con resultados distintos, son
    # dos series y unirlas las apila en una sola línea. Fue el caso de ICC_CIF con
    # ICC_CIF_CABA, _GBA e _INTERIOR: subíndices regionales del índice, no jurisdicciones.
    choques = []
    for c, ids in sorted(familias.items()):
        if len(ids) < 2:
            continue
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                x, y = ids[a], ids[b]
                for k in set(datos.get(x, {})) & set(datos.get(y, {})):
                    vx, vy = datos[x][k], datos[y][k]
                    if vx and vy and vx != vy:
                        choques.append((c, x, y, k, sorted(vx), sorted(vy)))
                        break
    if choques:
        print(f'{len(choques)} par(es) de id_indicador que la normalización uniría pero que '
              f'llevan datos distintos:\n', file=sys.stderr)
        for c, x, y, k, vx, vy in choques:
            cons, mes, cat = k
            print(f'  · {x}  vs  {y}', file=sys.stderr)
            print(f'    los dos quedarían como {c}', file=sys.stderr)
            print(f'    {cons} · {mes} · «{cat}»: {", ".join(vx)} contra {", ".join(vy)}',
                  file=sys.stderr)
            print(file=sys.stderr)
        print('Una pregunta medida una vez por una consultora en un mes tiene un valor por '
              'categoría, no dos: son series distintas y unirlas las apila en una línea.',
              file=sys.stderr)
        print('Si el sufijo que las distingue es parte de la pregunta (un subíndice regional '
              'del índice, por ejemplo) y no un dato de contexto, va a "excepciones" del '
              'diccionario, con el motivo.', file=sys.stderr)
        return 1

    if contradicen:
        print(f'{len(contradicen)} id_indicador cuyo sufijo de consultora no coincide con la '
              f'columna consultora de sus filas:\n', file=sys.stderr)
        for i, tok, cs in contradicen:
            print(f'  · {i}', file=sys.stderr)
            print(f'    sufijo «{tok}» · columna consultora: {", ".join(cs)}', file=sys.stderr)
        print('\nO el ID lleva la consultora equivocada, o la fila está mal atribuida, o falta '
              'el alias en "alias_consultoras". Las tres hay que mirarlas: ninguna se arregla sola.',
              file=sys.stderr)
        return 1

    if nuevos:
        print(f'{len(nuevos)} id_indicador fuera de forma canónica y sin registrar:\n', file=sys.stderr)
        for i, c, q in nuevos:
            hermanos = [o for o, cc in canon_de.items() if cc == c and o != i]
            print(f'  · {i}', file=sys.stderr)
            print(f'    canónico: {c}' + (f'   (sobra: {", ".join(q)})' if q else ''), file=sys.stderr)
            if hermanos:
                print(f'    fragmenta una pregunta que ya existe como: {", ".join(hermanos)}',
                      file=sys.stderr)
            print(file=sys.stderr)
        print('La consultora y la jurisdicción no van dentro del ID: ya son columnas de Nivel 2.',
              file=sys.stderr)
        print('Si el sufijo es parte de la pregunta y no un dato de contexto, agregalo a '
              '"excepciones" en el diccionario, con el motivo.', file=sys.stderr)
        return 1

    ya_bien = [i for i in pendientes if i in canon_de and canon_de[i] == i]
    if ya_bien:
        print(f'aviso: {len(ya_bien)} ID(s) del backlog ya están en forma canónica; '
              f'conviene sacarlos de "pendientes_de_normalizar": {", ".join(sorted(ya_bien)[:5])}')
    fuera = [i for i in pendientes if i not in canon_de]
    if fuera:
        print(f'aviso: {len(fuera)} ID(s) del backlog ya no están en el extracto; '
              f'conviene sacarlos del diccionario')

    frag = sum(1 for v in familias.values() if len(v) > 1)
    print(f'indicadores OK: {len(canon_de)} IDs · {len(familias)} preguntas · '
          f'{len(resueltos)} en el backlog de normalización · {frag} preguntas aún fragmentadas')
    return 0


if __name__ == '__main__':
    sys.exit(main())
