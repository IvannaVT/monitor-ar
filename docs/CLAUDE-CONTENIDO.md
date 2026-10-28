# Encargo breve para Claude

GitHub es la fuente única: https://github.com/IvannaVT/monitor-ar . Mientras se revisa la propuesta de síntesis, usar la rama `diseno/sintesis-y-lecturas`; después del merge, usar `main`. Leer `data/legislativo.json` y los registros de fuentes indicados para el lote solicitado. No enviar el repositorio completo ni reconstruir el sitio desde el artefacto anterior.

## Texto para copiar

Mejorá el contenido del anterior artefacto Monitor LEG, usando como base la versión revisada de GitHub. Trabajá únicamente en el lote de registros que te pase; conservá ID, fuente, atribución, fechas y alcance. No regeneres HTML, CSS ni JavaScript y no publiques cambios.

Organizá la propuesta en diagnóstico breve, palabras clave, coincidencias temáticas, diferencias de enfoque y próximo encuentro oficial. Usá frases cortas: diagnóstico hasta 30 palabras, cada planteo hasta 20 palabras y cada lectura temática hasta 35. No reduzcas el texto si eso elimina una atribución o condición necesaria.

Correcciones obligatorias del artefacto anterior:

- No trasladar sus sumas de bancas ni alianzas. Composición revisada: LLA 14, FxBA 20, CD 6, Vamos por más 12, Ciudadanos Unidos/UCR 5, FIT/PO 2 y Transformación 1: total 60. Consultar la [composición oficial](https://www.legislatura.gob.ar/seccion/bloques.html) antes de proponer cambios.
- El quórum es mayoría absoluta: 31 sobre 60, según las [preguntas frecuentes de la Legislatura](https://www.legislatura.gob.ar/seccion/preguntas-frecuentes.html). No pronosticar presencias o votos ni equiparar firma de dictamen con apoyo en el recinto.
- La nota de Salud del 23/10 es un comunicado; no acredita la publicación de una taquigrafía completa.
- Quitar SL_GA/Social Listening, resonancia alta/media, actores más activos y velocidades de circulación: falta corpus y método. No inventar métricas sustitutas.
- No afirmar falta de respuesta, acuerdos, coordinación, oferta vencida o caída de una sesión sin evidencia directa. Diferenciar coincidencia temática de acuerdo político y anuncio de hecho realizado.
- No ampliar el corte de datos por cambiar la fecha de redacción. No copiar acusaciones ni cifras sin período, unidad y fuente comprobable.

Devolvé sólo propuestas de cambios en JSON, con esta estructura por registro: `id`, `texto_actual`, `texto_propuesto`, `fuentes` (URL y ubicación/párrafo), `motivo`, `pendiente_de_verificacion`. Si no podés consultar una fuente, indicá la limitación y dejá el cambio pendiente. Tu salida es una propuesta: la verificación y aprobación se realizan antes de generar el sitio desde GitHub.

## Uso eficiente

Enviar de tres a cinco registros por vez, sus fuentes y extractos pertinentes. Evitar regenerar toda la página ante cambios de texto. Codex integra el lote aceptado, ejecuta los controles y abre o actualiza la PR; la titular publica mediante merge. Las correcciones editoriales y la huella de revisión se registran después del cotejo, nunca como aprobación automática de la salida de Claude.
