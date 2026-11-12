# Actualización del Radar · oct–nov 2026 (corte parcial 11/11/2026)

## Qué cambió en el circuito

Antes, `index.html` traía los datos escritos dentro del script. Ahora los carga desde `data/radar_data.json`, que se genera así:

```
python3 scripts/build_radar_data.py          # regenera data/radar_data.json y data/radar_trazabilidad.csv
python3 scripts/build_radar_data.py --check  # falla si el JSON no coincide con las bases
python3 -m unittest discover -s tests -p 'test_radar_data.py'
```

Entradas:

- `data/bases/nivel2_extracto_radar.tsv`: filas de `nivel2_indicadores` que usa el Radar, con número de fila de Sheets, file_id y estado (ok / duplicado / superada / secundaria). Solo las filas `ok` pueden alimentar una celda.
- `data/bases/base_maestra_extracto_oct_nov.tsv` y `base_maestra_resultados_clave.tsv`: filas de `base_maestra_2026` (registro SL y valores citados en resultados_clave).
- `data/bases/radar_historico_publicado_b43fcb8.json`: series ya publicadas hasta b43fcb8. No se regeneran; las celdas que cubren las bases las reemplazan.
- `data/radar_mapping.json`: qué fila alimenta cada celda. No contiene valores.

Salida: `data/radar_trazabilidad.csv` tiene una fila por valor nuevo, corregido, retirado o puntual, con su fila, file_id y nota.

Para la próxima corrida: actualizar los extractos de `data/bases/` con las filas nuevas de los Sheets, agregar las asignaciones en `radar_mapping.json` y regenerar. No editar valores en el HTML.

## Publicación

`pages.yml` ahora copia `data/radar_data.json` al sitio y corre `build_radar_data.py --check` y sus tests. Sin esa copia, el sitio publicado queda sin datos.

`monitor_leg_build.py --check` ya fallaba en b43fcb8 (anterior a este cambio). El paso «Comprobar contenido antes de publicar» va a fallar hasta regenerar `monitor_leg.html`.

## Decisiones y alertas de esta corrida

- ICG octubre: se usa solo la fila 1086. Las filas 1219–1224 (duplicado) y la 1324 (cita de Infomedia) quedan anotadas en la base y no se contabilizan.
- ICC octubre: respaldado con el PDF CIF «2026-10 ICC Informe» (1uD_RKIA3E5i3Hm0WU6347wZ_A_rGrkEg); N1 fila 369, N2 filas 1345–1350.
- QMonitor noviembre: totales leídos de los gráficos del PDF (pp. 13, 25, 42, 59), N2 filas 1351–1363; mes noviembre según el informe (campo 8–26 oct).
- IPC Nación: octubre está pendiente (INDEC publica el 12/11). Septiembre 1,9% se mantiene como histórico publicado, sin fila en nivel 2.
- Isasi-Burdman agosto: se restablece la corrección del 26/10 (42 aprueba / 48 desaprueba), que estaba invertida en el index.html publicado.
- Fechas: se aplica siempre la fecha indicada por el informe de la consultora (criterio confirmado el 11/11). Synopsis, Equipo Mide y M&F quedan en octubre, como en la base.
- base_maestra tiene file_ids registrados dos veces (1_0CncF…, 1hyu3UO5…, 1E0rcIk…, 11hGDB…, 1o_mlbWD…). En el Radar no se contaron dos veces.

## Segunda corrida — fuentes secundarias (2026-11-11)

Fuentes consultadas: monitorargy.com, encuestas-argentinas.com, neetipol.com/mileienx, argelecciones.netlify.app/radar-electoral. Antes de usar una fuente secundaria se agotó Drive (Parte XVI.1).

| Hueco | Resultado | Base |
|---|---|---|
| IPC Nación sep-26 (había 1,9 publicado sin fila N2) | Cargado desde monitorargy (INDEC, publicado 14/10). No hay PDF en Drive: el último es ipc_09_26 (cubre agosto). Control: agosto 1,7 en el sitio = fila 1044. Evidencia MEDIA. | N2 fila 1365 · N1 fila 370 |
| Imagen negativa Milei DC Consultores oct-26 | Encontrada en la fuente primaria (lámina 12, pág. 19, relevada visualmente): 55,1%. No hizo falta la fuente secundaria; encuestas-argentinas coincide y quedó solo como control. | N2 fila 1364 · corrección anotada en N2 fila 1337 |
| DC intención «PJ 25,6» (encuestas-argentinas) | No se carga: es la suma de Peronismo 17,1 + Kirchnerismo 8,5 del original. La base respeta las categorías originales. | — |
| Synopsis, ola 12–17/10 (Peronismo 35 / LLA 33,6) | Candidato pendiente: sin informe en Drive ni enlace al original. No reemplaza la ola 8–15/9 (N2 1208). | pendiente en mapping |
| IPC Nación oct-26 | Sigue pendiente: monitorargy solo muestra la expectativa REM (1,8), que no es IPC. INDEC publica el 12/11. | — |

neetipol.com/mileienx: archivo de posteos de la cuenta @JMilei con clasificación de tono propio (datos hasta el 21/10/2026). Es contexto: no mide menciones ni sentimiento de terceros y no es comparable con Reputación Digital, Ad Hoc ni Monitor Digital. No se carga en SL.

argelecciones.netlify.app/radar-electoral: agregador automático de titulares de medios (620 ítems al 11/11, 18:17). No publica cifras propias; sus encuestas son notas de prensa que hay que chequear contra la fuente primaria. Útil solo para localizar estudios.

Por indicación de Ivanna (11/11), los valores de fuente secundaria se integran en la sección que completan, sin bloque aparte (se aparta de la Parte XVI.12). Cada uno lleva el rótulo completo y el tope de evidencia MEDIA en tres lugares: la lista de novedades del mes (etiqueta «serie · fuente secundaria»), la nota de fuente del gráfico o KPI y el tooltip de la barra, que además lleva borde naranja. `build_radar_data.py` falla si una fila con file_id «No aplica (fuente secundaria)» llega sin rótulo.

## Tercera corrida — encabezado, series de evolución, inflación y UTDT (2026-11-11)

- **Noviembre sin caja de novedades.** La vista de noviembre ya no muestra la apertura; octubre y septiembre la conservan.
- **Pendientes de publicación en el encabezado.** La franja superior se genera desde `radar_data.json` con el formato del original: últimos publicados (IPC, IPCBA, ICC, ICG, IPIM) y próximos (IPC oct 12/11 16:00 y nov 15/12 16:00, calendario oficial INDEC; ICC e ICG nov ~17/11, fecha estimada; IPCBA nov ~dic). Fechas tomadas del MCP de monitorargy (herramienta `calendario`).
- **Puntuales integrados en series.** `radar_mapping.json` reemplaza `puntuales` por `evolucion`: cada medición queda en la serie de su consultora e indicador, con todos los meses disponibles en la base, Δ y evidencia (ALTA ≥3, MEDIA 2, BAJA 1 o comparabilidad limitada). Series con más de un corte: QMonitor economía del país, voto e imagen de CFK, Bullrich y Kicillof (oct–nov); ICC subíndices (oct-25, jul–oct-26). En voto se suman las líneas QMonitor, Analogías, ESPOP y DC Consultores al gráfico por consultora.
- **Inflación.** IPC Nación oct-26 sin dato: INDEC lo publica el 12/11 16:00 y monitorargy tiene hasta sep-26. Interanual ene–abr-26 cargado de fuente primaria (informe INDEC abril 2026 en Drive, N2 1376–1379; monitorargy solo como control). Brecha acumulada IPCBA − IPC ene–abr calculada (Parte XIV.42). IPCBA interanual ene–abr sigue sin dato.
- **ICC regional y subíndices.** Cargados jul–ago (filas N2 824–835 ya existentes) y sep-26 y oct-25 desde las columnas comparativas del informe ICC de octubre (N2 1366–1375, fuente primaria).
- **Alerta:** el KPI «Regulados 2,8%» de sep-26 viene del Radar publicado sin fila en la base; monitorargy (INDEC) informa 2,34%. Queda marcado ⚠ hasta verificar con el informe INDEC de septiembre.

## Regla de presentación (2026-11-11, indicada por Ivanna)

Cada sección abre con KPIs y gráficos, como el Monitor AR publicado. Lo que no entra en un gráfico va al final de la sección, plegado en «Detalle por fuente y trazabilidad». Las series de evolución con 2 o más cortes se dibujan como líneas, una por consultora e indicador; la línea es punteada si la comparabilidad es baja. Si una sección solo tiene mediciones únicas, se dibuja un gráfico de barras del último corte, con 3 o más valores de la misma unidad. Noviembre, por ser un corte parcial, se resume en una línea dentro de ese bloque final.

## Cuarta corrida (2026-11-11)

- Se quitó la barra de mes. El bloque plegado del final muestra el resumen de noviembre y, si tienen filas, las novedades de octubre y septiembre.
- **Agenda pública.** Se agregó el gráfico de octubre por consultora (Proyección y CELAG) debajo del ranking de septiembre. «Inflación como problema» se extiende a may–oct: suma D'Alessio (septiembre, N2 1169) y Proyección (octubre, N2 1135), cada una con una medición.
- **Conversación digital.** El único informe SL con tono sobre Milei que cubre octubre es el de Reputación Digital «¿Se le acabó el aura?» (5/9–4/11, rotulado noviembre). Se cargaron sus tramos (N2 1380–1383, % negativo entre cuentas reales: 63 / 60 / 68 / 74) y se grafican en «Tono entre cuentas reales · sep–oct». No hay medición mensual de ISN de octubre en Drive. Los otros informes SL de octubre son temáticos (Bullrich, Messi, Maradona, minería, audiencias PDM, apuestas) y ya cuentan en «Informes SL por mes».

## Quinta corrida (2026-11-11)

- **Registro de informes SL por consultora.** Las variantes de nombre se unifican. Hay un gráfico de barras apiladas (consultora × mes) y una lista plegable por consultora con hipervínculo a cada informe en Drive. Reputación Digital y AD HOC enlazan además a sus gráficos dentro de la sección. 35 de 40 informes tienen vínculo: los file_id salen de base_maestra (capa SL, verificados contra la columna I el 11/11), y cuatro se ubicaron por título en Drive. Sin vínculo: «Milei 2027 (PBA)» y «Escucha social sobre video de Milei», porque no tienen fila propia en la base.
- **Estudios puntuales RD jul–nov.** Se suman «¿Bullrich candidata a vice?» (oct, N2 1080–1081) y «¿Se le acabó el aura?» (sep–nov, N2 1293, 1294, 1296 y 1299).
- **Títulos con período.** Los de Imagen, Gestión y Voto se calculan desde las series cargadas. Se actualizaron los de SL y Agenda, y se aclaran los meses sin informe: AD HOC octubre, ISN mensual octubre, IPC octubre.

## IPC Nación octubre 2026 (2026-11-12)

INDEC publicó el 12/11. El PDF no está en Drive. Se registró en N1 (fila 371) con enlace al informe en línea.
- Mensual 2,2%: fuente primaria en línea (página oficial de INDEC y resumen ejecutivo del informe). N2 1384.
- Interanual 33,1, núcleo 1,5 y regulados 2,9: fuente secundaria monitorargy (MCP, serie INDEC), con control visual en el resumen del informe. Acumulado ene–oct 26,3: calculado sobre el nivel general INDEC (12785,93 / 10121,37 − 1). N2 1385–1388. Evidencia MEDIA.
- Derivados: brecha IPCBA − IPC oct −0,3 p.p.; brecha acumulada −0,2 p.p.
- Se quitó «IPC oct» de próximos; queda IPC nov el 15/12.
- Pendiente: subir el PDF a Drive para pasar las cuatro filas secundarias a fuente primaria.

## Fuentes secundarias como nota metodológica (2026-11-12, indicado por Ivanna)

Los datos de fuente secundaria ya no se marcan dentro de gráficos, KPIs ni encabezado: no hay notas al pie de los gráficos ni texto en tooltips, y las barras y los bordes van sin distinción. Se listan en una nota metodológica general, plegada al pie de todas las pestañas y generada desde `NOTA_SECUNDARIA` en radar_data.json: indicador, mes, valor, rótulo completo y fila de N2. La trazabilidad por sección conserva la marca.

## Sexta corrida · 2026-11-12 (estructura por sección)

- **Nivel 2:** 1387 → 1394 filas con dato (+7 SL, filas de hoja 1389–1395: Sustantiva y Radar Público, visita de León XIV, nov-26; comparabilidad BAJA, NO COMPARABLE con encuestas). Nivel 1: 370 filas sin cambios (filas 362 y 364 pasan a ficha Parcial).
- **Imagen · Gestión:** la tabla consultora × variable se arma desde los datos y se agrupa en cuatro desplegables (imagen +/−, aprobación/desaprobación). Δ = última medición vs. la anterior de la misma consultora. Valores de Vozna que figuraban en el Radar publicado sin fila en la base quedan marcados con * (pendiente de cargar).
- **Conv. digital:** hay datos más recientes (nov-26, León XIV). La sección «Estudios puntuales · conversación digital · jul–nov 2026» pasa al inicio del tab, con las dos tarjetas nuevas primero.
- **Agenda pública:** se actualizan los KPI y el hallazgo con oct-26 (Proyección, CELAG). Nov-26: sin mediciones de agenda en la base al 12/11. Las tablas pasan a desplegables (oct-26, sep-26).
- **Tablas:** toda tabla estática queda en un desplegable (`details.det-tab`); el semáforo nacional abre por defecto.
- **GAP CONV–SL:** se retira intención de voto (voto LLA, escenario 2027), porque SL no mide voto. `GAP_STATUS` pasa a 8 indicadores (`gap_n_indicadores` en el mapping).
- **Cobertura:** se elimina el tab «Cobertura oct–nov». La cobertura se muestra por sección: una línea antes del detalle de cada tab y fuentes/pendientes dentro del desplegable.
- **Pendiente de registro (Modo Detección):** «PULSO SOCIAL – Municipalización de Crisis y Construcción de Legitimidad.pdf» (file_id 1gxt2w4KZpz-TUBZh1R__mncgAPDWRY_q, 12/11, 105 MB), aún sin fila en Nivel 1.

### Agregado 2026-11-12 · Pulso Social en Territorio
- Nivel 1: 370 → 372 filas con dato (fila 372, original de 105 MB, ficha Completa; fila 373, versión comprimida, registrada como duplicado). Lectura por OCR interno (spa) de la versión comprimida, 68 láminas.
- Capa TEM (cualitativo, 20 entrevistas). Excluido de Nivel 2: los porcentajes son de municipios anonimizados o citados de Proyección/PDM.
- Semáforo › Territorio: panel gráfico de contexto (cobertura, brecha responsabilidad–capacidad, cuatro modalidades, cinco trayectorias ilustrativas sin datos). No se cruza con encuestas.

### Agregado 2026-11-12 · Enlace a Monitor LEG y regeneración
- `index.html`: botón «Monitor LEG» en el encabezado (`href="./monitor_leg.html"`), con la tipografía, el color y el subrayado al pasar el cursor de las pestañas del sitio. En móvil la fecha del corte pasa debajo del logo para que entren el enlace y el botón de tema.
- `monitor_leg.html` regenerado con `python3 monitor_leg_build.py` desde `data/legislativo.json` + `monitor_leg.template.html` + `monitor_leg_view.py` (sin cambios en las fuentes). El HTML anterior no coincidía con el generador (el chequeo ya fallaba en b43fcb8).
- Chequeos: `monitor_leg_build.py --check` OK · `scripts/build_radar_data.py --check` OK · `unittest discover -s tests -p 'test_radar_data.py'` 6 tests OK.
