-- Carga el modelo limpio y el consumo generado.
-- Se corre dentro del contenedor, con los CSV montados en /datos.

\set ON_ERROR_STOP on
SET search_path TO makaia;

CREATE TEMP TABLE geo_raw (
    cod_departamento text,
    departamento text,
    cod_divipola text,
    nombre text,
    tipo_municipio text,
    longitud text,
    latitud text
);
\copy geo_raw FROM '/datos/modelo/geografia.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO geografia (cod_divipola, nombre, departamento, tipo_municipio, latitud, longitud)
SELECT cod_divipola, nombre, departamento, tipo_municipio, latitud::double precision, longitud::double precision
FROM geo_raw;

\copy tiempo FROM '/datos/modelo/tiempo.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

CREATE TEMP TABLE cliente_raw (
    cliente_id text,
    cod_divipola text,
    tipo_cliente text,
    estrato text,
    estado text
);
\copy cliente_raw FROM '/datos/modelo/cliente.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO cliente (cliente_id, cod_divipola, tipo_cliente, estrato, estado)
SELECT cliente_id, cod_divipola, tipo_cliente, NULLIF(estrato, '')::smallint, estado
FROM cliente_raw;

\copy activo FROM '/datos/modelo/activo.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy clima FROM '/datos/modelo/clima.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy consumo FROM '/datos/operacion/04-consumo.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy factura FROM '/datos/modelo/factura.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

CREATE TEMP TABLE falla_raw (
    incidente_id text,
    infraestructura_id text,
    fecha_hora text,
    clientes_afectados text,
    duracion_minutos text,
    periodo text
);
\copy falla_raw FROM '/datos/modelo/falla.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO falla (incidente_id, infraestructura_id, fecha_hora, clientes_afectados, duracion_minutos)
SELECT incidente_id, infraestructura_id, fecha_hora::timestamp, clientes_afectados::integer, duracion_minutos::integer
FROM falla_raw;

CREATE TEMP TABLE mantenimiento_raw (
    mantenimiento_id text,
    infraestructura_id text,
    fecha text,
    tipo text,
    costo text,
    periodo text
);
\copy mantenimiento_raw FROM '/datos/modelo/mantenimiento.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO mantenimiento (mantenimiento_id, infraestructura_id, fecha, tipo, costo)
SELECT mantenimiento_id, infraestructura_id, fecha::date, tipo, costo::numeric
FROM mantenimiento_raw;

CREATE TEMP TABLE poblacion_raw (
    cod_divipola text,
    anio text,
    area text,
    habitantes text,
    incluido_en_total text
);
\copy poblacion_raw FROM '/datos/modelo/poblacion.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO poblacion (cod_divipola, anio, area, habitantes)
SELECT cod_divipola, anio::smallint, area, habitantes::integer
FROM poblacion_raw;

CREATE TEMP TABLE sui_raw (
    cod_divipola text,
    nombre_publicado text,
    anio text,
    periodo text,
    ubicacion text,
    empresa text,
    estrato_1 text,
    estrato_2 text,
    estrato_3 text,
    estrato_4 text,
    estrato_5 text,
    estrato_6 text,
    total_residencial text,
    industrial text,
    comercial text,
    oficial text,
    otros text,
    total_no_residencial text
);
\copy sui_raw FROM '/datos/modelo/sui.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO sui (
    cod_divipola, anio, periodo, ubicacion, empresa,
    estrato_1, estrato_2, estrato_3, estrato_4, estrato_5, estrato_6,
    total_residencial, industrial, comercial, oficial, otros, total_no_residencial
)
SELECT
    cod_divipola, anio::smallint, periodo::smallint, ubicacion, empresa,
    NULLIF(estrato_1, '')::numeric::integer,
    NULLIF(estrato_2, '')::numeric::integer,
    NULLIF(estrato_3, '')::numeric::integer,
    NULLIF(estrato_4, '')::numeric::integer,
    NULLIF(estrato_5, '')::numeric::integer,
    NULLIF(estrato_6, '')::numeric::integer,
    NULLIF(total_residencial, '')::numeric::integer,
    NULLIF(industrial, '')::numeric::integer,
    NULLIF(comercial, '')::numeric::integer,
    NULLIF(oficial, '')::numeric::integer,
    NULLIF(otros, '')::numeric::integer,
    NULLIF(total_no_residencial, '')::numeric::integer
FROM sui_raw;

CREATE TEMP TABLE tarifa_raw (
    anio text,
    mes text,
    precio_propiedad_epm text,
    tipo_informacion text,
    tipo_tarifa text,
    tipo_dato text,
    rango_consumo text,
    nivel text
);
\copy tarifa_raw FROM '/datos/modelo/tarifa.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
INSERT INTO tarifa (
    anio, mes, tipo_informacion, tipo_tarifa, tipo_dato, rango_consumo, nivel, precio_propiedad_epm
)
SELECT
    anio::smallint, mes::smallint, tipo_informacion, tipo_tarifa, tipo_dato, rango_consumo, nivel,
    precio_propiedad_epm::numeric
FROM tarifa_raw;

SELECT 'geografia' AS tabla, count(*) FROM geografia
UNION ALL SELECT 'tiempo', count(*) FROM tiempo
UNION ALL SELECT 'cliente', count(*) FROM cliente
UNION ALL SELECT 'activo', count(*) FROM activo
UNION ALL SELECT 'clima', count(*) FROM clima
UNION ALL SELECT 'consumo', count(*) FROM consumo
UNION ALL SELECT 'factura', count(*) FROM factura
UNION ALL SELECT 'falla', count(*) FROM falla
UNION ALL SELECT 'mantenimiento', count(*) FROM mantenimiento
UNION ALL SELECT 'poblacion', count(*) FROM poblacion
UNION ALL SELECT 'sui', count(*) FROM sui
UNION ALL SELECT 'tarifa', count(*) FROM tarifa
ORDER BY tabla;
