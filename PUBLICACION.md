# Proceso previo a cada publicación de Monitor LEG

La adaptación del diseño exportado de Claude usa `monitor_leg_view.py` para la estructura y `monitor_leg.template.html` para estilos e interacciones. Ver `DISENO_CLAUDE.md` para el alcance visual y la corrección del mapa de bancas a siete bloques y 60 integrantes. No se importan predicciones de voto ni mediciones de impacto sin respaldo.

## Ajuste de lectura y móvil · 26/10/2026

Cambio de diseño autorizado por la usuaria: cuerpo de 16px, tarjetas de 1rem, fuentes enlazadas con mayor contraste, espaciado y foco visibles, botones de al menos 44px. A 640px o menos, mosaicos en una columna y tablas como fichas etiquetadas conservando filtros. Se actualiza solo la huella CSS; no cambia el contenido legislativo ni el corte de datos. Se mantiene «Repercusión» en la bajada. Comprobar 320, 390, 640, 768 y 1280px, ausencia de desborde y los filtros antes de cerrar la publicación.

La página pública es un monitor legislativo. No lleva rótulos de auditoría. El registro de comprobaciones y los pendientes permanecen en GitHub, fuera del artefacto público desplegado.

## Fuente única y roles

`data/legislativo.json` es la fuente de Monitor LEG. `monitor_leg.template.html` conserva el diseño. `monitor_leg_build.py` genera `monitor_leg.html` de forma determinista. No modificar manualmente el HTML generado.

Claude es opcional: recibe solo registros que cambian y extractos oficiales suficientes, y devuelve una propuesta JSON con ID, valor anterior, valor propuesto, URL, localización en la fuente y motivo. No regenerar HTML ni enviarle el repositorio o el historial completo. No se integra una API paga ni se crean secretos.

## Antes de cada actualización

1. Crear rama y PR. Revisar en fuentes oficiales cada afirmación nueva o modificada. Registrar fecha del evento y de consulta; distinguir anuncio, proyecto, dictamen, sanción, adjudicación e inicio efectivo. Revisar también si los registros mantenidos siguen vigentes al nuevo corte.
2. Publicar solo registros cotejados. Las citas requieren documento y página o video y minuto. Las cifras requieren período, unidad y contexto. No publicar probabilidades sin método ni inferir votos a partir de firmas de comisión. Retirar de la versión pública lo que no pueda sustentarse; conservar los antecedentes y pendientes en docs o en la PR.
3. Actualizar los datos, las fuentes y el corte. Después del cotejo, el responsable registra la revisión en `revision`, incluida la huella SHA-256 del contenido canónico (JSON sin `revision`, claves ordenadas, UTF-8, sin espacios entre separadores). La huella detecta cambios posteriores; no certifica la veracidad por sí misma.
4. Ejecutar `python monitor_leg_build.py` y `python monitor_leg_build.py --check`. Comparar la vista en escritorio y móvil, probar todos los filtros y revisar enlaces. Confirmar que el diseño no fue alterado.
5. Describir en la PR qué cambió y qué evidencia lo respalda. Revisar el diff y la comprobación de GitHub Actions. Mezclar únicamente después de esta revisión. El control automatizado no reemplaza el cotejo editorial humano.
6. GitHub Pages usa como origen GitHub Actions. El workflow `.github/workflows/pages.yml` vuelve a comprobar los archivos del commit de main y publica solo si pasa. El job de despliegue depende del job de chequeo; las PR no despliegan. Una edición de contenido sin nueva revisión o un HTML desactualizado bloquea la publicación de esa versión.
7. Tras el despliegue, comprobar ejecución, URL pública, fecha de corte y filtros. Si falla, revertir el commit de merge y comprobar de nuevo. No usar otra ruta de publicación que omita el chequeo.

El workflow publica únicamente index.html, monitor_ar.html, monitor_leg.html y data/indicadores.json. La documentación interna, la plantilla y el generador no se incorporan al sitio. El control específico implementado cubre Monitor LEG; no certifica los indicadores de Monitor AR.

## Versión del 26/10/2026

Para preguntas y controversias, priorizar registro oficial y publicaciones del propio actor. Si la atribución solo aparece en prensa, identificarla. La fuente acredita el planteo, no la veracidad de la acusación. Usar síntesis sin comillas y no presumir falta de respuesta. Distinguir fecha del hecho, cobertura y consulta. Las palabras clave son selección editorial; indicar si pertenecen a agenda posterior o general. Ver `REVISION_PREGUNTAS.md`.

Se reemplazaron antecedentes sin evidencia accesible por hechos respaldados: exposiciones ministeriales, estado de expedientes, composición completa y cronograma anunciado de Línea F. Se conservaron colores, clases, mosaicos y filtros. Cambiaron los textos, el número de filas y la longitud de la página. El registro histórico está en `docs/AUDITORIA-2026-10-26.md`.
