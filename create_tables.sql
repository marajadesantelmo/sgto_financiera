-- Create the operador_operaciones_diarios table
CREATE TABLE sgto_operador_operaciones_diarios (
    id SERIAL PRIMARY KEY,
    Operador VARCHAR(10),
    Fecha DATE,
    BS NUMERIC(10,1),
    "AS" NUMERIC(10,1),
    CA NUMERIC(10,1),
    EP NUMERIC(10,1),
    FB NUMERIC(10,1),
    MT NUMERIC(10,1),
    NP NUMERIC(10,1),
    TDLA NUMERIC(10,1),
    Total NUMERIC(10,1)
);

-- Create the operador_operaciones_diarios_tidy table
CREATE TABLE sgto_operador_operaciones_diarios_tidy (
    id SERIAL PRIMARY KEY,
    Fecha DATE,
    Operador VARCHAR(10),
    Cantidad_Operaciones INTEGER
);
