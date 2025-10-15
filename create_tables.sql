-- Create the operador_operaciones_diarios table
CREATE TABLE sgto_matriz_operadores_dias (
    id SERIAL PRIMARY KEY,
    "Operador" TEXT,
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
