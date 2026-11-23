# EDA local, antes de Databricks

Cada archivo del corte se volvió a leer en esta máquina, sin transformarlo. Los scripts de las muestras públicas quedaron en pandas y leen `/Volumes/main/default/Muestras/` cuando ese volumen existe. Lo que esa corrida encontró está en [09-eda-pandas.md](09-eda-pandas.md). Este documento guarda la ficha del cajón A, que no se volvió a leer.

En Databricks los mismos archivos están en `/Volumes/main/default/Muestras/`. El paso siguiente es el ETL. El grano no cambia por cambiar de motor.

Desde `eda/`:

```text
python divipola.py
python clima.py
python poblacion.py
python sui.py
python tarifas.py
python tiempo.py
python cliente.py
python activo.py
python consumo.py
python factura.py
python falla.py
python mantenimiento.py
```

`poblacion.py` usa openpyxl. `consumo.py` y `factura.py` recorren las 8.760.000 horas de una en una.

No hay script para el polígono ni para los archivos que se quedan fuera. El polígono ya se usó al generar los equipos. El clima de 2024, el SUI de enero, el urbano, Codensa y Cali no entran al corte.

## Qué confirmó la corrida

| Archivo | Filas | Grano | Código |
|---|---|---|---|
| DIVIPOLA | 1.122 municipios, 125 de Antioquia | un municipio | `Código Municipio`. Medellín `05001` |
| Clima 2021 | 8.760 horas, `2021-01-01T00:00` a `2021-12-31T23:00` | una hora de la cabecera | no viene. Al cargar se escribe `05001` |
| Población | 84.225 filas de datos en `PobMunicipalxÁrea` | municipio, año y área | `MPIO` |
| SUI | 123 municipios | municipio, suscriptores EPM, año 2021, ubicación Total | no viene. Solo el nombre |
| Tarifas | 3.623 filas, años 2016 a 2021 | un precio, un mes, un tipo y un nivel | no viene |
| Tiempo | 8.760 horas | una hora de 2021 | no aplica |
| Cliente | 1.000 | un cliente de la muestra | `cod_divipola` = `05001` en las 1.000 |
| Activo | 200 | un equipo | `05001` en los 200. Estado `en servicio` |
| Consumo | 8.760.000 | un cliente y una hora | no trae municipio |
| Factura | 12.000 | un cliente y un mes | no se une a la hora |
| Falla | 522 | un evento, un equipo, una hora | no trae lluvia |
| Mantenimiento | 428 | un trabajo, un equipo, una fecha | no se une a un cliente |

La prueba de cierre, cliente `C0001`, enero de 2021:

| Prueba | Resultado |
|---|---|
| Horas | 744 |
| Suma del medidor | 145,9701 kWh |
| `consumo_kwh_mes` de la factura | 145,9701 kWh |
| ¿Coinciden? | sí |
| Tarifa | 573,05 |
| Valor | 83.648,17. Estado pagada |

Las 12.000 facturas quedan así: 9.895 pagadas, 1.274 pendientes, 831 en mora.

## Lo que el lector tiene que cuidar

DIVIPOLA. La columna de tipo no se llama `Tipo`. Se llama `Tipo: Municipio / Isla / Área no municipalizada`. La latitud de Medellín es `6,246631` y la longitud `-75,581775`, con coma decimal. El nombre es `MEDELLÍN`.

Clima. El punto del JSON es latitud 6,2214413 y longitud -75,55185, elevación 1.475, zona `America/Bogota`. No es la coordenada de la cabecera del DIVIPOLA: es el cruce de grilla de Open-Meteo. Las 8.760 horas traen dato de lluvia. Ninguna hora viene vacía.

Población. La hoja trae tres filas de título antes de `DP, DPNOM, MPIO, DPMP, AÑO, ÁREA GEOGRÁFICA, TOTAL`. Excel guarda `05001` como número, así que al leer hay que reponer el cero. Medellín, 2021: cabecera 2.459.249, resto 48.371, total 2.507.620. Esas dos primeras ya están dentro del total.

SUI. El archivo es cp1252. Tiene 123 municipios y, debajo, un pie de seis líneas: año 2021, período 25, ubicación Total, ANTIOQUIA, EPM, Suscriptores. Si esas líneas se cuentan como municipios, salen 129. No lo son. El período 25 es el anual. Medellín: estratos 129.315, 307.598, 258.602, 102.812, 73.005 y 39.254. Residencial 910.586. Industrial 7.200, comercial 76.833, oficial 1.848, otros 526. La suma es 996.993. Hay 75 celdas `ND`. El nombre a veces no trae tilde, y el código no viene: se traduce una vez contra DIVIPOLA y después se cruza por `cod_divipola`.

Tarifas. Hay una fila sin año y sin precio: `Monomia`, `Costo Unitario`, `Costo compra: Gm, i`, nivel I. No entra. La fila del corte sí está: enero 2021, estrato 1, `Rango > CS`, Monomia, nivel I, Propiedad Epm, 573,05. De 2021, con ese tipo y ese nivel, hay 228 filas.

Cajón A. La mezcla de los 1.000 clientes es estrato 1, 130; 2, 309; 3, 259; 4, 103; 5, 73; 6, 39; comercial 77; industrial 7; oficial 2; otros 1. Los equipos son 90 postes, 50 transformadores, 35 líneas, 20 protecciones y 5 subestaciones. El ejemplo `A0001` está en 6,304471 y -75,588159, instalado el 2015-12-23. Las fallas suman 83.087 clientes alcanzados y 52.438 minutos, sobre 178 equipos. `F00001` es el equipo `A0001`, el 2021-03-03 a la 01:00, 38 clientes, 129 minutos, y la fila no tiene lluvia. Los mantenimientos son 200 preventivos (132.903.211 pesos) y 228 correctivos (293.776.172 pesos), sobre los 200 equipos.

El consumo no se suma con la factura. La factura de enero ya es la suma de esas 744 horas.
