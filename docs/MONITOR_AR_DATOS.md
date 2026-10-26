# Monitor AR: datos y actualización

Monitor AR es independiente de Monitor LEG. Este procedimiento, scripts y controles se aplican únicamente a Monitor AR; no se modifican los datos, el diseño ni el generador de Monitor LEG.

## Isasi-Burdman agosto 2026

Gestión de Javier Milei: 42% aprueba,48% desaprueba,10% no sabe. Fuente primaria: informe de agosto,página física3;Drive1Phw7mb5Dy9q7of8G-5wbfxUqy2lwxKgT. El maestro trazable ya contenía estas cifras. Se corrigen N2,las series GESTION/CROSS,las tablas estáticas yla interpretación que infería una suba deaprobación.

La corrección no certifica todas las demás cifras del JSON ni resuelve las discrepancias deimagen personal detectadas enlas bases heredadas. Imagen personal ygestión siguen siendo preguntas diferentes.

## Extracción oficial de inflación

scripts/extract_inflacion.py descarga la serie CSV oficial INDEC ydescubre el XLSX actual desde la página oficial IDECBA. Solo nivel general nacional yCABA;variación mensual publicada enambas fuentes,interanual publicada solo INDEC. No calcula acumulados ni interanuales ausentes.

Cada registro conserva territorio,base,período de referencia,URL,huella SHA256 yfila/celda deorigen. La fecha deconsulta yLast-Modified no se interpretan como fecha depublicación. Los originales se conservan porhuella.

El workflow inflacion-ar.yml se ejecuta diariamente a21UTC(18hArgentina),manualmente yante cambios relevantes enmain. Las PR ejecutan pruebas,sin descargar ni publicar datos. Se recupera el último artefacto exitoso para detectar revisiones operdida dedatos. Cambios deesquema,duplicados,huecos temporales oerrores bloquean lacarga. El workflow solo tiene permisos delectura;no modifica main ni losdatasets deSheets.

Salida: artefacto inflacion-oficial-ar coninflacion_oficial.json yoriginales,retenido90días enGitHubActions. Todos los registros salen pendientes deintegración al maestro ypublicable_monitor=false. No confundir extracción automática conpublicación automática:la promoción al maestro,el cotejo dehistóricos yla exportación al monitor son etapas posteriores. Una falla no reemplaza el último resultado válido.

Pruebas:python scripts/test_inflacion.py;python -m unittest discover -s tests -p test_monitor_ar.py. Dependencia:openpyxl3.1.5. No requiere API paga ni secretos adicionales.

## Nuevos informes deoctubre

El26/10se auditaron14PDF directos y2provinciales enla carpeta deoctubre conocida. Ocho son nuevos respecto delcatálogo trazable;no significa ocho cargas realizadas hoy. Se registran pendientes,sin integrar cifras: PulsarUBA,CELAG,ZubanCórdoba,QSocialTerceraAlternativa,Analogías,PDMArgentina,GrupoFeedbackCórdoba ySiri&OrtegaMendoza.

Pulsar yPDMson compilaciones:identificar fuentes originales,no tratarlos como encuestas independientes.PDMcombina períodos2025–2026. Zuban declara1600casos,online,16–19octubre.CELAGdeclara2000casos presenciales.Siri declara400casos,núcleos urbanos Mendoza,muestreo noprobabilístico yexclusión deindecisos/abstencionistas:reservar inferencias.Estos datos son cribado textual,no auditoría completa de resultados.QSocial,Analogías yFeedback requieren revisión visual porfalta detexto recuperable.

No se añadieron valores deestos informes al maestro. Continúa en3267observaciones,3066habilitadas y201bloqueadas. Catálogo curado:318Drive+1referencia externa;4integrados,45parciales,246pendientes,23excluidos delrecorte.Fecha exacta pendiente314de319referencias.

## Circuito incremental

Informes originales → lote provisional porID/versión → dataset trazable → validación → maestro → vista analítica porfamilia/comparabilidad → exportación versionada → MonitorAR.

Procesar solo archivos nuevos/modificados.Reutilizar extracciones.No enviar bases completas aClaude.No cambiar valores manualmente envarias vistas.El monitor debeconsumir únicamente cifras habilitadas,con filtros adicionales decomparabilidad para series.Los archivos históricos no se suman al maestro sinconciliación.

