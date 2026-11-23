-- Tablas vacías del corte. No inserta datos.
-- PostgreSQL. Si el esquema makaia ya existe, lo borra y lo crea de nuevo.

DROP SCHEMA IF EXISTS makaia CASCADE;
CREATE SCHEMA makaia;

SET search_path TO makaia;

CREATE TABLE geografia (
    cod_divipola    char(5) PRIMARY KEY,
    nombre          text NOT NULL,
    departamento    text NOT NULL,
    tipo_municipio  text,
    latitud         double precision,
    longitud        double precision
);

CREATE TABLE tiempo (
    fecha_hora  timestamp PRIMARY KEY,
    fecha       date NOT NULL,
    hora        smallint NOT NULL,
    mes         smallint NOT NULL,
    anio        smallint NOT NULL,
    periodo     char(7) NOT NULL
);

CREATE TABLE cliente (
    cliente_id    varchar(10) PRIMARY KEY,
    cod_divipola  char(5) NOT NULL REFERENCES geografia (cod_divipola),
    tipo_cliente  text NOT NULL,
    estrato       smallint,
    estado        text NOT NULL
);

CREATE TABLE activo (
    infraestructura_id  varchar(10) PRIMARY KEY,
    cod_divipola        char(5) NOT NULL REFERENCES geografia (cod_divipola),
    tipo                text NOT NULL,
    latitud             double precision NOT NULL,
    longitud            double precision NOT NULL,
    fecha_instalacion   date NOT NULL,
    estado              text NOT NULL
);

CREATE TABLE clima (
    cod_divipola      char(5) NOT NULL REFERENCES geografia (cod_divipola),
    fecha_hora        timestamp NOT NULL REFERENCES tiempo (fecha_hora),
    precipitacion_mm  double precision NOT NULL,
    temperatura_2m    double precision NOT NULL,
    humedad_relativa  double precision,
    viento_kmh        double precision,
    presion_hpa       double precision,
    PRIMARY KEY (cod_divipola, fecha_hora)
);

CREATE TABLE consumo (
    cliente_id   varchar(10) NOT NULL REFERENCES cliente (cliente_id),
    fecha_hora   timestamp NOT NULL REFERENCES tiempo (fecha_hora),
    consumo_kwh  numeric(14, 4) NOT NULL,
    PRIMARY KEY (cliente_id, fecha_hora)
);

CREATE TABLE factura (
    cliente_id       varchar(10) NOT NULL REFERENCES cliente (cliente_id),
    periodo          char(7) NOT NULL,
    consumo_kwh_mes  numeric(14, 4) NOT NULL,
    valor_facturado  numeric(16, 2) NOT NULL,
    tarifa           numeric(12, 2) NOT NULL,
    estado_pago      text NOT NULL,
    PRIMARY KEY (cliente_id, periodo)
);

CREATE TABLE falla (
    incidente_id        varchar(10) PRIMARY KEY,
    infraestructura_id  varchar(10) NOT NULL REFERENCES activo (infraestructura_id),
    fecha_hora          timestamp NOT NULL REFERENCES tiempo (fecha_hora),
    clientes_afectados  integer NOT NULL,
    duracion_minutos    integer NOT NULL
);

CREATE TABLE mantenimiento (
    mantenimiento_id    varchar(10) PRIMARY KEY,
    infraestructura_id  varchar(10) NOT NULL REFERENCES activo (infraestructura_id),
    fecha               date NOT NULL,
    tipo                text NOT NULL,
    costo               numeric(14, 2) NOT NULL
);

CREATE TABLE poblacion (
    cod_divipola  char(5) NOT NULL REFERENCES geografia (cod_divipola),
    anio          smallint NOT NULL,
    area          text NOT NULL,
    habitantes    integer NOT NULL,
    PRIMARY KEY (cod_divipola, anio, area)
);

CREATE TABLE sui (
    cod_divipola          char(5) NOT NULL REFERENCES geografia (cod_divipola),
    anio                  smallint NOT NULL,
    periodo               smallint NOT NULL,
    ubicacion             text NOT NULL,
    empresa               text NOT NULL,
    estrato_1             integer,
    estrato_2             integer,
    estrato_3             integer,
    estrato_4             integer,
    estrato_5             integer,
    estrato_6             integer,
    total_residencial     integer,
    industrial            integer,
    comercial             integer,
    oficial               integer,
    otros                 integer,
    total_no_residencial  integer,
    PRIMARY KEY (cod_divipola, anio, periodo, ubicacion, empresa)
);

CREATE TABLE tarifa (
    anio                      smallint NOT NULL,
    mes                       smallint NOT NULL,
    tipo_informacion          text NOT NULL,
    tipo_tarifa               text NOT NULL,
    tipo_dato                 text NOT NULL,
    rango_consumo             text NOT NULL,
    nivel                     text NOT NULL,
    precio_propiedad_epm      numeric(12, 2),
    precio_compartido         numeric(12, 2),
    precio_propiedad_cliente  numeric(12, 2),
    precio_punta              numeric(12, 2),
    precio_fuera_punta        numeric(12, 2),
    PRIMARY KEY (anio, mes, tipo_informacion, tipo_tarifa, tipo_dato, rango_consumo, nivel)
);
