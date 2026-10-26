"""Extrae inflación publicada de INDEC/IDECBA; no estima cifras ni publica el monitor."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, re, time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import openpyxl

INDEC = 'https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv'
IDECBA = 'https://www.estadisticaciudad.gob.ar/eyc/banco-datos/ipcba-base-2021-100-evolucion-del-nivel-general-de-los-bienes-y-de-los-servicios-indices-y-variaciones-porcentuales-respecto-del-mes-anterior-ciudad-de-buenos-aires-febrero-de-2022-agosto-d/'
HOSTS = {'www.indec.gob.ar', 'indec.gob.ar', 'www.estadisticaciudad.gob.ar', 'estadisticaciudad.gob.ar'}

def allowed(url):
    p = urlparse(url)
    if p.scheme != 'https' or p.hostname not in HOSTS:
        raise ValueError('Origen no oficial: ' + url)

def download(url):
    allowed(url)
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'MonitorAR/1.0 (official statistics)'}), timeout=45) as r:
                allowed(r.url)
                data = r.read(20_000_001)
                if len(data) > 20_000_000:
                    raise ValueError('Archivo excede límite')
                return data, r.headers.get('Last-Modified')
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def number(value):
    if value is None or str(value).strip() in {'', 'NA', '///'}:
        return None
    n = float(str(value).strip().replace(',', '.'))
    if not math.isfinite(n):
        raise ValueError('Valor no finito')
    return n

def record(producer, period, level, monthly, locator, annual=None):
    date.fromisoformat(period + '-01')
    if level is None or level <= 0:
        raise ValueError('Índice inválido')
    return {'id': producer + '_IPC_' + period, 'productor': producer,
            'indicador': 'IPC_NACIONAL' if producer == 'INDEC' else 'IPCBA',
            'territorio': 'Argentina' if producer == 'INDEC' else 'CABA',
            'periodo_referencia': period, 'indice': level,
            'base': 'diciembre 2016=100' if producer == 'INDEC' else '2021=100',
            'variacion_mensual': monthly, 'variacion_interanual': annual,
            'variacion_acumulada': None, 'unidad_variaciones': '%',
            'origen_valores': 'publicados; no recalculados',
            'localizador': locator, 'fecha_publicacion': None,
            'estado_publicacion': 'Fecha exacta pendiente; consulta/Last-Modified no la sustituyen'}

def validate(rows):
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Observación duplicada')
    for producer in {r['productor'] for r in rows}:
        periods = sorted(r['periodo_referencia'] for r in rows if r['productor'] == producer)
        for a, b in zip(periods, periods[1:]):
            y, m = map(int, a.split('-'))
            expected = f'{y + (m == 12):04d}-{m % 12 + 1:02d}'
            if b != expected:
                raise ValueError('Hueco temporal ' + producer + ': ' + a + '/' + b)
    return rows

def parse_indec(data):
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = data.decode('latin-1')
    reader = csv.DictReader(io.StringIO(text), delimiter=';')
    required = {'Codigo', 'Descripcion', 'Periodo', 'Indice_IPC', 'v_m_IPC', 'v_i_a_IPC', 'Region'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('Cambió el esquema CSV INDEC')
    rows = []
    for line, r in enumerate(reader, 2):
        if r['Region'] != 'Nacional' or r['Codigo'] != '0':
            continue
        if r['Descripcion'].strip() != 'NIVEL GENERAL' or not re.fullmatch(r'\d{6}', r['Periodo']):
            raise ValueError('Cambió identificación de serie INDEC')
        p = r['Periodo'][:4] + '-' + r['Periodo'][4:]
        rows.append(record('INDEC', p, number(r['Indice_IPC']), number(r['v_m_IPC']),
                           f'CSV fila {line}; Region=Nacional; Codigo=0', number(r['v_i_a_IPC'])))
    if not rows:
        raise ValueError('Serie INDEC vacía')
    return validate(rows)

def parse_idecba(data):
    book = openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=True)
    if 'Evol_gral_bs_svcios' not in book.sheetnames:
        raise ValueError('Cambió hoja IDECBA')
    sheet = book['Evol_gral_bs_svcios']
    values = list(sheet.values)
    if 'base 2021 = 100' not in str(values[0][0]) or values[3][1] != 'Nivel General' or values[3][4] != 'Nivel General':
        raise ValueError('Cambió base o estructura IDECBA')
    rows = []
    for line, r in enumerate(values, 1):
        if isinstance(r[0], datetime):
            rows.append(record('IDECBA', r[0].strftime('%Y-%m'), number(r[1]), number(r[4]),
                               f'Evol_gral_bs_svcios!A{line}:E{line}'))
    book.close()
    if not rows:
        raise ValueError('Serie IDECBA vacía')
    return validate(rows)

def discover_idecba(html):
    links = re.findall(r'href=[\"\']([^\"\']+\.xlsx(?:\?[^\"\']*)?)[\"\']', html, re.I)
    links = sorted(set(urljoin(IDECBA, u) for u in links if 'Evol_gral_bs_svcios' in u))
    if len(links) != 1:
        raise ValueError('No hay enlace XLSX IDECBA inequívoco')
    allowed(links[0])
    return links[0]

def build(blobs, urls, since='2026-01', previous=None):
    date.fromisoformat(since + '-01')
    rows = parse_indec(blobs['INDEC']) + parse_idecba(blobs['IDECBA'])
    rows = sorted((r for r in rows if r['periodo_referencia'] >= since), key=lambda r: r['id'])
    for producer in ('INDEC', 'IDECBA'):
        if not any(r['productor'] == producer for r in rows):
            raise ValueError('No hay datos del recorte: ' + producer)
    old = {r['id']: r for r in (previous or {}).get('observaciones', [])}
    revised = []
    for r in rows:
        if r['id'] in old:
            changes = {k: {'antes': old[r['id']].get(k), 'ahora': r[k]} for k in
                       ('indice', 'variacion_mensual', 'variacion_interanual') if old[r['id']].get(k) != r[k]}
            if changes:
                revised.append({'id': r['id'], 'cambios': changes})
    if set(old) - {r['id'] for r in rows}:
        raise ValueError('La nueva descarga pierde observaciones previas')
    for r in rows:
        r['fuente_url'] = urls[r['productor']]
        r['fuente_sha256'] = hashlib.sha256(blobs[r['productor']]).hexdigest()
        r['estado_revision'] = 'Extraído automáticamente; pendiente de integración al maestro'
        r['publicable_monitor'] = False
    return {'schema_version': 1, 'consulta_utc': datetime.now(timezone.utc).isoformat(),
            'alcance': 'Nivel general; variación mensual publicada en ambas fuentes; interanual publicada solo INDEC. No calcular ni completar métricas ausentes.',
            'fuentes': {p: {'url': urls[p], 'sha256': hashlib.sha256(b).hexdigest()} for p, b in blobs.items()},
            'revisiones_detectadas': revised, 'observaciones': rows}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='artifacts/inflacion/inflacion_oficial.json')
    ap.add_argument('--since', default='2026-01')
    ap.add_argument('--fixture-dir', help='Usar indec.csv e ipcba.xlsx locales para pruebas sin red')
    ap.add_argument('--previous', help='JSON anterior para controlar revisiones/pérdidas')
    args = ap.parse_args()
    out = Path(args.output)
    urls = {'INDEC': INDEC, 'IDECBA': IDECBA}
    if args.fixture_dir:
        d = Path(args.fixture_dir)
        blobs = {'INDEC': (d/'indec.csv').read_bytes(), 'IDECBA': (d/'ipcba.xlsx').read_bytes()}
        urls['IDECBA'] = 'https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2026/08/IPCBA_base_2021100-Evol_gral_bs_svcios.xlsx'
    else:
        page, _ = download(IDECBA)
        urls['IDECBA'] = discover_idecba(page.decode('utf-8'))
        blobs = {p: download(u)[0] for p, u in urls.items()}
    previous = json.loads(Path(args.previous).read_text(encoding='utf-8')) if args.previous else None
    result = build(blobs, urls, args.since, previous)
    out.parent.mkdir(parents=True, exist_ok=True)
    for producer, b in blobs.items():
        ext = '.csv' if producer == 'INDEC' else '.xlsx'
        raw = out.parent/'fuentes'/producer/(hashlib.sha256(b).hexdigest()+ext)
        raw.parent.mkdir(parents=True, exist_ok=True)
        if not raw.exists():
            raw.write_bytes(b)
    temp = out.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temp.replace(out)
    print(json.dumps({'observaciones': len(result['observaciones']), 'revisiones': len(result['revisiones_detectadas']), 'output': str(out)}))

if __name__ == '__main__':
    main()

