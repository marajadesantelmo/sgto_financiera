-- Create the operador_operaciones_diarios table
CREATE TABLE sgto_matriz_operadores_dias (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "BS AS" NUMERIC,
    "CA" NUMERIC,
    "EP" NUMERIC,
    "FB" NUMERIC,
    "MT" NUMERIC,
    "NP" NUMERIC,
    "TDLA" NUMERIC,
    "Total" NUMERIC
);

-- Create the operador_operaciones_diarios_tidy table
CREATE TABLE sgto_operaciones_operador_por_dia (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Operador" TEXT,
    "Cantidad Operaciones" NUMERIC
);

-- Create the sgto_montos_usd_tdc table
CREATE TABLE sgto_montos_usd_tdc (
    id SERIAL PRIMARY KEY,
    "Monto USD ayer" NUMERIC,
    "TdC ayer" NUMERIC,
    "Monto USD hoy" NUMERIC,
    "TdC hoy" NUMERIC
);
-- Create the log_entry table
CREATE TABLE log_entry (
    id SERIAL PRIMARY KEY,
    "Ultimo Update" TIMESTAMP
);

-- Create the tabla_datos table
CREATE TABLE sgto_tabla_datos (
    id SERIAL PRIMARY KEY,
    "CONCEPTO" TEXT,
    "HOY" NUMERIC,
    "ACUM MES" NUMERIC,
    "PROM x DIA" NUMERIC,
    "VAR MA" NUMERIC,
    "PROY MES" NUMERIC, 
    "VAR PROY" NUMERIC,
    "Obj" NUMERIC
);

-- Create the historico_caja table
CREATE TABLE sgto_historico_caja (
    id SERIAL PRIMARY KEY,
    "Fecha" DATE,
    "Total Caja" NUMERIC,
    "Ganancias" NUMERIC
);

CREATE TABLE sgto_tabla_tdc (
    id SERIAL PRIMARY KEY,
    "Fecha" DATE,
    "TC Prom" NUMERIC, 
    "TC_min" NUMERIC,
    "TC_max" NUMERIC
);