# Hallazgos y construcción — corte 2021

Qué trajeron los archivos, cómo se nombraron las carpetas y cómo se armaron el cajón A y las tablas.

El orden de trabajo sigue en [00-plan-de-trabajo.md](00-plan-de-trabajo.md).
La estrella está en [05-modelo-estrella-visual.md](05-modelo-estrella-visual.md).

## Carpetas

| Carpeta | Qué guarda |
|---|---|
| `docs/` | Este plan, las fichas y la estrella |
| `muestras/` | Cajón B. La primera copia de cada fuente, sin transformar |
| `generacion/` | El script del cajón A |
| `generacion/salida/` | Los CSV que escribe ese script |
| `base-de-datos/` | El SQL que crea las tablas vacías |

El polígono conserva el mismo nombre de base en `.shp`, `.dbf`, `.shx`, `.prj`, `.cpg`, `.sbn` y `.sbx`. Si uno solo cambia de nombre, el mapa no abre.

## Corte que quedó cerrado

Medellín, `05001`, todas las horas de 2021, ubicación Total.

El mapa de códigos puede ser Antioquia. El dato fino (cliente, hora, activo, falla) es solo Medellín, porque el clima horario solo existe para esa cabecera.

La muestra generada es de 1.000 clientes y 200 activos. No son los 996.993 suscriptores.

## Nombres

La copia no se editó. Solo se renombró con la fuente y la fecha.

| Nombre actual | Nombre con el que llegó |
|---|---|
| `divipola-codigos-municipios-20261007.csv` | `DIVIPOLA-_Códigos_municipios_20261007.csv` |
| `mgn2025-mpio/` | `MGN2025_MPIO_GRAFICO/` |
| `open-meteo-medellin-2021.json` | `clima 2021 entero.json` |
| `dane-poblacion-municipal-2018-2042.xlsx` | `PPED-AreaMun-2018-2042_VP.xlsx` |
| `sui-epm-antioquia-2021-suscriptores.csv` | `reporte sui completo año 2021.csv` |
| `epm-tarifas-2016-2021-20261007.csv` | `Histórico_de_Tarifas_de_Energía_Eléctrica_–_EPM_(2016-2021)_20261007.csv` |
| `sui-epm-medellin-2021-01-total.csv` | `reporte (1).csv` |
| `sui-epm-medellin-2021-01-urbano.csv` | `reporte.csv` |
| `open-meteo-medellin-20240101-20240107.json` | `open_meteo_archive.json` |
| `sui-facturacion-muestra-200.csv` | `gw2d-7n7y.csv` |
| `sui-caracterizacion-muestra-200.csv` | `endg-udcv.csv` |

## Fichas

### DIVIPOLA

```text
Fuente: DANE / DIVIPOLA
Archivo: muestras/divipola-codigos-municipios-20261007.csv
Fecha de la muestra: 2026-10-07
Filas de la muestra: 1.122 municipios. 125 son Antioquia, departamento 05
Años que aparecen: ninguno. Es un padrón
El periodo es mes, año u hora: no aplica
Columnas: Código Departamento, Nombre Departamento, Código Municipio, Nombre Municipio, Tipo, longitud, Latitud
Columna del código de municipio: Código Municipio. Medellín es 05001
El nombre del municipio viene en otra columna: sí
Qué grano es una fila: un municipio
Sirve para: la lista de ciudades y la coordenada de la cabecera
No sirve para: clientes, consumo ni clima horario
Duda que quedó: trae el país entero. Al cargar se filtra departamento 05. La coordenada usa coma decimal
```

### Polígono

```text
Fuente: DANE, Marco Geoestadístico 2025, nivel municipio
Archivo: muestras/mgn2025-mpio/mgn2025-mpio.shp
Fecha de la muestra: vigencia 2025
Filas de la muestra: 1.122 municipios
Años que aparecen: no es una serie de tiempo
El periodo es mes, año u hora: no aplica
Columnas de código: dpto_ccdgo, mpio_ccdgo, mpio_cdpmp, mpio_cnmbr
Columna del código de municipio: mpio_cdpmp. Medellín es 05001
El nombre del municipio viene en otra columna: sí, mpio_cnmbr
Qué grano es una fila: un municipio, un polígono
Sirve para: saber si un punto cae en la ciudad
No sirve para: pedir el clima
Duda que quedó: ninguna para este corte. Medellín es un solo anillo, 8.429 vértices, WGS84. OpenStreetMap no se usó
```

### Clima

```text
Fuente: Open-Meteo, archivo histórico
Archivo: muestras/open-meteo-medellin-2021.json
Fecha de la muestra: año 2021 completo
Filas de la muestra: 8.760 horas
Años que aparecen: 2021
El periodo es mes, año u hora: hora. El campo time es fecha-hora, por ejemplo 2021-01-01T18:00
Columnas: time, temperature_2m, precipitation, relative_humidity_2m, wind_speed_10m, surface_pressure
Columna del código de municipio: no viene
El nombre del municipio viene en otra columna: no
Qué grano es una fila: una hora de la cabecera de Medellín
Sirve para: lluvia y temperatura de 05001, al escribirle el código al guardar
No sirve para: los otros municipios, ni para un transformador
Duda que quedó: la API dejó el punto en latitud 6.2214413 y longitud -75.55185. La cabecera del DIVIPOLA es 6,246631 y -75,581775. Es el cruce de grilla más cercano, el mismo de la muestra de siete días
```

La muestra `open-meteo-medellin-20240101-20240107.json` es del 1 al 7 de enero de 2024. Quedó guardada para ver la forma. No entra al corte.

### Población

```text
Fuente: DANE, proyecciones de población por área
Archivo: muestras/dane-poblacion-municipal-2018-2042.xlsx
Fecha de la muestra: serie publicada 2018-2042. Hoja PobMunicipalxÁrea
Filas de la muestra: la hoja municipal pasa de 84.000 filas, con encabezado
Años que aparecen: 2018 a 2042. Cada año es una fila
El periodo es mes, año u hora: año
Columnas: DP, DPNOM, MPIO, DPMP, AÑO, ÁREA GEOGRÁFICA, TOTAL
Columna del código de municipio: MPIO. Medellín es 05001
El nombre del municipio viene en otra columna: sí, DPMP
Qué grano es una fila: un municipio, un año y un área
Sirve para: habitantes de 05001 en 2021, como contexto
No sirve para: crear clientes
Duda que quedó: el área trae Cabecera Municipal, Centros Poblados y Rural Disperso, y Total. El Total ya es la suma de las dos primeras. No se vuelven a sumar
```

Medellín, 2021, en esa hoja:

| Área | Habitantes |
|---|---|
| Cabecera Municipal | 2.459.249 |
| Centros Poblados y Rural Disperso | 48.371 |
| Total | 2.507.620 |

### SUI

```text
Fuente: SUI, Consolidado energía por empresa, departamento y municipio
Archivo: muestras/sui-epm-antioquia-2021-suscriptores.csv
Fecha de la muestra: año 2021
Filas de la muestra: 123 municipios
Años que aparecen: 2021
El periodo es mes, año u hora: año. El pie del archivo dice Período 25. En ese formulario el 1 es enero y el 25 es el anual
Columnas: Departamento, Municipio, Empresa, Variable Calculada, Estrato 1 a 6, Total Residencial, Industrial, Comercial, Oficial, Otros, Total No Residencial
Columna del código de municipio: no viene
El nombre del municipio viene en otra columna: sí, solo el nombre. A veces sin tilde
Qué grano es una fila: un municipio, un año, suscriptores de EPM, ubicación Total
Sirve para: la mezcla de estrato y tipo al crear la muestra de clientes
No sirve para: el kWh, ni para identificar a un cliente
Duda que quedó: Antioquia tiene 125 municipios. No aparecen Murindó ni Vigía del Fuerte. Hay celdas ND
```

Medellín en ese archivo: 996.993 suscriptores. En enero, el archivo `sui-epm-medellin-2021-01-total.csv` decía 974.552. Son dos cortes. No se suman. El urbano tampoco se suma con el Total.

El reporte no trae consumo ni kWh facturados. Si más adelante se quieren esas cifras, se exportan aparte, con la misma empresa, el mismo año y la ubicación Total.

### Tarifas EPM

```text
Fuente: EPM, datos abiertos, tarifas de energía
Archivo: muestras/epm-tarifas-2016-2021-20261007.csv
Fecha de la muestra: serie de diciembre de 2016 a diciembre de 2021
Filas de la muestra: más de 3.600
Años que aparecen: 2016 a 2021. En el corte se usan los doce meses de 2021
El periodo es mes, año u hora: mes. El mes viene con nombre: Enero, Febrero, y así
Columnas: Tipo de Información, Tipo de Tarifa, Tipo de Dato, Rango de Consumo, Nivel, Propiedad Epm, Compartido, Propiedad del Cliente, Punta, Fuera de Punta, Año, Mes
Columna del código de municipio: no viene
El nombre del municipio viene en otra columna: no
Qué grano es una fila: un precio de EPM en un año, un mes, un tipo y un nivel
Sirve para: el precio de la factura simulada. Se usa Monomia, nivel I, columna Propiedad Epm
No sirve para: cruzar con una ciudad, ni para el kWh medido
Duda que quedó: el precio usa $ y coma decimal, por ejemplo $573,05
```

Para el residencial de 2021 la fila que se usa es esta:

| Estrato | Rango que se toma |
|---|---|
| 1, 2 y 3 | `Rango > CS` |
| 4 | `Todo el consumo` |
| 5 y 6 | una sola fila, `Estrato 5 y 6`, `Todo el consumo` |
| Industrial, comercial y otros | `No Residencial` / `Industrial y Comercial` |
| Oficial | `Oficial y Exentos de Contribución` |

En enero de 2021, estrato 1, por encima del consumo de subsistencia, Propiedad Epm vale 573,05 pesos por kWh.

## Qué no entra

| Archivo | Por qué se queda fuera |
|---|---|
| `sui-facturacion-muestra-200.csv` | 200 facturas de Codensa. Sin código de municipio |
| `sui-caracterizacion-muestra-200.csv` | Usuarios de Cali. El municipio viene por nombre |
| `sui-epm-medellin-2021-01-urbano.csv` | El urbano ya está dentro del Total |
| `sui-epm-medellin-2021-01-total.csv` | Es enero. El corte usa el anual |
| `open-meteo-medellin-20240101-20240107.json` | Siete días de 2024 |
| OpenStreetMap | No se bajó. No trae `cod_divipola` |

## Cómo se construyó el cajón A

El script es `generacion/generar-cajon-a.py`. Lee las muestras y escribe `generacion/salida/`. No modifica el cajón B.

Para volver a correrlo, desde `generacion/`:

```text
pip install pyshp
python generar-cajon-a.py
```

`N_CLIENTES` y `N_ACTIVOS` están al inicio del archivo. La semilla es 2021, así que la misma corrida produce los mismos archivos.

Orden en que escribe:

| Paso | Archivo | Qué hace |
|---|---|---|
| 1 | `01-tiempo.csv` | Las 8.760 horas de 2021 |
| 2 | `02-cliente.csv` | 1.000 clientes con la mezcla del SUI de Medellín, todos con `05001` |
| 3 | `03-activo.csv` | 200 puntos que caen dentro del polígono |
| 4 | `04-consumo.csv` | Una fila por cliente y hora. La forma del día cambia con el tipo. La temperatura sube un poco el residencial |
| 5 | `05-factura.csv` | Suma de esas horas en el mes, por la tarifa EPM de ese mes |
| 6 | `06-falla.csv` | Fallas sobre activos. Más probabilidad si el activo es viejo o si esa hora tuvo lluvia o calor |
| 7 | `07-mantenimiento.csv` | Un preventivo por activo, y un correctivo en parte de las fallas |

La mezcla de los 1.000 clientes quedó así: estrato 1, 130; estrato 2, 309; estrato 3, 259; estrato 4, 103; estrato 5, 73; estrato 6, 39; industrial, 7; comercial, 77; oficial, 2; otros, 1.

La lluvia no se escribe en la falla. El consumo no lleva municipio: llega a Medellín por el cliente. El kWh de la hora y el kWh de la factura no se suman entre sí.

Comprobación ya hecha sobre los CSV, cliente `C0001`, enero de 2021:

| Prueba | Resultado |
|---|---|
| Horas de enero | 744 |
| Suma de esas horas | 145,9701 kWh |
| `consumo_kwh_mes` de su factura `2021-01` | 145,9701 kWh |
| Tarifa aplicada | 573,05 pesos, Propiedad Epm, estrato 1 |
| Activos | 200, todos con `05001`, un punto de ejemplo en 6,304471 y -75,588159 |
| Fallas | 522. La fila no tiene columna de lluvia |
| Mantenimientos | 428 |

## Cómo se construyeron las tablas

El script `base-de-datos/crear-tablas.sql` crea el esquema `makaia` y lo deja vacío. Si el esquema ya existía, lo borra y lo crea de nuevo. No inserta filas y no pide PostGIS.

| Tabla | De dónde sale la fila |
|---|---|
| `geografia` | DIVIPOLA |
| `tiempo` | `01-tiempo.csv` |
| `cliente` | `02-cliente.csv` |
| `activo` | `03-activo.csv` |
| `clima` | el JSON de 2021, con `05001` escrito al cargar |
| `consumo` | `04-consumo.csv` |
| `factura` | `05-factura.csv` |
| `falla` | `06-falla.csv` |
| `mantenimiento` | `07-mantenimiento.csv` |
| `poblacion` | la hoja municipal del DANE, año 2021 |
| `sui` | el CSV anual, después de traducir el nombre a `cod_divipola` |
| `tarifa` | el CSV de EPM, meses de 2021 |

La factura no apunta a `tiempo`. El periodo `2021-01` se repite en cada hora, y la llave de `tiempo` es la hora. La tarifa no apunta a `geografia`: no tiene municipio.

Esas tablas todavía no están cargadas. El paso que sigue es ejecutar el SQL y después insertar, primero el lugar y el contexto, y después los CSV de `generacion/salida/`.
