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
