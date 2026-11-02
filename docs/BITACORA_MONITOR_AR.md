# Bitácora de Monitor AR

Registro por adición de entradas. No reescribir decisiones aceptadas: registrar una revisión que las sustituya y conservar el antecedente. Cada edición debe guardar identificador, fecha, autor/responsable, alcance, motivo, antes/después, fuentes, validaciones, estado, evidencia de aceptación, commit/PR y tareas pendientes.

Estados: **propuesta**, **en revisión**, **aceptada**, **descartada**, **sustituida**. Integrar un PR autorizado acredita aceptación técnica de ese cambio; no acredita automáticamente que todos sus datos o reglas sean válidos. Las reglas nuevas requieren decisión explícita de la usuaria. La publicación del sitio se verifica por separado.

## AR-20261026-01 — Isasi y extracción oficial — ACEPTADA

- Solicitud: corregir Isasi agosto, mantener independiente Monitor LEG y crear extracción de inflación oficial.
- Antes: Monitor AR invertía aprobación/desaprobación de agosto (48/42); maestro correcto, N2 incorrecto; extractor no instalado.
- Después: 42% aprobación, 48% desaprobación, 10% no sabe. N2 corregido y variaciones julio–agosto −4/+1 pp. HTML/JSON y narrativa corregidos. Extractor INDEC/IDECBA instalado.
- Evidencia: informe Isasi agosto, página 3, Drive 1Phw7mb5Dy9q7of8G-5wbfxUqy2lwxKgT. La corrección no valida otras cifras heredadas.
- Pruebas: nueve del extractor y dos de Monitor AR aprobadas; controles de GitHub aprobados; consulta del sitio público confirmó 42/48/10 y texto corregido.
- Aceptación: la usuaria pidió «avanza» después de la propuesta concreta #11 y se integró. PR https://github.com/IvannaVT/monitor-ar/pull/11. Commit 10ba8530543a8b923fb11f220213babe588f72c9.
- Extractor: primera ejecución exitosa https://github.com/IvannaVT/monitor-ar/actions/runs/40417464919; dataset y originales conservados como artefacto. Programación diaria 21 UTC, 18 h Argentina; no garantiza hora exacta de inicio.
- Límite: extracción provisional; no promoción automática a Sheets ni al monitor. Fechas de publicación y conciliación histórica pendientes. No se modificaron archivos de Monitor LEG.
- Incidencia resuelta: escritura del conector inicialmente 403; tras guardar la instalación con acceso a monitor-ar se verificó creación de rama y escritura de ocho archivos. El paquete manual previo queda como antecedente, no como versión vigente del sitio.

## AR-20261026-02 — Octubre, filtro y cobertura — EN REVISIÓN

- Solicitud: ampliar octubre en todas las secciones; tabla consultora–variable–mes–delta; cotejar informes, dataset y maestro; proponer agrupaciones/visualizaciones.
- Aceptado expresamente: tres meses consecutivos como umbral; registrar las ediciones aceptadas en bitácora. Publicación y campo separados siguen siendo una regla previa.
- Propuesto: AR-SERIES-1.0, con comparabilidad por pregunta/población, deltas mensuales contiguos, sin imputación y distinción entre series y contexto. No declarar aceptada toda la metodología por su mera redacción.
- Acción: lectura actual de P_Dataset, B_Repositorio_pub, B_Estudios y B_Documentos; conciliación de identificadores/fuente/página/habilitación con B_Evidencias, B_Vinculos y B_Uso_datos. Exportaciones diagnósticas derivadas; ninguna cifra del maestro fue modificada en esta edición.
- Resultado: 3.267 observaciones; 3.066 habilitadas; 201 bloqueadas; cero diferencias en campos cotejados entre capas. 70 grupos con tres períodos consecutivos, solo tres con publicación y comparabilidad acreditadas según el control aplicado.
- Pendiente: inventario exhaustivo pregunta por pregunta de los informes sin cerrar, acreditar publicación, resolver D’Alessio y completar extracción/cotejo de octubre. No se certifica exhaustividad por haber leído el maestro.
- Aplicación: los filtros nuevos se muestran en una vista de auditoría; los gráficos heredados quedan identificados como archivo pendiente de conciliación. No se afirma que ya cumplan el filtro.
- Aceptación de edición: pendiente de decisión explícita; registrar aquí su evidencia cuando ocurra.

## Formato obligatorio para próximas entradas

ID · fecha · estado · solicitud · archivos/rangos afectados · antes/después · motivo · fuente/página · validaciones y límites · PR/commit · aceptación (quién, cuándo y qué alcance) · reglas para conservar · pendientes.

## AR-20261026-02 · actualización de control

Se agregaron AR_Tabla_3M!A1:N347 (346 registros candidatos), AR_Publicadas_3M!A1:N16 (15 registros habilitados) y AR_Bitacora!A1:K5 al mismo libro maestro. Se marcaron 30 candidatos ICC/ICG sin página de origen; no se alteraron sus cifras en P_Dataset. Lectura posterior: cero diferencias en la tabla de 346 registros. La vista de auditoría distingue período y publicación, y los gráficos heredados se identifican como pendientes de conciliación. Se agregaron seis pruebas de regresión de cobertura, deltas, evidencia y límites de la auditoría; aprobadas localmente. El navegador de verificación no estuvo disponible; la revisión visual de la propuesta permanece pendiente. Estado: EN REVISIÓN.

## AR-20261026-02 · estado de entrega

La propuesta de sitio NO fue subida ni publicada. La revisión automática rechazó crear codex/auditoria-series-bitacora-20261026 porque interpretó vigente la instrucción anterior de entregar solo un paquete manual. La escritura en Sheets sí se completó. No se intentó eludir el rechazo. La autorización específica para crear rama y PR queda pendiente; la propuesta se conserva en un paquete local revisable.


## AR-20261026-02 · autorización para presentar la propuesta

La usuaria autorizó explícitamente «Sí, autorizo crear la rama y la PR» para subir el paquete preparado. Alcance: crear la rama y abrir la propuesta, sin integrarla ni publicarla. La aceptación de la edición completa y la revisión visual siguen pendientes.

## AR-20261026-02 · propuesta presentada

Se creó la rama autorizada y se abrió el borrador https://github.com/IvannaVT/monitor-ar/pull/12. Commit inicial de la propuesta: 2d154901257fe87b947795fe2f1c6907afc775ee. Los controles de GitHub check, extract y audit aprobaron sobre ese commit; el despliegue quedó omitido. Se mantiene EN REVISIÓN, sin integración ni publicación. Esta entrada resuelve la autorización pendiente del registro anterior, que se conserva como antecedente.
