# Monitor AR — Opinión Pública Argentina

Repositorio de los tableros de seguimiento: opinión pública, monitor legislativo y radar electoral.

## Contenido

| Archivo | Tablero | Origen del HTML |
| --- | --- | --- |
| `index.html` | Sitio principal — indicadores de opinión pública | Edición directa |
| `monitor_ar.html` | Monitor AR — dashboard de indicadores | Edición directa |
| `monitor_leg.html` | Monitor LEG — Presupuesto CABA | **Generado. No editar a mano** |
| `radar_eeuu_2026.html` | Radar Elecciones EEUU 2026 | Edición directa |

## Monitor LEG — modelo de actualización

Monitor LEG no se edita como HTML. Tiene tres piezas con roles separados:

| Pieza | Rol |
| --- | --- |
| `data/legislativo.json` | **Fuente de contenido.** Todo dato publicado sale de acá |
| `monitor_leg.template.html` | **Diseño.** CSS, interacciones y huella visual |
| `monitor_leg_view.py` | **Estructura.** Arma el cuerpo a partir del JSON |
| `monitor_leg_build.py` | **Generación y validación.** Produce `monitor_leg.html` de forma determinista |

### El artefacto de Claude es referencia de diseño, no fuente de publicación

Cuando el diseño se trabaja en un artefacto de Claude, de esa exportación **se toma el CSS y la estructura visual, no el HTML ni su contenido**. Las afirmaciones del artefacto no pasan al sitio sin cotejo previo contra fuente oficial. Ver `DISENO_CLAUDE.md`.

El artefacto puede ser un documento de trabajo interno con un estándar distinto del público. La versión publicada, en cambio, no reproduce:

- rótulos de uso interno;
- rótulos de auditoría, pendientes de cotejo o notas de verificación — van a `docs/` o a la PR, no a la página;
- resonancia mediática o latencias de medios sin método declarado;
- probabilidades sin método;
- **inferencia de voto en el recinto a partir de firmas de dictamen;**
- predicciones de quórum o sumas de alianzas.

La identificación editorial se escribe «Social Listening GA», nunca la abreviatura.

El generador bloquea el build si detecta en el HTML los términos `auditoría`, `auditoria`, `sin verificar`, `pendiente de cotejo` o `prob.`.

### Rol de Claude en la actualización

Claude es opcional. Cuando se usa, recibe solo los registros que cambian y los extractos oficiales suficientes, y devuelve **una propuesta en JSON** con: ID, valor anterior, valor propuesto, URL, localización en la fuente y motivo. No regenera el HTML ni recibe el repositorio o el historial completo.

### Procedimiento

El proceso completo, con los siete pasos obligatorios, está en **`PUBLICACION.md`**. Resumen:

1. Rama y PR. Cotejar cada afirmación nueva o modificada en fuente oficial, y revisar si los registros vigentes siguen válidos al nuevo corte.
2. Publicar solo registros cotejados, distinguiendo anuncio, proyecto, dictamen, sanción, adjudicación e inicio efectivo.
3. Actualizar datos, fuentes y corte. Registrar la revisión en `revision`, con la huella SHA-256 del contenido canónico.
4. `python monitor_leg_build.py` y luego `python monitor_leg_build.py --check`. Probar escritorio y móvil, filtros y enlaces.
5. Describir en la PR qué cambió y con qué evidencia. Mezclar solo después de la revisión humana.
6. Verificar la publicación: ejecución del workflow, URL pública, fecha de corte y filtros.

La huella SHA-256 detecta cambios posteriores a la revisión; no certifica veracidad. El control automatizado no reemplaza el cotejo editorial humano.

## Deploy — dos rutas, una sin chequeo

El repositorio publica por dos caminos simultáneos, con garantías distintas:

| Ruta | Mecanismo | Chequeo previo |
| --- | --- | --- |
| GitHub Pages | push a `main` → `.github/workflows/pages.yml` → `monitor_leg_build.py --check` y scripts de validación → despliega **solo si pasa** | Sí |
| Netlify | push a `main` → despliegue de los archivos estáticos del repo | **No** |

Las PR no despliegan por ninguna de las dos rutas.

**Implicancia:** un HTML desactualizado o una edición de contenido sin nueva revisión **bloquean la publicación en GitHub Pages, pero no en Netlify**. `PUBLICACION.md` establece no usar rutas de publicación que omitan el chequeo; mientras Netlify siga conectado a `main`, esa condición no se cumple por configuración y depende de que cada cambio entre por el procedimiento.

Para cerrar la brecha, las opciones son restringir Netlify a desplegar el artefacto ya chequeado, o dejar una sola ruta activa. Pendiente de definición.

Pendiente de verificar: el sitio figuraba antes en `https://ivannatravaini.netlify.app/`; confirmar cuál de los dominios Netlify está activo y si ambos apuntan a este repositorio.

## Alcance de la validación

Los scripts de chequeo cubren Monitor LEG. No certifican los indicadores de Monitor AR, que se mantienen por edición directa y con su propia documentación en `docs/MONITOR_AR_DATOS.md`.

## Documentación

| Archivo | Contenido |
| --- | --- |
| `PUBLICACION.md` | Proceso obligatorio previo a cada publicación |
| `DISENO_CLAUDE.md` | Alcance de la adaptación visual y corrección del mapa de bancas |
| `REVISION_PREGUNTAS.md` | Criterios editoriales para preguntas y controversias |
| `docs/` | Registro histórico de auditorías y actualizaciones |
