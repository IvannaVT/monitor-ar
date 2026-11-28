#!/usr/bin/env bash
# Construye el sitio público en _site/ después de validar el contenido.
#
# Lo invocan el workflow de GitHub Pages y el build de Netlify, de modo que
# ambas rutas publiquen exactamente los mismos archivos y detrás del mismo
# chequeo previo. PUBLICACION.md establece no usar rutas de publicación que
# omitan el chequeo; mientras las dos pasen por acá, esa condición se cumple
# por configuración y no por disciplina.
#
# Si se agrega una página pública o un archivo de datos que el sitio consuma,
# hay que sumarlo acá. Lo que no se copie a _site/ no se publica.

set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Chequeo previo ──"
python3 monitor_leg_build.py --check
python3 scripts/build_radar_data.py --check
python3 scripts/build_caba_data.py --check
python3 scripts/check_cifras.py
python3 scripts/check_indicadores.py
python3 scripts/check_sintaxis.py
python3 -m unittest discover -s tests -p 'test_radar_data.py'

echo "── Sitio público ──"
rm -rf _site
mkdir -p _site/data
cp index.html monitor_ar.html monitor_leg.html radar_eeuu_2026.html espana_29n.html 404.html _site/
cp data/indicadores.json data/radar_data.json data/caba_data.json data/espana_29n.json _site/data/

echo "_site/ generado con $(find _site -type f | wc -l) archivos"
