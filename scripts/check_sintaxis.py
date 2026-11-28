#!/usr/bin/env python3
"""Valida la sintaxis del JavaScript embebido en las páginas.

El problema que resuelve: el 18/11 rompí el JS de index.html dos veces editando
el archivo con scripts. Una vez quedó una variable huérfana al borrar un bloque,
y otra un corte mal hecho porque busqué el marcador de fin desde el principio
del archivo y encontró una coincidencia anterior. Las dos veces la página quedó
en blanco de la mitad para abajo y sólo se vio al abrirla en el navegador.

Un error de sintaxis no debería depender de que alguien lo note: corta la
corrida, como el resto de los chequeos.

Uso: python3 scripts/check_sintaxis.py
"""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PAGINAS = ['index.html', 'monitor_ar.html', 'monitor_leg.html', 'radar_eeuu_2026.html', 'espana_29n.html']


def main():
    if subprocess.run(['node', '--version'], capture_output=True).returncode != 0:
        print('node no está disponible: no se puede validar la sintaxis', file=sys.stderr)
        return 1

    fallas, bloques = [], 0
    for nombre in PAGINAS:
        p = RAIZ / nombre
        if not p.exists():
            continue
        html = p.read_text(encoding='utf-8')
        for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S):
            js = m.group(1)
            if not js.strip():
                continue
            bloques += 1
            linea = html[:m.start()].count('\n') + 1
            f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8')
            f.write(js)
            f.close()
            r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
            os.unlink(f.name)
            if r.returncode:
                fallas.append((nombre, linea, r.stderr.strip()))

    if fallas:
        print(f'{len(fallas)} bloque(s) de script con sintaxis inválida:\n', file=sys.stderr)
        for nombre, linea, err in fallas:
            print(f'  · {nombre}, script que empieza en la línea {linea}', file=sys.stderr)
            for l in err.splitlines()[:6]:
                print(f'      {l}', file=sys.stderr)
            print(file=sys.stderr)
        return 1

    print(f'sintaxis OK: {bloques} bloque(s) de script en {len(PAGINAS)} página(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
