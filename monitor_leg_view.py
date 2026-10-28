"""Render reviewed records using the visual structure of the supplied artifact."""
from html import escape as e


def render_monitor(d):
    sources = d['fuentes']
    date = '/'.join(reversed(d['corte'].split('-')))

    def refs(row):
        return ' · '.join(f'<a href="{e(sources[s]["url"], quote=True)}">{e(sources[s]["etiqueta"])}</a>' for s in row['fuentes'])

    def tile(title, text, color, evidence, extra=''):
        return f'<div class="mtile mtile-{color}"><div class="tl">{e(title)}</div>{text}{extra}<small class="sources">{refs(evidence)}</small></div>'

    def record_tile(row):
        extra = ''
        if 'palabras_clave' in row:
            words = ''.join(f'<span class="kw kw-yellow">{e(word)}</span>' for word in row['palabras_clave'])
            extra = f'<p class="debate"><strong>{e(row["alcance_debate"])}:</strong><br>{words}<small class="sources">{refs({"fuentes":row["fuentes_debate"]})}</small></p>'
        return tile(row['titulo'], e(row['texto']), row['tipo'], row, extra)

    def section(number, anchor, title, content):
        return f'<section id="{anchor}" aria-labelledby="{anchor}-titulo"><div class="section-heading"><h2 id="{anchor}-titulo">{e(title)}</h2><a class="back-top" href="#inicio">↑ Volver arriba</a></div>{content}<div class="section-end"><a class="back-top" href="#inicio">↑ Volver arriba</a></div></section>'

    def panel(anchor, title, content):
        return f'<dialog id="{anchor}" class="utility-panel" aria-labelledby="{anchor}-titulo"><div class="panel-heading"><h2 id="{anchor}-titulo">{e(title)}</h2><button type="button" class="panel-close" onclick="cerrarPanel(\'{anchor}\')">Cerrar ×</button></div><div class="panel-content">{content}</div><a class="back-top" href="#inicio" onclick="cerrarPanel(\'{anchor}\')">↑ Volver arriba</a></dialog>'

    def group(rows):
        return '<div class="mosaico">'+''.join(map(record_tile, rows))+'</div>'

    body = f'<header id="inicio" tabindex="-1"><div class="header-top"><div class="kicker">Presupuesto CABA 2027 · Seguimiento legislativo y de medios</div><div class="header-tools"><nav class="header-links" aria-label="Agenda y rondas ministeriales"><a href="#agenda" data-panel="agenda" aria-haspopup="dialog" aria-controls="agenda">Agenda</a><a href="#rondas" data-panel="rondas" aria-haspopup="dialog" aria-controls="rondas">Rondas ministeriales</a></nav><div class="theme-switch" role="group" aria-label="Apariencia"><button type="button" data-theme-choice="light" aria-pressed="false" onclick="setTheme(\'light\')">Claro</button><button type="button" data-theme-choice="dark" aria-pressed="true" onclick="setTheme(\'dark\')">Oscuro azul</button></div></div></div><h1>Monitor LEG | Presupuesto 2027 en medios</h1><p class="meta">Repercusión de las rondas presupuestarias de la Ciudad en medios locales y nacionales: temas destacados, controversias y planteos por bloque.</p><div class="meta">Corte de información: <span class="corte">⏱ {date} ART</span></div></header>'
    body += '<div class="aviso-top">Sesión ordinaria prevista: <strong>29/10</strong>. Los dictámenes no equivalen a sanción. Línea F: adjudicación anunciada para diciembre e inicio de obras previsto en 2027.</div>'
    nav = [('conclusion','Síntesis'),('controversiales','Debates'),('posiciones','Posiciones'),('seguimiento','Seguimiento')]
    body += '<nav class="nav-interna" aria-label="Secciones del monitor">'+''.join(f'<a href="#{anchor}">{e(label)}</a>' for anchor,label in nav)+'</nav>'

    conclusion = tile('Síntesis del debate · '+date, 'Impuestos, gasto público, vivienda, educación y seguridad concentran los planteos relevados. La cobertura reúne preguntas y posiciones atribuidas a sus fuentes.', 'red', d['panorama'][0])
    actors = ''
    for block, color in [('LLA','red'),('FxBA','blue'),('CD','green'),('FIT','purple')]:
        names = list(dict.fromkeys(name for r in d['preguntas_bloques'] if r['filtro']==block and r['actor']!='Bloque' for name in r['actor'].split(' / ')))
        actors += f'<p><strong class="actor-{color}">{block}:</strong> {e(" · ".join(names))}</p>'
    press = [key for key,s in sources.items() if s.get('clase')=='prensa']
    actor_sources = [key for key,s in sources.items() if s.get('clase')=='actor']
    coverage = '<strong>Cobertura periodística</strong><br>'+refs({'fuentes':press})+'<p class="debate"><strong>Publicaciones de actores</strong><br>'+refs({'fuentes':actor_sources})+'</p>'
    conclusion += '<div class="mosaico spaced">'+tile('Actores con planteos relevados', actors, 'grey', {'fuentes':['hacienda_prensa','tagliaferri','po_seguridad']})+tile('Medios y fuentes de seguimiento', coverage, 'grey', {'fuentes':['agenda']})+'</div>'
    conclusion += '<div class="mosaico-3 spaced panorama">'
    for row,color in zip(d['panorama'],['red','yellow','green']):
        conclusion += f'<details open class="mtile mtile-{color}"><summary class="tl">{e(row["titulo"])}</summary><p>{e(row["texto"])}</p><small class="sources">{refs(row)}</small></details>'
    conclusion += '</div>'
    conclusion += '<h3>Novedades y contexto</h3>'+group(d['novedades'])
    # Existing reviewed themes are displayed in the reference's paired panels.
    conclusion += '<div class="mosaico spaced">'+tile('Temas transversales', '<br>'.join(f'<strong>{e(r["titulo"])}</strong> — {e(r["texto"])}' for r in d['temas'][:2]),'blue',{'fuentes':['emergencia','bono']})+tile('Servicios e infraestructura', '<br>'.join(f'<strong>{e(r["titulo"])}</strong> — {e(r["texto"])}' for r in d['temas'][2:]),'purple',{'fuentes':['infra','educacion']})+'</div>'
    body += section(1,'conclusion','Síntesis',conclusion)

    controversies = ''
    for i,row in enumerate(d['controversias'],1):
        controversies += f'<article class="cont-item"><div class="cont-header"><span class="cont-num">C-{i:02}</span><h3 class="cont-titulo">{e(row["titulo"])}</h3></div><div class="cont-body">{e(row["texto"])}<small class="sources">{refs(row)}</small><a class="text-link" href="#posiciones">Ver preguntas y posiciones →</a></div></article>'
    controversies += '<p class="section-note">Selección de ejes documentados; no representa un ranking de impacto ni una medición de frecuencia de cobertura.</p>'
    controversies += '<h3 id="proyectos">Proyectos prioritarios</h3><div class="mosaico">'+''.join(tile(r['titulo'], e(r['texto']), 'green' if r['id']!='P-02' else 'yellow', r) for r in d['preguntas'])+'</div>'
    body += '<hr class="divider">'+section(3,'controversiales','Temas y controversias — Planteos relevados',controversies)

    questions = '<p class="section-note">Síntesis de intervenciones y posiciones públicas; no son citas textuales ni implican falta de respuesta.</p><div class="filtros" role="group" aria-label="Filtrar posiciones por bloque">'
    for key,label in [('todos','Todos'),('LLA','🔴 LLA'),('FxBA','🔵 FxBA'),('CD','🟢 CD'),('FIT','FIT/PO')]:
        active = ' class="activo" aria-pressed="true"' if key=='todos' else ' aria-pressed="false"'
        questions += f'<button type="button"{active} onclick="filtrar(\'{key}\',this)">{label}</button>'
    questions += '</div><div class="table-wrap"><table id="tabla-bloques"><thead><tr>'+''.join(f'<th scope="col">{x}</th>' for x in ['Bloque','Actor','Tema','Pregunta / reclamo','Fecha','Fuente'])+'</tr></thead><tbody>'
    for row in d['preguntas_bloques']:
        label = e(row['filtro'])
        if row['filtro'] in ['LLA','FxBA','CD']: label = f'<span class="badge-{row["filtro"].lower()}">{label}</span>'
        fecha = '/'.join(reversed(row['fecha'].split('-')[1:]))
        if row['fuentes']==['fxba']: fecha+=' · consulta'
        if row['fuentes']==['docentes_prensa']: fecha+=' · cobertura'
        values=[label,e(row['actor']),e(row['tema']),e(row['texto']),fecha,refs(row)]
        cells=''.join(f'<td data-label="{key}"><div>{value}</div></td>' for key,value in zip(['Bloque','Actor','Tema','Planteo','Fecha','Fuente'],values))
        questions+=f'<tr data-bloque="{e(row["filtro"])}">{cells}</tr>'
    questions+='</tbody></table></div>'
    body += '<hr class="divider">'+section(4,'posiciones','Posiciones por bloque — Preguntas y reclamos', '<div id="preguntas">'+questions+'</div>')

    following = ''
    for row in d['seguimiento']:
        following += f'<div class="pend-item pi-yellow"><span class="pend-ico" aria-hidden="true">◷</span><div class="pend-body"><strong>{e(row["titulo"])}</strong><span>{e(row["texto"])}</span><small class="sources">{refs(row)}</small></div></div>'
    following += '<div class="mosaico spaced">'+''.join(map(record_tile,d['declaraciones']))+'</div>'
    body += '<hr class="divider">'+section(5,'seguimiento','Seguimiento — Hitos y anuncios oficiales', following)

    agenda=''
    for row,day in zip(d['agenda'],['29/10','En curso','19/10','19/10']):
        agenda+=f'<div class="ag-item"><span class="ag-fecha">{day}</span><div class="ag-body"><strong>{e(row["titulo"])}</strong><span>{e(row["texto"])}</span><small class="sources">{refs(row)}</small></div></div>'
    banks = ' · '.join(f'<span title="{e(block["titulo"], quote=True)}">{e(block["filtro"])} <strong>{block["bancas"]}</strong></span>' for block in d['bloques'])
    body += f'<aside id="votos" class="banks-strip" tabindex="0" aria-label="Bancas por bloque. Desplazamiento horizontal en pantallas pequeñas."><p><strong>Bancas</strong> · {banks} · <strong>Total: 60</strong> · {refs(d["bloques"][0])} · <a class="back-top" href="#inicio">↑ Volver arriba</a></p></aside>'
    body += f'<footer>Monitor LEG · CABA · {date} ART · Fuentes oficiales, actores y prensa identificadas en cada registro.</footer>'
    body += panel('agenda','Agenda legislativa',agenda)
    body += panel('rondas','Rondas ministeriales y sesiones informativas',group(d['rondas']))
    return body
