# Monitor LEG · corte 26/11/2026 — dictámenes del 25/11

## Qué se incorporó

El 25/11/2026 la Comisión de Presupuesto, Hacienda, Administración Financiera y Política Tributaria emitió dictamen de mayoría, único de comisión, en los cinco expedientes del Ejecutivo para 2027. Reunión de las 10:00 en el Salón San Martín, agenda 4855, reunión 30894. Los cinco expedientes ingresaron el 30/09/2026.

| Expediente | Despacho | Preferencia | Observaciones hasta |
| --- | --- | --- | --- |
| 3079-J código fiscal 2027 | 923-2026 | Sí | 30/11/2026 14:00 |
| 3080-J ley impositiva 2027 | 924-2026 | Sí | 30/11/2026 14:00 |
| 3081-J ley arancelaria 2027 | 925-2026 | Sí | 30/11/2026 14:00 |
| 3083-J presupuesto general 2027 | 926-2026 | Sí | 30/11/2026 14:00 |
| 3084-J financiamiento Belgrano Sur | 922-2026 | No | 04/12/2026 14:00 |

Registros agregados o modificados en `data/legislativo.json`:

| ID | Operación | Destino en la página |
| --- | --- | --- |
| `exp3079` a `exp3084` | Alta de cinco fuentes | Enlaces de evidencia en cada registro |
| `PAN-03` | Texto reemplazado | Aviso superior |
| `A-06` | Alta | Panel de cronología legislativa |
| `S-05` | Alta | Seguimiento |
| `S-06` | Alta | Seguimiento |
| `NOV-DIC-01` | Alta | Novedades y contexto |
| `P-02` | Texto reemplazado | Proyectos prioritarios |

## Antecedente: firmas de los dictámenes

Este apartado no se publica. `DISENO_CLAUDE.md` establece que no se deduce apoyo en el recinto a partir de las firmas de dictamen, y `PUBLICACION.md` prohíbe inferir votos de ese modo. Se registra acá como antecedente de trámite.

Lectura de la web parlamentaria del 25/11 por la noche, sobre 23 miembros de comisión.

Expedientes 3079-J, 3080-J, 3081-J y 3083-J, con idéntica composición de firmas:

- Firman sin disidencia (7): Donati, López, Loupias, Parera, Siciliano, Thourte, Wolff.
- Firman con disidencia (4): Pakgojz, Pelayo, Ramírez, Vartabedian.
- No firman (12): Arenaza, Barroetaveña, Bielli, Caporiccio, Casielles, Ferrario, Iañez, Lammens, Modarelli, Nagata, Negri, Neira.

Expediente 3084-J:

- Firman sin disidencia (13): los siete anteriores más Ferrario, Nagata, Pakgojz, Pelayo, Ramírez y Vartabedian.
- No firman (10): Arenaza, Barroetaveña, Bielli, Caporiccio, Casielles, Iañez, Lammens, Modarelli, Negri, Neira.

«No firma» puede corresponder a una firma pendiente de carga en el sistema. Releer antes de usar este detalle en cualquier pieza, interna o pública.

## Pendientes de esta corrida

Los textos de los dictámenes de 3079-J, 3080-J, 3081-J y 3083-J no se leyeron. Por eso los registros publicados atribuyen el contenido al proyecto remitido por el Ejecutivo —«el proyecto remitido por el Ejecutivo fija…»— y no al dictamen. El dictamen puede diferir del proyecto. Para el próximo corte: leer los cuatro dictámenes y, si hay diferencias, corregir la atribución.

El único dictamen cotejado contra su proyecto es el del 3084-J: no registra diferencias en los artículos 1 a 8 y agrega un considerando sobre la presencia de funcionarios del Ejecutivo que informaron. Así consta en `P-02`.

No se leyeron los anexos completos de las leyes impositiva y arancelaria, ni las planillas del presupuesto, incluida la planilla 43 de operaciones de crédito público.

Queda por cotejar la formulación de la exención del código fiscal para enero–junio de 2027. El documento de trabajo de la titular dice «librerías» y un resumen posterior dice «libros». Se publicó «librerías», por ser la formulación del documento derivado del texto del proyecto. Verificar contra el articulado.

Sin relevamiento de posiciones de bloque posteriores al 26/10. La nota de la tabla de posiciones sigue advirtiendo que las posiciones de noviembre y los votos sobre el Presupuesto 2027 están pendientes de confirmación.

## Revisión

`revision.responsable` queda asentado como propuesta de Claude con fuentes oficiales, a la espera de revisión editorial. La huella de contenido se recalculó sobre el JSON canónico sin `revision`. La huella detecta cambios posteriores; no sustituye el cotejo editorial, que corresponde a la titular antes de mezclar.

`revision.css_sha256` no cambia: esta corrida no toca el diseño.

## Comprobaciones

```
python3 monitor_leg_build.py           # regenera monitor_leg.html
python3 monitor_leg_build.py --check    # OK
python3 scripts/check_cifras.py         # OK
python3 scripts/check_indicadores.py    # OK
python3 scripts/check_sintaxis.py       # OK
python3 -m unittest discover -s tests -p 'test_radar_data.py'   # 8 tests OK
```

`check_cifras.py` emite dos avisos preexistentes sobre la cifra 26.4, ajenos a esta corrida.

Los archivos se mantienen con fin de línea CRLF, como el resto del repositorio.
