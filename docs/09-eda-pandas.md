# EDA con pandas, volumen de Databricks

Cada archivo de `muestras/` tiene un script en `eda/`. El script lee con pandas y no escribe tablas. Si el archivo existe en `/Volumes/main/default/Muestras/`, lo lee de ahí. En esta máquina, donde ese volumen no está montado, lee la copia local. El grano no cambia por cambiar de ruta.

Desde `eda/`:

```text
python divipola.py
python clima.py
python clima-2024.py
python poblacion.py
python sui.py
python sui-enero-total.py
python sui-enero-urbano.py
python sui-facturacion.py
python sui-caracterizacion.py
python tarifas.py
python poligono.py
```

En Databricks el polígono tiene que conservar la carpeta: `/Volumes/main/default/Muestras/mgn2025-mpio/mgn2025-mpio.shp`, con sus archivos al lado. El resto va suelto en el volumen, con el mismo nombre.

`poblacion.py` usa openpyxl. `poligono.py` usa pyshp. Los CSV del cajón A no se volvieron a leer aquí: ya tienen su ficha en [08-eda-local.md](08-eda-local.md).

## Qué confirmó la corrida

| Archivo | Filas | Cómo llega | ¿Entra al corte? |
|---|---|---|---|
| DIVIPOLA | 1.122 municipios, 125 de Antioquia | utf-8, coma, sin celdas vacías | sí |
| Clima 2021 | 8.760 horas | JSON utf-8, sin hora vacía | sí. Al guardar se le escribe `05001` |
| Clima 2024 | 168 horas, 1 al 7 de enero | el mismo JSON, otro año | no |
| Población | 84.225 filas en `PobMunicipalxÁrea` | Excel. La fila de columnas es la 8 | sí, solo Medellín 2021, área Total |
| SUI anual | 123 municipios | cp1252. El pie no es una fila de municipio | sí. Período 25 |
| SUI enero Total | 1 fila, Medellín | cp1252. Pie con período 1 | no |
| SUI enero Urbano | 1 fila, Medellín | cp1252. Pie con ubicación Urbano | no |
| Facturación SUI | 200 filas, 67 columnas | utf-8. Codensa, código 2103, año 2021, período 7 | no |
| Caracterización SUI | 200 filas, 36 columnas | utf-8. Empresas Municipales de Cali, código 2438, año 2021, período 8 | no |
| Tarifas | 3.623 filas | utf-8. Años 2016 a 2021 | sí, los doce meses de 2021 |
| Polígono | 1.122 municipios, 11 atributos | shapefile. Medellín, un anillo, 8.429 vértices | no se vuelve a leer para el consumo |

## Cómo llega cada archivo del corte

DIVIPOLA. La columna de tipo se llama `Tipo: Municipio / Isla / Área no municipalizada`. Medellín es `05001`, nombre `MEDELLÍN`, latitud `6,246631`, longitud `-75,581775`. La coma es decimal. El código y el nombre vienen en columnas distintas.

Clima 2021. Pandas arma una tabla con `time`, `temperature_2m`, `precipitation`, `relative_humidity_2m`, `wind_speed_10m` y `surface_pressure`. La primera hora es `2021-01-01T00:00` y la última `2021-12-31T23:00`. El punto es latitud 6,2214413, longitud -75,55185, elevación 1.475, zona `America/Bogota`. No trae `cod_divipola`. La lluvia de la primera hora es 0,1 mm y la temperatura 17,7 °C. Ninguna de las 8.760 horas viene vacía.

Población. Antes de `DP, DPNOM, MPIO, DPMP, AÑO, ÁREA GEOGRÁFICA, TOTAL` hay filas de título. En esta lectura `MPIO` llegó como texto `05001`. El script igual rellena el cero, por si Excel lo entrega como número. Medellín, 2021: cabecera 2.459.249, resto 48.371, total 2.507.620. El total ya incluye las otras dos.

SUI anual. Pandas lee 130 filas porque el pie cae en las mismas columnas: `Año | 2021`, `Período | 25`, `Ubicación | Total`, `Departamento | ANTIOQUIA`, `Empresa | EMPRESAS PÚBLICAS DE MEDELLIN E.S.P.`, `Reporte a Consultar | Suscriptores`. El script se queda con las filas cuyo departamento es `ANTIOQUIA`: 123 municipios. Medellín: estratos 129.315, 307.598, 258.602, 102.812, 73.005 y 39.254. Residencial 910.586. Industrial 7.200, comercial 76.833, oficial 1.848, otros 526. La suma es 996.993. Hay 75 celdas `ND`. El código no viene. El nombre a veces no trae tilde. El período 25 es el anual.

Tarifas. El precio llega con `$` y coma decimal. Enero 2021, estrato 1, `Rango > CS`, Monomia, nivel I, Propiedad Epm: `$573,05`. De 2021, Monomia, nivel I, hay 228 filas. Una fila no trae año ni precio: `Monomia`, `Costo Unitario`, `Costo compra: Gm, i`, nivel I. No entra. La tarifa no tiene municipio.

## Lo que se ve y no entra

Clima 2024. Misma forma que el de 2021 y el mismo punto de grilla. Va de `2024-01-01T00:00` a `2024-01-07T23:00`, 168 horas. El corte es 2021.

SUI de enero, Total. Una fila de Medellín. Residencial 889.541, industrial 7.110, comercial 75.571, oficial 1.814, otros 516. Juntos son 974.552 suscriptores. El pie dice período 1 y ubicación Total. No es el anual de 996.993.

SUI de enero, Urbano. Otra fila. Residencial 868.232, industrial 6.948, comercial 75.010, oficial 1.686, otros 511. El pie dice ubicación Urbano. Ya está dentro del Total de enero. No se suma con ese archivo ni con el anual.

Facturación. 200 facturas de `CODENSA S.A. ESP`, código de empresa 2103, año 2021, período 7. No hay `cod_divipola`. Ocho columnas llegan vacías en las 200 filas, entre ellas `car_t1743_cons_cdc`, `val_fact_cdc` y `fch_publ_tarifa_apl`. Ese kWh no se suma con el medidor ni con la factura del corte.

Caracterización. 200 filas de `EMPRESAS MUNICIPALES DE CALI E.I.C.E E.S.P`, código 2438. El nombre llega con espacios de más entre CALI y E.I.C.E. Año 2021, período 8. Los municipios, por nombre, son Cali, Puerto Tejada y Yumbo, en Valle del Cauca y Cauca. `car_t1732_dane_niu` trae códigos de ocho dígitos, por ejemplo `76001000`, no el `cod_divipola` de cinco. Siete columnas de autogeneración llegan vacías en las 200 filas. `comercializador` está vacío en 7.

Polígono. 1.122 municipios. El código está en `mpio_cdpmp`. Medellín es un solo anillo de 8.429 vértices, nombre `MEDELLÍN`. Los 200 equipos ya se generaron dentro de ese anillo. El consumo no vuelve a leer el shapefile.
