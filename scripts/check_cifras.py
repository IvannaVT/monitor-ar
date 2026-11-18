#!/usr/bin/env python3
"""Control de cifras escritas a mano en index.html.

El problema que resuelve: una cifra tipeada en el HTML no se recalcula cuando
cambia la base, y queda contradiciendo al dato sin que nada avise. Pasó cuatro
veces en la auditoría del 18/11 (Zentrix junio, Vozna, Zuban abr→sep, agenda).

Regla: toda cifra del HTML estático tiene que estar respaldada por un valor de
data/radar_data.json. La que no lo esté debe figurar en data/cifras_sin_respaldo.json
con su sección y su motivo. Una cifra nueva sin respaldo ni registro hace fallar
la corrida, que es el punto: el fallo es ruidoso en lugar de silencioso.

Uso: python3 scripts/check_cifras.py
"""
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTML = RAIZ / 'index.html'
DATOS = RAIZ / 'data' / 'radar_data.json'
REGISTRO = RAIZ / 'data' / 'cifras_sin_respaldo.json'

# cifras con unidad: lo que el lector lee como un dato de la base
CIFRA = re.compile(r'(?<![\d,.])(\d{1,3}(?:[,.]\d{1,2})?)\s*(%|p\.p\.|pp\b|puntos)')
# lo que no es un dato: escalas, años, fechas, tamaños de muestra
IGNORAR = {'0', '100'}


def valores_de(obj, acc):
    """Todo número que aparece en radar_data.json, a cualquier profundidad."""
    if isinstance(obj, dict):
        for v in obj.values():
            valores_de(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            valores_de(v, acc)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        acc.add(round(float(obj), 2))
        acc.add(round(abs(float(obj)), 2))
    elif isinstance(obj, str):
        # notas y lecturas ya resueltas por plantilla: sus cifras están respaldadas
        for m in CIFRA.finditer(obj):
            try:
                acc.add(round(float(m.group(1).replace(',', '.')), 2))
            except ValueError:
                pass
    return acc


def seccion_de(html, pos):
    """La pestaña en la que cae una posición del HTML."""
    titulos = [(m.start(), m.group(1)) for m in
               re.finditer(r'<section[^>]*id="tab-([a-z]+)"', html)]
    actual = '(encabezado)'
    for ini, nombre in titulos:
        if ini <= pos:
            actual = nombre
    return actual


def main():
    html = HTML.read_text(encoding='utf-8')
    datos = json.loads(DATOS.read_text(encoding='utf-8'))
    registro = json.loads(REGISTRO.read_text(encoding='utf-8')) if REGISTRO.exists() else {'permitidas': []}

    respaldadas = valores_de(datos, set())
    permitidas = {}
    for e in registro['permitidas']:
        permitidas.setdefault(round(float(str(e['valor']).replace(',', '.')), 2), []).append(e)

    # solo el HTML que el lector ve: fuera scripts y estilos
    visible = re.sub(r'<script.*?</script>', lambda m: ' ' * len(m.group(0)), html, flags=re.S)
    visible = re.sub(r'<style.*?</style>', lambda m: ' ' * len(m.group(0)), visible, flags=re.S)
    visible = re.sub(r'<!--.*?-->', lambda m: ' ' * len(m.group(0)), visible, flags=re.S)
    # lo atado a una plantilla ya se recalcula: su texto de respaldo no se audita
    visible = re.sub(r'<span data-cifra="[^"]*">.*?</span>',
                     lambda m: ' ' * len(m.group(0)), visible, flags=re.S)
    sin_tags = re.sub(r'<[^>]+>', lambda m: ' ' * len(m.group(0)), visible)

    huerfanas, usadas = [], set()
    for m in CIFRA.finditer(sin_tags):
        crudo = m.group(1)
        if crudo in IGNORAR:
            continue
        val = round(float(crudo.replace(',', '.')), 2)
        if val in respaldadas:
            continue
        if val in permitidas:
            usadas.add(val)
            continue
        ctx = re.sub(r'\s+', ' ', sin_tags[max(0, m.start() - 110):m.end() + 40]).strip()
        huerfanas.append((crudo, seccion_de(html, m.start()), ctx))

    obsoletas = [v for v in permitidas if v not in usadas]
    ahora_respaldadas = [v for v in permitidas if v in respaldadas]

    if huerfanas:
        print(f'{len(huerfanas)} cifra(s) del HTML sin respaldo en la base ni registro:\n', file=sys.stderr)
        for crudo, sec, ctx in huerfanas:
            print(f'  · {crudo} — pestaña «{sec}»\n    …{ctx}…\n', file=sys.stderr)
        print('Cada una necesita una de estas tres cosas:', file=sys.stderr)
        print('  1) salir de la base por plantilla, como el bloque de destacados;', file=sys.stderr)
        print('  2) cargarse como fila de Nivel 2 y entrar al extracto del radar;', file=sys.stderr)
        print(f'  3) registrarse en {REGISTRO.relative_to(RAIZ)} con su sección y el motivo.',
              file=sys.stderr)
        return 1

    if ahora_respaldadas:
        print(f'aviso: {len(ahora_respaldadas)} cifra(s) registradas ya tienen respaldo en la base '
              f'({", ".join(str(v) for v in sorted(ahora_respaldadas))}): conviene pasarlas a plantilla '
              f'y sacarlas del registro.')
    if obsoletas:
        print(f'aviso: {len(obsoletas)} cifra(s) del registro ya no están en el HTML '
              f'({", ".join(str(v) for v in sorted(obsoletas))}): conviene borrarlas del registro.')
    print(f'cifras OK: ninguna sin respaldo · {len(permitidas)} registradas con motivo')
    return 0


if __name__ == '__main__':
    sys.exit(main())
