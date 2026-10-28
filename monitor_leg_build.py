"""Generate Monitor LEG from reviewed records; --check fails on unpublished edits."""
import argparse
import hashlib
import json
from monitor_leg_view import render_monitor
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
            'www.letrap.com.ar': 'prensa', 'www.pagina12.com.ar': 'prensa',
            'acij.org.ar': 'actor',
            'po.org.ar': 'actor', 'guadalupetagliaferri.com.ar': 'actor',
            'www.xn--presupuestoporteo-uxb.com.ar': 'actor',
        }
        assert u.scheme == 'https' and (official or (u.hostname in attributed and attributed[u.hostname] == source.get('clase')))
        CalendarDate.fromisoformat(source['consultada'])
        assert source['consultada'] == d['corte']
    records = d['rondas'] + d['preguntas'] + d['temas'] + d['declaraciones'] + d['seguimiento'] + d['agenda'] + d['bloques'] + d['preguntas_bloques'] + d['panorama'] + d['novedades'] + d['controversias']
    assert len({r['id'] for r in records}) == len(records)
    for r in records:
        assert r['estado'] == 'verificado', r['id']
        assert r['fuentes'] and all(s in sources for s in r['fuentes']), r['id']
    for r in d['rondas']:
        assert 1 <= len(r['palabras_clave']) <= 4
        assert r['fuentes_debate'] and all(s in sources for s in r['fuentes_debate'])
        assert r['alcance_debate'] in ['En debate', 'Agenda al ' + CalendarDate.fromisoformat(d['corte']).strftime('%d/%m')]
    for r in d['preguntas_bloques']:
        assert r['filtro'] in {b['filtro'] for b in d['bloques']}
        assert r['clase'] in ['Pregunta', 'Reclamo'] and r['actor'].strip()
        assert r['fecha'] <= d['corte']
    body = render_monitor(d)
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
