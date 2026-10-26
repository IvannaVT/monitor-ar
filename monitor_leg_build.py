"""Generate Monitor LEG from reviewed records; --check fails on unpublished edits."""
import argparse
import hashlib
import html
import json
from datetime import date as CalendarDate
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent

def build():
    d = json.loads((ROOT / 'data/legislativo.json').read_text(encoding='utf-8'))
    assert d['schema_version'] == 1
    assert d['revision']['estado'] == 'aprobado'
    assert d['revision']['fecha'] == d['corte']
    assert d['revision']['responsable'].strip()
    CalendarDate.fromisoformat(d['corte'])
    reviewed = {k:v for k,v in d.items() if k != 'revision'}
    digest = hashlib.sha256(json.dumps(reviewed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest == d['revision']['contenido_sha256'], 'El contenido cambió después de su revisión.'
    assert sum(x['bancas'] for x in d['bloques']) == 60
    assert len({x['id'] for x in d['bloques']}) == len(d['bloques'])
    sources = d['fuentes']
    for source in sources.values():
        u = urlparse(source['url'])
        official = u.hostname and u.hostname.endswith('.gob.ar')
        attributed = {
            'www.ambito.com': 'prensa', 'www.tiempoar.com.ar': 'prensa',
            'www.noticiasurbanas.com.ar': 'prensa',
            'po.org.ar': 'actor', 'guadalupetagliaferri.com.ar': 'actor',
            'www.xn--presupuestoporteo-uxb.com.ar': 'actor',
        }
        assert u.scheme == 'https' and (official or (u.hostname in attributed and attributed[u.hostname] == source.get('clase')))
        assert source['consultada'] == d['corte']
    records = d['rondas'] + d['preguntas'] + d['temas'] + d['declaraciones'] + d['seguimiento'] + d['agenda'] + d['bloques'] + d['preguntas_bloques']
    assert len({r['id'] for r in records}) == len(records)
    for r in records:
        assert r['estado'] == 'verificado', r['id']
        assert r['fuentes'] and all(s in sources for s in r['fuentes']), r['id']
    for r in d['rondas']:
        assert 1 <= len(r['palabras_clave']) <= 4
        assert r['fuentes_debate'] and all(s in sources for s in r['fuentes_debate'])
        assert r['alcance_debate'] in ['En debate', 'Agenda al 26/10']
    for r in d['preguntas_bloques']:
        assert r['filtro'] in {b['filtro'] for b in d['bloques']}
        assert r['clase'] in ['Pregunta', 'Reclamo'] and r['actor'].strip()
        assert r['fecha'] <= d['corte']
    e = html.escape
    def refs(r):
        return ' · '.join(f'<a href="{e(sources[s]["url"], quote=True)}">{e(sources[s]["etiqueta"])}</a>' for s in r['fuentes'])
    def tile(r):
        assert r['tipo'] in ['yellow', 'green', 'grey', 'blue', 'red']
        debate = ''
        if 'palabras_clave' in r:
            debate = f'<p><strong>{e(r["alcance_debate"])}:</strong> {e(" · ".join(r["palabras_clave"]))} <small>{refs({"fuentes": r["fuentes_debate"]})}</small></p>'
        return f'<div class="mtile mtile-{r["tipo"]}"><div class="tl">{e(r["titulo"])}</div>{e(r["texto"])} <small>{refs(r)}</small>{debate}</div>'
    def tiles(title, rows):
        return '<section><h2>'+e(title)+'</h2><div class="mosaico-tiles">'+''.join(map(tile, rows))+'</div></section>'
    date = '/'.join(reversed(d['corte'].split('-')))
    body = f'<header><div class="kicker">Comisión de Presupuesto · CABA</div><h1>Presupuesto 2027 — Monitor LEG</h1><div class="meta">Seguimiento legislativo &nbsp;|&nbsp; <span class="corte">⏱ {date} ART</span></div></header>'
    body += '<div class="aviso">Próxima sesión ordinaria prevista: 29/10. Los dictámenes de comisión no equivalen a sanción legislativa. El cronograma anunciado de Línea F prevé adjudicación en diciembre e inicio de obras en 2027.</div><hr class="divider">'
    body += tiles('Rondas ministeriales y sesiones informativas', d['rondas'])
    body += '<hr class="divider"><section><h2>Proyectos prioritarios</h2><div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Tema</th><th>Estado parlamentario</th><th>Est.</th></tr></thead><tbody>'
    for r in d['preguntas']:
        body += f'<tr><td>{e(r["id"])}</td><td>{e(r["titulo"])}</td><td>{e(r["texto"])} {refs(r)}</td><td>{e(r["simbolo"])}</td></tr>'
    body += '</tbody></table></div></section><hr class="divider"><section><h2>Preguntas y reclamos por bloque</h2><p style="font-size:.72rem;color:var(--muted)">Síntesis de intervenciones y posiciones públicas; no son citas textuales ni implican falta de respuesta.</p><div class="filtros">'
    for key, label in [('todos','Todos'),('LLA','🔴 LLA'),('FxBA','🔵 FxBA'),('CD','🟢 CD'),('FIT','FIT/PO')]:
        active = ' class="activo"' if key == 'todos' else ''
        body += f'<button{active} onclick="filtrar(\'{key}\',this)">{label}</button>'
    body += '</div><div style="overflow-x:auto"><table id="tabla-bloques"><thead><tr><th>Bloque</th><th>Actor</th><th>Tema</th><th>Pregunta / reclamo</th><th>Fecha</th><th>Fuente</th></tr></thead><tbody>'
    for r in d['preguntas_bloques']:
        badge = {'LLA':'lla','FxBA':'fxba','CD':'cd'}.get(r['filtro'])
        label = e(r['filtro'])
        if badge: label = f'<span class="badge-{badge}">{label}</span>'
        fecha = '/'.join(reversed(r['fecha'].split('-')[1:]))
        if r['fuentes'] == ['fxba']: fecha += ' · consulta'
        if r['fuentes'] == ['docentes_prensa']: fecha += ' · cobertura'
        body += f'<tr data-bloque="{e(r["filtro"])}"><td>{label}</td><td>{e(r["actor"])}</td><td>{e(r["tema"])}</td><td>{e(r["texto"])}</td><td>{fecha}</td><td>{refs(r)}</td></tr>'
    banks = ' · '.join(f'{e(r["filtro"])} {r["bancas"]}' for r in d['bloques'])
    body += f'</tbody></table></div><div style="font-size:.72rem;color:var(--muted)">Bancas: {banks}. Total: 60. {refs(d["bloques"][0])}. No determina el voto de cada proyecto.</div></section><hr class="divider"><div class="mosaico-par">'
    body += tiles('Temas transversales', d['temas']) + tiles('Anuncios y antecedentes oficiales', d['declaraciones'])
    body += '</div><hr class="divider"><div class="mosaico-par">'
    body += tiles('Puntos de seguimiento', d['seguimiento']) + tiles('Agenda legislativa', d['agenda'])
    body += f'</div><footer>Monitor LEG · CABA · {date} ART · Fuentes oficiales, actores y prensa identificadas en cada registro.</footer>'
    template = (ROOT / 'monitor_leg.template.html').read_text(encoding='utf-8')
    assert template.count('{{CONTENT}}') == 1
    css = template.split('<style>',1)[1].split('</style>',1)[0]
    assert hashlib.sha256(css.encode()).hexdigest() == d['revision']['css_sha256'], 'El diseño cambió: revisar y autorizar explícitamente.'
    result = template.replace('{{CONTENT}}',body)
    for term in ['auditoría','auditoria','sin verificar','pendiente de cotejo','prob.']:
        assert term not in result.lower(), term
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=build()
    path=ROOT/'monitor_leg.html'
    if args.check:
        assert path.read_text(encoding='utf-8')==result, 'Regenerar monitor_leg.html antes de publicar.'
        print('Chequeo previo OK: fuente estructurada, evidencia, revisión, 60 bancas, diseño y HTML sincronizado.')
    else:
        path.write_text(result,encoding='utf-8')
