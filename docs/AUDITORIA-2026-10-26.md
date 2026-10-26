# Monitor LEG: auditoría parcial al 26/10/2026 (ART)

> Registro histórico de la primera tanda. La preparación posterior para publicación reemplaza los antecedentes sin respaldo accesible por hechos cotejados, elimina menciones públicas de auditoría e implementa el generador y el workflow descritos en `../PUBLICACION.md`. Las observaciones siguientes conservan el diagnóstico previo y sus pendientes; no describen por sí solas la versión pública final.

## Alcance y publicación

Primera tanda para revisión; no certifica el resto del monitor. No mezclar automáticamente.
Base: `a2bddac2dca9c1ed0ed5ca098739260b0b06c0c4`. CSS y función de filtros conservados literalmente.
La lectura web de GitHub Pages falló durante la auditoría: se inspeccionó el archivo del commit desplegado, no se confirmó equivalencia byte a byte con la respuesta pública.

## Repositorio, historia y automatización

- Sitio estático: index.html, monitor_ar.html, monitor_leg.html; datos en data/indicadores.json y data/legislativo.json.
- `75d8a48` (22/10) separó los datos legislativos y agregó carga JSON. `ac1e6b1` volvió a reemplazar el monitor por HTML con contenido incluido. `a2bddac` agregó Salud y escenarios al HTML sin actualizar el JSON. Este último quedó desfasado al 20/10 y actualmente no se consume. No restaurarlo como fuente publicada: perdería contenido reciente.
- `56be751` introdujo LLA 13, FxBA 20, CD 7 y PRO 29: 69 bancas, incompatibles con el recinto de 60. `5bca98a` puso dictámenes 20/10; `15841b7` corrigió gran parte a 19/10, pero RP-14 quedó desactualizado.
- No hay archivos `.github/workflows` en el árbol actual ni historia para `.github`. Las ejecuciones consultadas corresponden al workflow administrado `pages build and deployment`, ruta `dynamic/pages/pages-build-deployment`; última ejecución `40332733327`, exitosa para el commit base. No se encontró validación editorial automatizada. El endpoint de catálogo de workflows fue rechazado por el conector; no se infiere de ello que no existan workflows administrados.
- README describe Netlify y un monitor.html inexistente. El despliegue observado es GitHub Pages; la conexión actual de Netlify no fue comprobada.
- Los dos scripts de base maestra trabajan sobre CSV externos, uno con ruta `/home/claude/monitor-ar/base_maestra_work.csv`; no abastecen Monitor LEG.
- Fuentes citadas por el HTML: transcripciones de Drive sin enlaces/documentos en el repositorio; SL_GA, prensa y dictámenes. No hay trazabilidad por afirmación. No se accedió a esas transcripciones ni se da por verificado su contenido.

## Correcciones comprobables

| Punto | Antes | Resultado / evidencia |
|---|---|---|
| Bancas | LLA 13; CD 7; PRO 29 | LLA 14; Confianza y Desarrollo 6; Vamos por más 12. FxBA 20 se conserva. La denominación PRO no representa el nombre oficial del bloque. Wolff preside la comisión, no el bloque. |
| Bereciartua | 14/10 | 13/10; exposición oficial de Movilidad e Infraestructura. |
| Miguel | 16/10 | 15/10; exposición de Educación. |
| Mraida | 19/10 | 16/10; exposición de Desarrollo Humano y Hábitat. |
| Quirós | 23/10 y cierre antes de dictámenes | 23/10 confirmado; se retira la certeza de cierre de toda la ronda. Es posterior al 19/10. |
| RP-14 | Dictaminado 20/10 | 19/10. Los expedientes 3082-J y 3085-J registran dictámenes de mayoría y despachos 753/2026 y 754/2026, respectivamente. |
| Línea F | Sin plazos / 3 estaciones en obra | Se distingue anuncio de cronograma de ejecución: adjudicación anunciada para diciembre de 2026 e inicio previsto en 2027. No se verificó acto de adjudicación ni acta de inicio. |
| Firmas y probabilidades | Firma cuádruple equiparada a alineamiento; probabilidades 60–70% / 30–40% | Firmas individuales y voto final quedan pendientes; porcentajes sin método se retiran. |

Composición oficial completa consultada: Ciudadanos Unidos/UCR 5; Confianza y Desarrollo 6; FIT/PO 2; Fuerza por Buenos Aires 20; LLA 14; Transformación 1; Vamos por más 12. Total 60. Es una fotografía de la consulta, no una reconstrucción histórica certificada. Los cuatro bloques resumidos en el diseño no representan el total.

El JSON histórico recibe correcciones básicas de bancas/fechas y una advertencia de que no es la fuente activa. Su contenido restante sigue pendiente: no usarlo para regenerar el sitio.

## Fuentes oficiales consultadas

- [Composición por bloques](https://www.legislatura.gob.ar/seccion/bloques.html) y [Vamos por más](https://www.legislatura.gob.ar/bloque/vamosporm%C3%A1s).
- [Bereciartua, 13/10](https://www.legislatura.gob.ar/posts/continuan-los-debates-en-torno-al-presupuesto-2027.html).
- [Miguel, 15/10](https://www.legislatura.gob.ar/posts/la-ministra-de-educacion-presento-los-ejes-principales-del-presupuesto-2027.html).
- [Mraida, 16/10](https://www.legislatura.gob.ar/posts/el-ministro-de-desarrollo-humano-y-habitat-gabriel-mraida-presento-el-presupuesto-2027.html).
- [Quirós, 23/10](https://www.legislatura.gob.ar/posts/quiros-presento-el-presupuesto-2027-de-salud-ante-la-comision-de-presupuesto.html).
- [Expediente 3085-J-2026](https://parlamentaria.legislatura.gob.ar/pages/expediente.aspx?id=142697) y [3082-J-2026](https://parlamentaria.legislatura.gob.ar/pages/expediente.aspx?id=142694): movimientos, dictámenes y despachos del 19/10.
- [Comisiones del 19/10 y sesión prevista del 29/10](https://www.legislatura.gob.ar/posts/reunion-conjunta-de-la-comisiones-de-desarrollo-economico-y-de-presupuesto4126.html). No acredita por sí solo convocatoria formal ni temario definitivo.
- [GCBA, anuncio Línea F](https://buenosaires.gob.ar/gcaba_historico/noticias/linea-f-dos-consorcios-de-empresas-nacionales-e-internacionales-se). La página tiene fecha 7/10 e inserta un mensaje del 2/10: no se usa para fijar un día exacto de apertura. Sí respalda estado de ofertas y cronograma anunciado.

## Pendientes antes de considerar auditado el conjunto

Obtener documentos oficiales de firmas/disidencias y texto final de los dictámenes. Cotejar duración, facultades, monto del bono, TAMAR, vencimiento y amortización. El registro del expediente prueba la existencia y fecha del dictamen, no todos esos detalles.

Cotejar las citas y pedidos individuales con video oficial y minuto o versión taquigráfica. La ausencia de una transcripción en el repositorio no prueba que no esté publicada. Verificar todas las menciones de falta de respuesta, disponibilidad de versiones y cierre de ronda; revisar Arengo 7/10 con registro oficial. No se corrigió arbitrariamente la fecha de una declaración individual para hacerla coincidir con una exposición.

Línea F: obtener pliegos/documento ambiental para explicar 9,8 frente a 10,9 km; no publicar el desglose de 1,1 km como hecho comprobado. Verificar contrato e inicio efectivo. Revisar también las cifras y citas de transporte conservadas como antecedentes, incluida FB-14.

Revisar cifras reales y sus deflactores, empleo, deuda, IVC, salud, subsidios, afirmaciones sobre personas, canales de amplificación y ausencia de actividad de PRO en X. Los escenarios y las etiquetas de riesgo son análisis previo sin validación independiente. El aviso del monitor explicita el alcance parcial; esta tanda no agrega nuevas certezas sobre esos temas.

## Circuito propuesto: GitHub como fuente única

1. Una issue por tanda, con fecha de corte y lista de afirmaciones por comprobar. Guardar cada evidencia como URL oficial, fecha del evento, fecha de publicación, fecha de consulta, extracto breve y ubicación (página/minuto).
2. En una segunda PR técnica, reconciliar primero todo el HTML actual con data/legislativo.json. Usar plantilla estable y generador determinista; mantener HTML estático generado para Pages. No restaurar el JSON viejo ni regenerar el diseño con IA. Validar equivalencia de contenido y aspecto antes de activar el circuito.
3. Claude recibe únicamente los registros modificados y extractos oficiales suficientes. Devuelve JSON con `id`, `campo`, `valor_anterior`, `valor_propuesto`, `fuentes`, `estado_verificacion` y `motivo`; nunca HTML, CSS, archivos enteros ni el historial del chat. Una llamada breve por tanda. No se requiere API paga ni se crean secretos en esta PR.
4. Validación determinista: JSON válido, IDs únicos, campos permitidos, fechas ISO, URL de evidencia, suma de bancas 60 y estados `verificado`, `atribuido`, `pendiente`. La etiqueta verificado requiere revisión humana de la evidencia; no basta la salida de Claude. Para publicar afirmaciones nuevas solo se admiten verificadas, o citas atribuidas con localización comprobada. Pendientes quedan en la issue.
5. GitHub Actions en PR ejecuta validación y generación en modo comprobación; comparar contenido y capturas en escritorio/móvil, probar filtros. Sin permisos de publicación ni acceso a secretos para la validación. Nunca usar una acción que deje a Claude reescribir la página o empujar a main.
6. Revisión de evidencia y aprobación de la PR. Merge explícito; Pages publica desde main. Verificar la ejecución y la página real tras el merge. Revertir el commit de merge si falla; historial y evidencia quedan en GitHub.

El circuito se diseña aquí; el generador y sus controles de CI aún no están implementados. Esta propuesta contiene la primera corrección editorial reversible, no activa publicación automática nueva.

## Entrega y acceso

Se preparó una rama `audit/monitor-leg-2026-10-26`. El conector de GitHub rechazó la escritura con HTTP 403 y Git local no pudo autenticarse. La sesión del navegador sí permitió crear la rama remota y cargar los cambios para una PR de revisión. Main y la publicación quedan sin modificar hasta una decisión explícita de merge.

## Validación de esta tanda

Comprobados: CSS y JavaScript idénticos a la base; mismos encabezados de sección, tablas, mosaicos y filas por bloque; JSON válido, IDs únicos y suma de composición completa igual a 60; ausencia de las bancas erróneas, RP-14 con 20/10, estaciones afirmadas en obra y probabilidades numéricas retiradas. `git diff --check` sin errores. No se realizó comparación de capturas ni prueba interactiva en navegador; queda pendiente para la revisión antes de mezclar.
