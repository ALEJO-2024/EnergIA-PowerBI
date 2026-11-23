# Páginas de Power BI — Medellín 2021

Cinco páginas para el esquema `makaia`. Cada una cuenta una historia con los datos que ya existen. El script de las tablas es `base-de-datos/crear-tablas.sql`. Los números de este corte están en [06-hallazgos-y-construccion.md](06-hallazgos-y-construccion.md).

El archivo de Power BI todavía no está armado. Este documento dice qué página se abre, qué gráfico lleva y qué se lee en él.

## Qué cuenta el tablero

Un año en Medellín, código `05001`.

La operación fina es una muestra: 1.000 clientes y 200 activos, todas las horas de 2021. No son los 996.993 suscriptores que publicó el SUI. El filtro de municipio sirve para cuando entre otra ciudad. Hoy, si se elige un municipio distinto de Medellín, el consumo, la factura, la falla y el clima se quedan vacíos. El SUI y la población sí pueden traer esa otra ciudad.

Las seis preguntas del plan caben en cinco páginas. La lluvia no tiene página propia: se compara con las fallas en la página 3, en un gráfico aparte. La población, el SUI y la tarifa cierran en la página 5, marcadas como contexto.

## El modelo que leen las páginas

| Tabla | Una fila es | La usa |
|---|---|---|
| `geografia` | Un municipio. Llave `cod_divipola` | Todas, como filtro |
| `tiempo` | Una hora de 2021. Llave `fecha_hora` | Consumo, fallas, clima |
| `cliente` | Un cliente de la muestra, con `cod_divipola` | Consumo y factura |
| `activo` | Un equipo, con punto y `cod_divipola` | Fallas y mantenimiento |
| `consumo` | Un cliente en una hora. `consumo_kwh` | Página 1 |
| `factura` | Un cliente en un mes. `consumo_kwh_mes`, valor, tarifa, estado | Página 2 |
| `falla` | Un evento sobre un activo | Páginas 3 y 4 |
| `mantenimiento` | Un trabajo sobre un activo | Página 4 |
| `clima` | Una hora de la cabecera. Lluvia y temperatura | Página 3 |
| `poblacion` | Un municipio, un año, un área | Página 5 |
| `sui` | Un municipio, un año, suscriptores publicados | Página 5 |
| `tarifa` | Un precio de EPM en un mes. Sin municipio | Página 5 |

Relaciones que sí se usan:

- `geografia` con `cliente`, `activo`, `clima`, `poblacion` y `sui`, por `cod_divipola`.
- `tiempo` con `consumo`, `clima` y `falla`, por `fecha_hora`.
- `cliente` con `consumo` y con `factura`, por `cliente_id`.
- `activo` con `falla` y con `mantenimiento`, por `infraestructura_id`.

Relaciones que no se crean:

- `factura` no se une a `tiempo`. El periodo `2021-01` se repite en cada hora. El filtro de mes de la factura es `factura.periodo`.
- `tarifa` no se une a `geografia`. No tiene municipio. El precio que cobró la muestra ya está guardado en `factura.tarifa`.
- `consumo` no se suma con `factura`. El kWh del mes ya es la suma de las horas.
- `clima` no se une a `falla` fila a fila. Primero se cuentan las fallas de esa hora. La lluvia se queda en su tabla.

Todas las páginas comparten el filtro `cod_divipola`. Las páginas 1 a 4 comparten también el año 2021.

## Página 1 — El año en el medidor

**Pregunta.** ¿Cómo se movió el consumo de la muestra en 2021?

**Historia.** La energía medida no es una línea plana. En una casa sube al final de la tarde. En un local pesa más el horario de trabajo. El estrato 2 aparece grande en el total porque en la muestra hay 309 clientes de ese estrato, no porque cada uno gaste más que un estrato 6. Esta página mira el medidor. No mira la factura.

**Gráficos.**

| Gráfico | Campos | Qué cuenta |
|---|---|---|
| Tarjeta | Suma de `consumo.consumo_kwh` | Los kWh medidos de la muestra en el periodo filtrado |
| Línea | Eje `tiempo.fecha`. Valor: kWh medidos | Si el año tuvo meses más altos y días que se salen |
| Columnas | Eje `cliente.tipo_cliente`. Valor: kWh medidos | Cuánto del total es residencial, comercial, industrial, oficial u otros |
| Barras | Eje `cliente.estrato`. Valor: kWh medidos. Solo residencial | Qué estrato mueve el total de las casas |
| Línea por hora | Eje `tiempo.hora`, de 0 a 23. Una línea por `tipo_cliente`. Valor: promedio de `consumo_kwh` | La forma del día. La casa debe verse más alta entre las 18 y las 21. El industrial, más plano |

**Cómo se lee.** Si la línea de las 19:00 del residencial queda por encima de las 3:00, el día de la muestra se parece al que se diseñó. Si el estrato 2 gana en la barra y el estrato 6 gana en el promedio por cliente, las dos cosas pueden ser ciertas a la vez: hay más cuentas del 2, y cada cuenta del 6 mide más.

**No cuenta.** No son los 996.993 suscriptores. No es el kWh cobrado. No se parte un total del SUI entre estos 1.000 clientes.

## Página 2 — La cuenta del mes

**Pregunta.** ¿Cómo quedó la factura de cada mes?

**Historia.** Cada cliente tiene una sola cuenta por mes. Esa cuenta es la suma de sus horas, multiplicada por el precio que EPM publicó para ese mes. El precio se mueve a lo largo de 2021 porque la tarifa publicada se mueve, no porque el medidor se haya vuelto a sumar. La mayoría de las cuentas queda pagada. Una parte queda pendiente o en mora.

**Gráficos.**

| Gráfico | Campos | Qué cuenta |
|---|---|---|
| Tres tarjetas | Suma de `valor_facturado`. Suma de `consumo_kwh_mes`. Conteo de facturas por `estado_pago` | La plata del periodo, los kWh cobrados y cuántas cuentas están pagadas, pendientes o en mora |
| Línea | Eje `factura.periodo`. Valor: suma de `valor_facturado` | Cómo creció o bajó el recaudo esperado mes a mes |
| Línea | Eje `factura.periodo`. Valor: promedio de `factura.tarifa` | El precio por kWh que usó la muestra. En enero, el estrato 1 queda en 573,05 pesos |
| Barras apiladas | Eje `factura.periodo`. Leyenda `estado_pago`. Valor: conteo de facturas | Si la mora se concentra en algún mes |
| Barras | Eje `cliente.tipo_cliente`. Valor: suma de `valor_facturado` | Qué tipo de cliente explica el valor, no solo el kWh |

**Cómo se lee.** Un mes puede medir menos kWh y facturar más, si la tarifa de ese mes subió. Por eso la línea de valor y la línea de tarifa van juntas, y el kWh facturado va en su propia tarjeta. El ejemplo de control es el cliente `C0001` en `2021-01`: 145,9701 kWh en las 744 horas de enero, y el mismo número en `consumo_kwh_mes`.

**No cuenta.** No se arrastra `consumo.consumo_kwh` a esta página para sumarlo otra vez. El estado de pago es de la factura, no del medidor de una hora.

## Página 3 — Dónde se fue la luz

**Pregunta.** ¿Dónde se concentraron las fallas, y la lluvia de esa hora las acompaña?

**Historia.** Cada falla cae sobre un activo que ya está dentro de Medellín. El mapa muestra en qué punto del municipio se juntan. El ranking no predice: ordena las horas y los equipos con más eventos, más clientes afectados y más minutos. Abajo, en otro gráfico, la lluvia de la cabecera se pone al lado del conteo de fallas. Son dos filas con la misma hora. La lluvia no viaja dentro de la falla.

En esta corrida hay 522 fallas.

**Gráficos.**

| Gráfico | Campos | Qué cuenta |
|---|---|---|
| Mapa de puntos | `activo.latitud`, `activo.longitud`. Tamaño: conteo de `falla.incidente_id` | Dónde se agrupan los eventos dentro del municipio |
| Tres tarjetas | Conteo de `incidente_id`. Suma de `clientes_afectados`. Suma de `duracion_minutos` | Cuántas fallas, a cuántos clientes alcanzan y cuántos minutos suman |
| Columnas | Eje `tiempo.mes`. Valor: conteo de fallas | En qué meses del año se acumulan |
| Tabla, ordenada de mayor a menor | `tiempo.fecha_hora`, conteo de fallas, suma de clientes afectados, suma de minutos | El ranking de horas. Es la “zona de mayor riesgo” de esta etapa: un orden, no un pronóstico |
| Líneas, dos ejes | Eje `tiempo.fecha`. Una línea: suma de `clima.precipitacion_mm`. Otra: conteo de fallas de ese día | Si los días de más lluvia son días de más fallas |

**Cómo se lee.** Un punto grande en el mapa es un activo con muchas fallas, no un barrio oficial: este corte no trae comuna. En el gráfico de lluvia, un día con 40 fallas cuenta la lluvia una vez. Si se viera la lluvia repetida en cada falla, el día quedaría inflado.

La muestra de control es la falla `F00001`, el 3 de marzo de 2021 a la 01:00: 38 clientes y 129 minutos. La lluvia de esa hora es 0,0 mm y no está escrita en la fila de la falla.

**No cuenta.** No calcula SAIDI ni SAIFI. Esos índices no salen de las fallas simuladas. El número de clientes afectados es el que trae la falla. No es una lista de `cliente_id`.

## Página 4 — Qué equipo falla más

**Pregunta.** ¿Qué activo concentra las fallas, y cuánto cuesta atenderlo?

**Historia.** Los 200 equipos no fallan igual. Un transformador viejo puede cargar más eventos que un poste nuevo. El mantenimiento es otra tabla: un preventivo por equipo y un correctivo después de parte de las fallas. En esta corrida hay 428 mantenimientos. La ciudad del equipo es la del punto que cayó en el polígono de `05001`.

**Gráficos.**

| Gráfico | Campos | Qué cuenta |
|---|---|---|
| Barras | Eje `activo.tipo`. Valor: conteo de fallas | Si el transformador, el poste, la línea, la protección o la subestación acumula más eventos |
| Tabla, ordenada de mayor a menor | `infraestructura_id`, `tipo`, `fecha_instalacion`, `estado`, conteo de fallas, suma de minutos, suma de `mantenimiento.costo` | El ranking de equipos. Arriba queda el que más falla, no el más nuevo |
| Dispersión | Eje X: antigüedad, `2021` menos el año de `fecha_instalacion`. Eje Y: conteo de fallas. Un punto por activo | Si los equipos más viejos están más arriba |
| Barras | Eje `mantenimiento.tipo`. Valor: suma de `costo` | Cuánto se fue en preventivo y cuánto en correctivo |
| Tarjeta | Suma de `mantenimiento.costo` | El costo de atender la muestra en el periodo filtrado |

**Cómo se lee.** Si los puntos viejos están más arriba en la dispersión, la edad acompaña la falla en esta muestra. Si un tipo tiene pocas fallas y un costo alto, el gráfico de costo lo muestra sin mezclarlo con el conteo. El estado del activo en esta corrida es `en servicio`: la página no promete una lista de equipos ya dañados.

**No cuenta.** No une el activo con un cliente. No usa el circuito de EPM. No predice el próximo daño.

## Página 5 — Lo que publican las fuentes

**Pregunta.** ¿Cómo se ve Medellín en el DANE, en el SUI y en la tarifa de EPM, al lado de la muestra?

**Historia.** Esta página no habla del cliente `C0001`. Habla del municipio. En 2021 el DANE estima 2.507.620 habitantes en el área Total. El SUI publica 996.993 suscriptores de EPM en el mismo año, ubicación Total. La tarifa dice cuánto costaba el kWh cada mes, sin decir en qué ciudad. Los tres números se miran juntos y no se suman entre sí. Tampoco se reparte ninguno entre los 1.000 clientes de las páginas anteriores.

**Gráficos.**

| Gráfico | Campos | Qué cuenta |
|---|---|---|
| Tarjeta | `poblacion.habitantes` donde `anio = 2021` y `area = 'Total'` | Los habitantes publicados. Medellín: 2.507.620 |
| Tarjeta | `sui.total_residencial` más `sui.total_no_residencial`, `anio = 2021`, `periodo = 25`, `ubicacion = 'Total'` | Los suscriptores publicados. Medellín: 996.993. El periodo 25 es el año, no un mes |
| Barras | Eje: estrato 1 a 6. Valor: `estrato_1` … `estrato_6` | La mezcla real de la ciudad. El estrato 2 es el más grande, con 307.598 |
| Barras | Eje: industrial, comercial, oficial, otros | El resto de las cuentas publicadas. Comercial: 76.833 |
| Línea | Eje: `tarifa.mes`. Valor: `precio_propiedad_epm`. Filtro fijo: año 2021, Monomia, nivel I, y la serie residencial que usa la factura | Cómo se movió el precio publicado. No es un dato de una ciudad |
| Texto fijo en la página | — | “Contexto publicado. No es la muestra de 1.000 clientes.” |

**Cómo se lee.** 2,5 millones de habitantes y 996.993 suscriptores pueden verse juntos sin convertirse el uno en el otro. Una persona no es una cuenta de energía. La barra del SUI explica por qué la página 1 tiene 309 clientes de estrato 2 y solo 39 de estrato 6: la muestra copia esa proporción, en pequeño.

La cabecera de Medellín en 2021 tiene 2.459.249 habitantes y el resto del municipio 48.371. Esas dos cifras ya están dentro del Total. No se vuelven a sumar.

**No cuenta.** No muestra el kWh del SUI: ese archivo no lo trae. No baja al cliente ni al transformador. No cruza la tarifa con `cod_divipola`.

## Lo que las cinco páginas no hacen

| No entra | Dónde quedaría |
|---|---|
| Demanda de XM | Después de esta etapa, solo por fecha |
| SAIDI y SAIFI calculados con las fallas | No se calculan. El SUI de este corte no los trae |
| Anomalías, predicción, preguntas en lenguaje natural | Etapa 2 |
| Comuna o barrio | Este mapa no trae ese polígono |
| Los 996.993 clientes hora por hora | Sigue siendo la muestra de 1.000 |
