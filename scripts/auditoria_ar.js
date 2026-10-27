'use strict';
// Vista derivada. La edición aceptada se registra en docs/BITACORA_MONITOR_AR.md.
async function renderAuditoriaAR(){
  const box=document.getElementById('auditoriaAR');
  if(!box)return;
  try{
    const response=await fetch('./data/series_ar_auditoria.json');
    if(!response.ok)throw new Error(String(response.status));
    const d=await response.json();
    const safe=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const number=v=>typeof v==='number'?v.toLocaleString('es-AR',{maximumFractionDigits:3}):'—';
    const summary=d.resumen;
    box.innerHTML=`<div class="notice"><strong>Regla de entrada: tres meses consecutivos.</strong> Misma consultora, variable, categoría, población y unidad, con comparabilidad y publicación acreditadas. Un delta descriptivo no prueba significancia.</div>
      <div class="kpi-grid"><div class="kpi"><div class="kpi-label">Observaciones en maestro</div><div class="kpi-num">${number(summary.observaciones_maestro)}</div></div><div class="kpi"><div class="kpi-label">Series con tres períodos</div><div class="kpi-num">${summary.grupos_tres_periodos_consecutivos}</div></div><div class="kpi"><div class="kpi-label">Habilitadas por publicación</div><div class="kpi-num">${summary.grupos_habilitados_publicacion}</div></div></div>
      <p class="source">Corte: 26/10/2026. Las tres series habilitadas son IPCBA. Hay otras 62 candidatas pendientes de publicación y cinco de comparabilidad. El cotejo exhaustivo de todos los informes sigue abierto.</p>
      <div class="audit-controls"><label>Vista <select id="auditMode"><option value="approved">Publicación acreditada</option><option value="candidate">Candidatas · revisión</option></select></label><label>Consultora <select id="auditConsult"><option value="">Todas</option></select></label><label>Variable <select id="auditVar"><option value="">Todas</option></select></label></div>
      <p id="auditExplanation" class="notice"></p><p id="auditCount" class="source" aria-live="polite"></p>
      <div class="table-wrap" tabindex="0" aria-label="Tabla de series y fuentes"><table><thead><tr><th>Consultora · variable</th><th>Categoría · población</th><th>Publicación</th><th>Período del dato</th><th>Valor</th><th>Delta</th><th>Unidad delta</th><th>Fuente</th><th>Estado</th></tr></thead><tbody id="auditRows"></tbody></table></div>
      <p class="source"><a href="./docs/METODOLOGIA_SERIES_AR.md">Regla metodológica</a> · <a href="./docs/BITACORA_MONITOR_AR.md">Bitácora</a> · <a href="./data/series_ar_auditoria.json">Dataset de esta vista</a></p>`;
    const mode=document.getElementById('auditMode'),consult=document.getElementById('auditConsult'),variable=document.getElementById('auditVar');
    function fill(select,values){const before=select.value;select.innerHTML='<option value="">Todas</option>'+[...new Set(values)].sort().map(v=>`<option value="${safe(v)}">${safe(v)}</option>`).join('');select.value=[...select.options].some(o=>o.value===before)?before:'';}
    function render(reset=false){
      const candidate=mode.value==='candidate';
      const source=candidate?d.tabla_candidatas:d.tabla_publicacion_habilitada;
      if(reset){consult.value='';variable.value='';}
      fill(consult,source.map(r=>r.consultora));
      fill(variable,source.filter(r=>!consult.value||r.consultora===consult.value).map(r=>r.variable));
      const rows=source.filter(r=>(!consult.value||r.consultora===consult.value)&&(!variable.value||r.variable===variable.value));
      document.getElementById('auditExplanation').textContent=candidate?'REVISIÓN: tres períodos registrados no prueban tres publicaciones mensuales. El delta de esta vista compara períodos del dato; no habilita una curva pública.':'Vista habilitada: tres publicaciones consecutivas acreditadas. El delta compara publicaciones contiguas y mantiene visible el período al que corresponde cada cifra.';
      document.getElementById('auditCount').textContent=`${rows.length} registros mostrados. No se incluyen grupos con menos de tres períodos consecutivos.`;
      document.getElementById('auditRows').innerHTML=rows.map(r=>{
        const delta=candidate?r.delta_periodo:r.delta;
        const url=new URL(r.url,location.href);const locationLabel=typeof r.pagina==='number'?'p. '+r.pagina:'página pendiente';const link=url.protocol==='https:'?`<a href="${safe(url.href)}" target="_blank" rel="noopener noreferrer">Informe · ${safe(locationLabel)}</a>`:'Fuente pendiente';
        return `<tr><td>${safe(r.consultora)}<br><small>${safe(r.variable)}</small></td><td>${safe(r.categoria)}<br><small>${safe(r.poblacion)}</small></td><td>${safe(r.mes_publicacion||'Pendiente')}</td><td>${safe(r.mes_periodo||r.periodo_dato)}</td><td class="num">${number(r.valor)} ${safe(r.unidad)}</td><td class="num">${delta===null||delta===undefined?'—':(delta>0?'+':'')+number(delta)}</td><td>${safe(r.unidad_delta)}</td><td>${link}<br><small>${safe(r.observacion_id)}</small></td><td>${safe(candidate?r.estado:r.dictamen)}</td></tr>`;
      }).join('');
    }
    mode.addEventListener('change',()=>render(true));consult.addEventListener('change',()=>render());variable.addEventListener('change',()=>render());render();
  }catch(error){box.textContent='No se pudo cargar la auditoría. Reintentá recargando la página; no se completan valores faltantes.';console.error(error);}
}
