# Series mensuales de Monitor AR

Versión propuesta AR-SERIES-1.0 · corte 26/10/2026.

## Regla de entrada

Una serie necesita tres meses consecutivos con observaciones numéricas habilitadas de la misma consultora, variable, categoría, población, territorio y unidad. Debe existir dictamen documental de comparabilidad y respaldo de los meses de publicación. La usuaria eligió expresamente tres meses consecutivos. El resto de esta especificación queda propuesto hasta su aceptación.

Tres meses son un umbral operativo de seguimiento, no una prueba estadística de tendencia. No se certifica homogeneidad por compartir un nombre: hay que revisar pregunta, opciones de respuesta, técnica, universo y base de cálculo. Un cambio sustancial abre una serie nueva o una ruptura documentada. Segmentos electorales con distinta definición no se empalman automáticamente.

## Dos relojes, sin sustituir uno por otro

El repositorio se ordena por publicación; el período del dato y las fechas de campo se guardan separados. La edición rotulada, la fecha de carga en Drive y la fecha de campo no prueban publicación. Se acepta evidencia con precisión mensual cuando la fuente acredita explícitamente el mes de publicación; el día puede quedar vacío. La excepción Giacobbe septiembre es una decisión documentada de la usuaria.

Una serie histórica reproducida dentro de un solo informe no equivale a varias publicaciones mensuales. Puede conservarse como historia del período observado, pero debe identificarse la edición que la publicó y no utilizarse para simular cobertura del repositorio. Inflación publicada en octubre puede referirse a septiembre: ambos campos deben verse.

## Delta

Delta = valor del mes menos valor del mes inmediato anterior, dentro de una misma serie. Para porcentajes se expresa en puntos porcentuales; para índices, puntos de índice y escala. No se calcula contra el último mes disponible si hay un hueco. Tampoco se imputan ceros ni se arrastran cifras.

La tabla habilitada calcula el delta por mes de publicación y muestra el período al que se refiere la cifra. La tabla de candidatos conserva el delta por período del dato y lo rotula provisional: NO equivale a delta por publicación. Los deltas son descriptivos; sin evaluación de incertidumbre no se etiquetan como cambios estadísticamente significativos.

## Faltantes, revisiones y permanencia

El umbral selecciona series, no borra observaciones. Una serie con un tramo válido puede conservar su historia; los huecos posteriores quedan abiertos y el último mes se muestra explícitamente. Para presentarla como actual en octubre debe existir una observación acreditada publicada en octubre. Revisiones se registran con valor anterior, nuevo, motivo, evidencia, fecha y edición aceptada; no sobrescribir el historial.

Un informe puntual permanece en la capa de contexto con su fecha y límites. Bajo el filtro de series no se muestra su porcentaje como curva. Una coincidencia temporal sirve para formular hipótesis, no para demostrar que un evento causó el movimiento de otro indicador.

## Familias y visualizaciones

1. Imagen personal: positiva y negativa separadas. Curvas por consultora o pequeños gráficos comparables. No equivalen a aprobación de gestión.
2. Gestión: aprobación/desaprobación y evaluación buena/mala se mantienen diferenciadas cuando la pregunta lo requiere. Curvas con mismo eje; sin promedio automático entre consultoras.
3. Economía: índices oficiales y percepciones en paneles distintos. Series de tasas, barras mensuales e índices con escala explícita.
4. Agenda: variables por pregunta espontánea/guiada y respuesta única/múltiple. Barras por consultora; no ranking combinado de porcentajes incompatibles.
5. Voto: separar elección, territorio, escenario, oferta de candidatos y universo. Potencialidad no equivale a intención efectiva de voto.
6. Conversación digital: corpus, plataformas, ventana y clasificación explícitos. Un porcentaje de menciones no representa electores ni opinión nacional.
7. Medios: corpus y métrica propios; no mezclar alcance, rating, visitas y menciones.
8. Cobertura: matriz consultora × mes con estados, más tabla auditable consultora–variable–categoría–población–mes–valor–delta–fuente–página.

## Flujo de cierre

Informe y versión → inventario de todas las preguntas/tablas/gráficos → extracción con página y base → dataset validado → conciliación con maestro → auditoría de comparabilidad y publicación → filtro de tres meses → exportación versionada → visualización → aceptación → bitácora de edición.

Cada gráfico requiere un manifiesto de observaciones e identificadores. Deben cuadrar cantidades y valores entre extracción, dataset, maestro y exportación. Cotejar capas sin diferencias NO certifica que se extrajeron todos los datos de todos los informes.

## Diagnóstico al corte

La lectura del banco contiene 3.267 observaciones, 3.066 cifras habilitadas y 201 bloqueadas. Se verificaron identificadores, fuente, página y habilitación contra B_Evidencias, B_Vinculos y B_Uso_datos: cero diferencias en esos campos; no es una auditoría de todos los metadatos ni de las fórmulas.

El catálogo contiene 319 referencias y 41 tienen observaciones en el maestro. No se certificó extracción exhaustiva de todas las tablas/gráficos de las 319 referencias. Hay 70 combinaciones con tres períodos consecutivos: 62 pendientes de publicación, cinco de comparabilidad y tres habilitadas por publicación en el control aplicado. Las tres corresponden a IPCBA (mensual, interanual y acumulado).

La asignación de D’Alessio a octubre sigue sin resolver: nombre del archivo octubre, edición septiembre y campo octubre. No se usa campo para resolver publicación. Los ocho documentos nuevos inventariados continúan sin alta numérica en el maestro. Se conservaron cuatro PDF para cotejo; esa descarga no acredita su integración.

Se detectaron además 30 registros candidatos ICC/ICG sin página registrada. Quedan marcados como pendientes, aunque la cifra heredada esté habilitada en el maestro. El control de entrada exige localización de evidencia.
