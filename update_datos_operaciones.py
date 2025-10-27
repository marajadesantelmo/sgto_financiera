import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase, sheet_operaciones_url, sheet_control_caja_url
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)
from datetime import datetime, timedelta

def convert_to_numeric(value):
    if isinstance(value, str):
        # Remove spaces, replace commas with dots (if European format)
        cleaned = value.strip().replace(' ', '')
        # Remove ",0" at the end if it exists
        if cleaned.endswith(',0'):
            cleaned = cleaned[:-2]
        # Handle negative values marked with dash in front or at end
        if cleaned.startswith('-'):
            cleaned = '-' + cleaned[1:].replace('.', '')
        elif cleaned.endswith('-'):
            cleaned = '-' + cleaned[:-1].replace('.', '')
        else:
            cleaned = cleaned.replace('.', '')
        # Try conversion
        try:
            return float(cleaned)
        except ValueError:
            return value
    return value


print("Iniciando actualización de datos de operaciones...")
if os.path.exists('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json'):
    gc = gspread.service_account('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json')
elif os.path.exists('credenciales_gsheets.json'):
    gc = gspread.service_account(filename='credenciales_gsheets.json')
#Operaciones
sheet_url = sheet_operaciones_url
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Operaciones Octubre 2025')
# Leer todo el rango una sola vez y procesar por posición de columna
all_rows = worksheet.get('A4:AY3961')  # único request

# Asegurar que todas las filas tengan la misma longitud (hasta AY -> 51 columnas: 0..50)
TARGET_COLS = 51
padded = [row + [''] * (TARGET_COLS - len(row)) if len(row) < TARGET_COLS else row[:TARGET_COLS] for row in all_rows]

# DataFrame con columnas por índice para seleccionar por posición
df_all = pd.DataFrame(padded, columns=list(range(TARGET_COLS)))

# Base general: Fecha(0), Operador(1), Cliente(2)
base = df_all[[0, 1, 2]].copy()
base.columns = ['Fecha', 'Operador', 'Cliente']

def make_single(col_idx, moneda, caja):
    df = pd.concat([base, df_all[[col_idx]].copy()], axis=1)
    df.columns = ['Fecha', 'Operador', 'Cliente', 'Monto']
    df = df.replace('', pd.NA).dropna(subset=['Monto']).copy()
    df['Moneda'] = moneda
    df['Caja'] = caja
    return df

def make_pair(col_idx_monto, col_idx_tc, moneda, caja):
    df = pd.concat([base, df_all[[col_idx_monto, col_idx_tc]].copy()], axis=1)
    df.columns = ['Fecha', 'Operador', 'Cliente', 'Monto', 'TC']
    df = df.replace('', pd.NA).dropna(subset=['Monto']).copy()
    df['Moneda'] = moneda
    df['Caja'] = caja
    return df

# Construir data2..data15 usando las posiciones originales
data2  = make_pair(5, 6,   'USD',          'Salta')              # F:G
data3  = make_single(10,    'Pesos',        'Salta')             # K
data4  = make_single(13,    'Transferencia','Salta')             # N
data5  = make_pair(16, 17,  'USD',          'Office Park')       # Q:R
data6  = make_single(21,    'Pesos',        'Office Park')       # V
data7  = make_single(24,    'Pesos',        'Office Park')       # Y
data8  = make_single(27,    'Euros',        'Office Park')       # AB
data9  = make_single(30,    'Euros',        'Salta')             # AE
data10 = make_single(33,    'USDT',         'Salta')             # AH
data11 = make_single(36,    'USD',          'Mindful')           # AK
data12 = make_pair(39, 40,  'USD',          'Reconquista CABA')   # AN:AO
data13 = make_single(44,    'Pesos',        'Reconquista CABA')   # AS
data14 = make_single(47,    'Transferencia','Reconquista CABA')   # AV
data15 = make_single(50,    'Euros',        'Reconquista CABA')   # AY

operaciones = pd.concat([data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12, data13, data14, data15], ignore_index=True)
operaciones['Cliente'] = operaciones['Cliente'].str.strip().str.title()
operaciones = operaciones[operaciones['Cliente'] != 'Apertura De Caja Octubre']
operaciones = operaciones[operaciones['Cliente'] != "Movimiento De Caja"].copy()    # Excluir movimientos de caja
operaciones.dropna(subset=['Fecha'], inplace=True)
operaciones.fillna("0", inplace=True)
numeric_columns = ['Monto', 'TC']
for col in numeric_columns:
    operaciones[col] = operaciones[col].apply(convert_to_numeric)

operaciones['Monto'] = pd.to_numeric(operaciones['Monto'], errors='coerce')
operaciones['TC'] = pd.to_numeric(operaciones['TC'], errors='coerce')

operaciones_usd = operaciones[operaciones['Moneda'] == 'USD'].copy()   

### Tablas de Clientes Mensual ###

operaciones_usd_por_cliente = operaciones_usd.groupby(['Cliente', 'Moneda']).agg({
    'Monto': ['count', lambda x: x.abs().sum()]
}).reset_index()

operaciones_usd_por_cliente.columns = ['Cliente', 'Moneda', 'Cantidad Operaciones', 'Monto operado en el mes']

operaciones_usd_por_cliente.sort_values(by='Monto operado en el mes', ascending=False, inplace=True)
operaciones_usd_por_cliente.reset_index(drop=True, inplace=True)
operaciones_usd_por_cliente = operaciones_usd_por_cliente[operaciones_usd_por_cliente['Monto operado en el mes'] != 0]
top_20_participacion_operaciones_usd_por_cliente = operaciones_usd_por_cliente.nlargest(20, 'Monto operado en el mes').copy()

# Calculate total amount for percentage calculation
total_monto = operaciones_usd_por_cliente['Monto operado en el mes'].sum()

# Add percentage column to top 20
top_20_participacion_operaciones_usd_por_cliente['Porcentaje'] = (top_20_participacion_operaciones_usd_por_cliente['Monto operado en el mes'] / total_monto * 100).round(2)

# Calculate "Otros" row
otros_monto = operaciones_usd_por_cliente.iloc[20:]['Monto operado en el mes'].sum()
otros_cantidad = operaciones_usd_por_cliente.iloc[20:]['Cantidad Operaciones'].sum()
otros_porcentaje = (otros_monto / total_monto * 100).round(2)

# Create "Otros" row
otros_row = pd.DataFrame({
    'Cliente': ['Otros'],
    'Moneda': ['USD'],
    'Cantidad Operaciones': [otros_cantidad],
    'Monto operado en el mes': [otros_monto],
    'Porcentaje': [otros_porcentaje]
})

# Concatenate top 20 with "Otros" row
top_20_participacion_operaciones_usd_por_cliente = pd.concat([top_20_participacion_operaciones_usd_por_cliente, otros_row], ignore_index=True)

### Tabla de operaciones por operador y dia ###

operaciones_operador_por_dia = operaciones.groupby(['Fecha', 'Operador']).size().reset_index(name='Cantidad Operaciones')
operador_operaciones_pivot = operaciones_operador_por_dia.pivot_table(
    index='Fecha', 
    columns='Operador', 
    values='Cantidad Operaciones', 
    fill_value=0
)
operador_operaciones_pivot['Total'] = operador_operaciones_pivot.sum(axis=1)
sgto_matriz_operadores_dias = operador_operaciones_pivot.reset_index()
# Filter out rows with empty or invalid dates
sgto_matriz_operadores_dias.drop(columns=['', '0'], inplace=True, errors='ignore')
sgto_matriz_operadores_dias = sgto_matriz_operadores_dias[sgto_matriz_operadores_dias['Fecha'].str.strip() != ''].copy()
sgto_matriz_operadores_dias['Fecha'] = pd.to_datetime(sgto_matriz_operadores_dias['Fecha'], format='%d/%m/%Y')
sgto_matriz_operadores_dias = sgto_matriz_operadores_dias.sort_values('Fecha')
sgto_matriz_operadores_dias['Fecha'] = sgto_matriz_operadores_dias['Fecha'].dt.strftime('%d/%m/%Y')


### Tabla de tipo de cambio y montos operados para operaciones en USD ###

operaciones_usd.loc[:, 'Monto'] = operaciones_usd['Monto'].abs()
operaciones_usd['MontoxTC'] = operaciones_usd['Monto'] * operaciones_usd['TC']
tabla_monto_operado = operaciones_usd.groupby('Fecha').agg({
    'Monto': 'sum'
}).reset_index()

operaciones_usd_tdc_clean = operaciones_usd[operaciones_usd['TC'] > 1000].copy()   # Filtrar operaciones con TC válido # Qué hacer con los casos donde TC es NaN??

tabla_tipo_de_cambio_por_dia = operaciones_usd_tdc_clean.groupby('Fecha').agg({         
    'Monto': 'sum',    
    'MontoxTC': 'sum'
}).reset_index()

tabla_tipo_de_cambio_por_dia['TC Prom'] = tabla_tipo_de_cambio_por_dia['MontoxTC'] / tabla_tipo_de_cambio_por_dia['Monto']
tabla_tipo_de_cambio_por_dia = tabla_tipo_de_cambio_por_dia[['Fecha', 'TC Prom']]

# Calculo de tipo de cambio maximo y minimo por dia
sgto_montos_usd_tdc = operaciones_usd_tdc_clean.groupby('Fecha').agg({
    'TC': ['min', 'max']
}).reset_index()

# Reset multi-index and rename columns before merging
sgto_montos_usd_tdc_flat = sgto_montos_usd_tdc.copy()
sgto_montos_usd_tdc_flat.columns = ['Fecha', 'TC_min', 'TC_max']
tabla_tdc = tabla_tipo_de_cambio_por_dia[['Fecha', 'TC Prom']].merge(
    sgto_montos_usd_tdc_flat,
    on='Fecha',
    how='left'
)

tabla_tdc = tabla_tdc.merge(
    tabla_monto_operado,
    on='Fecha',
    how='left'
)

tabla_tdc['Fecha'] = pd.to_datetime(tabla_tdc['Fecha'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

#### Cálculo de métricas principales ###

# Get yesterday's date in YYYY-MM-DD format to match tabla_tdc
ayer = pd.to_datetime("today") - pd.Timedelta(days=1)
ayer_formatted = ayer.strftime('%Y-%m-%d')

# Get today's date in YYYY-MM-DD format to match tabla_tdc
hoy = pd.to_datetime("today")
hoy_formatted = hoy.strftime('%Y-%m-%d')

# Get metrics from tabla_tdc for yesterday
if ayer_formatted in tabla_tdc['Fecha'].values:
    ayer_data = tabla_tdc[tabla_tdc['Fecha'] == ayer_formatted].iloc[0]
    monto_usd_ayer = ayer_data['Monto']
    tdc_ayer = ayer_data['TC Prom']
else:
    monto_usd_ayer = 0
    tdc_ayer = 0

# Get metrics from tabla_tdc for today
if hoy_formatted in tabla_tdc['Fecha'].values:
    hoy_data = tabla_tdc[tabla_tdc['Fecha'] == hoy_formatted].iloc[0]
    monto_usd_hoy = hoy_data['Monto']
    tdc_hoy = hoy_data['TC Prom']
else:
    monto_usd_hoy = 0
    tdc_hoy = 0

metricas_df = pd.DataFrame([{
    'Monto USD ayer': monto_usd_ayer,
    'TdC ayer': tdc_ayer,
    'Monto USD hoy': monto_usd_hoy,
    'TdC hoy': tdc_hoy
}])






#### Control Caja ####
sheet_url = sheet_control_caja_url
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Control caja')
fechas_caja = worksheet.get('AP2:BV2')
total_caja = worksheet.get('AP49:BV49')
ganancias = worksheet.get('AP50:BV50')


data_fechas = pd.DataFrame(fechas_caja).transpose()
data_total_caja = pd.DataFrame(total_caja).transpose()
data_ganancias = pd.DataFrame(ganancias).transpose()
data_fechas.columns = ['Fecha']
data_total_caja.columns = ['Total Caja']
data_ganancias.columns = ['Ganancias']
df = pd.concat([data_fechas, data_total_caja, data_ganancias], axis=1)

# Convert 'Fecha' column to standard format dd/mm/yyyy
df['Fecha'] = df['Fecha'].apply(lambda x: x.strip() if isinstance(x, str) else x)  # Remove whitespace if any

# Process dates
def standardize_date(date_str):
    if not isinstance(date_str, str):
        return date_str
    
    # Split by '/' if present
    parts = date_str.split('/')
    
    if len(parts) == 2:
        day, month = parts
    else:
        # Assuming format like '01/09'
        day = date_str[:2] if len(date_str) >= 2 else date_str
        month = date_str[3:5] if len(date_str) >= 5 else ""
        
    # Ensure day has two digits
    if len(day.strip()) == 1:
        day = f"0{day.strip()}"
    else:
        day = day.strip()
        
    # Ensure month has two digits
    if len(month.strip()) == 1:
        month = f"0{month.strip()}"
    else:
        month = month.strip()
        
    return f"2025-{month}-{day}"

df['Fecha'] = df['Fecha'].apply(standardize_date)

# Convert 'Total Caja' and 'Ganancias' to numeric, removing dots used as thousands separators
df['Total Caja'] = df['Total Caja'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(int)
df['Ganancias'] = df['Ganancias'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(int)

sheet= gc.open('Datos Financiera')
seguimiento_worksheet = sheet.worksheet('Seguimiento')


# Get the last value of Total Caja column
last_total_caja = df['Total Caja'].iloc[-1].astype(int).astype(str)
variacion = (df['Total Caja'].iloc[-1] - df['Total Caja'].iloc[0]) / df['Total Caja'].iloc[0]
variacion = variacion.round(4).astype(str)

metricas_worksheet = sheet.worksheet('Metricas')
metricas_worksheet.update( [[last_total_caja]], 'A2')
metricas_worksheet.update([[variacion]], 'B2')
### Tablita 

tabla = worksheet.get('AJ62:AR66')
# Create DataFrame from the tabla data
df_tabla = pd.DataFrame(tabla)

df_tabla.columns = df_tabla.iloc[0]
df_tabla = df_tabla.drop(0)
df_tabla = df_tabla.reset_index(drop=True)
df_tabla.columns = ['CONCEPTO', '', 'HOY', 'ACUM MES', 'PROM x DIA', 'VAR MA', 'PROY MES', 'VAR PROY', 'Obj'] #Cambio nombre a columna duplicada
df_tabla = df_tabla.drop(columns=[''])  # Drop the empty column
df_tabla['HOY'] = df_tabla['HOY'].str.replace('.', '', regex=False)
df_tabla['ACUM MES'] = df_tabla['ACUM MES'].str.replace('.', '', regex=False)
df_tabla['PROM x DIA'] = df_tabla['PROM x DIA'].str.replace('.', '', regex=False)
df_tabla['VAR MA'] = df_tabla['VAR MA'].str.replace('%', '', regex=False)
df_tabla['PROY MES'] = df_tabla['PROY MES'].str.replace('.', '', regex=False)
df_tabla['VAR PROY'] = df_tabla['VAR PROY'].str.replace('%', '', regex=False)
df_tabla['Obj'] = df_tabla['Obj'].str.replace('.', '', regex=False)
df_tabla['CONCEPTO'] = df_tabla['CONCEPTO'].str.strip() 
# Convert numeric columns to integers
numeric_columns = ['HOY', 'ACUM MES', 'PROM x DIA', 'PROY MES', 'Obj']
for col in numeric_columns:
    df_tabla[col] = pd.to_numeric(df_tabla[col], errors='coerce').fillna(0).astype(int)

# Convert percentage columns to float and divide by 100
percentage_columns = ['VAR MA', 'VAR PROY']
for col in percentage_columns:
    df_tabla[col] = pd.to_numeric(df_tabla[col], errors='coerce').fillna(0) / 100



#### Carga de datos en supabase ####
print("Datos procesados, actualizando base de datos...")

def insert_table_data(table_name, data):
    for record in data:
        try:
            supabase_client.from_(table_name).insert(record).execute()
        except Exception as e:
            print(f"Error inserting record into {table_name}: {e}")

def update_log():
    log_entry = {
        "Ultimo Update": datetime.now().isoformat()
    }
    supabase_client.table('sgto_log_entry').delete().neq('id', 0).execute()
    supabase_client.from_("sgto_log_entry").insert(log_entry).execute()

try:
    supabase_client.table('sgto_montos_usd_tdc').delete().neq('id', 0).execute()
    insert_table_data('sgto_montos_usd_tdc', metricas_df.to_dict(orient='records'))
    print("Métricas principales actualizadas.")
except Exception as e:
    print(f"Error updating sgto_montos_usd_tdc: {e}")

try:
    supabase_client.table('sgto_matriz_operadores_dias').delete().neq('id', 0).execute()
    insert_table_data('sgto_matriz_operadores_dias', sgto_matriz_operadores_dias.to_dict(orient='records'))
    print("Métricas de operadores por día actualizadas.")
except Exception as e:
    print(f"Error updating sgto_matriz_operadores_dias: {e}")

try:
    supabase_client.table('sgto_operaciones_operador_por_dia').delete().neq('id', 0).execute()
    insert_table_data('sgto_operaciones_operador_por_dia', operaciones_operador_por_dia.to_dict(orient='records'))
except Exception as e:
    print(f"Error updating sgto_operaciones_operador_por_dia: {e}")

try:
    supabase_client.table('sgto_tabla_datos').delete().neq('id', 0).execute()
    insert_table_data('sgto_tabla_datos', df_tabla.to_dict(orient='records'))
except Exception as e:
    print(f"Error updating sgto_tabla_datos: {e}")

try:
    supabase_client.table('sgto_historico_caja').delete().neq('id', 0).execute()
    insert_table_data('sgto_historico_caja', df.to_dict(orient='records'))
    print("Métricas de histórico de caja actualizadas.")
except Exception as e:
    print(f"Error updating sgto_historico_caja: {e}")

try:
    supabase_client.table('sgto_tabla_tdc').delete().neq('id', 0).execute()
    insert_table_data('sgto_tabla_tdc', tabla_tdc.to_dict(orient='records'))
except Exception as e:
    print(f"Error updating sgto_tabla_tdc: {e}")

try:
    supabase_client.table('sgto_operaciones_usd_por_cliente').delete().neq('id', 0).execute()
    insert_table_data('sgto_operaciones_usd_por_cliente', operaciones_usd_por_cliente.to_dict(orient='records'))
    print("Métricas de operaciones USD por cliente actualizadas.")
except Exception as e:
    print(f"Error updating sgto_operaciones_usd_por_cliente: {e}")

try:
    supabase_client.table('sgto_top_20_participacion_operaciones_usd_por_cliente').delete().neq('id', 0).execute()
    insert_table_data('sgto_top_20_participacion_operaciones_usd_por_cliente', top_20_participacion_operaciones_usd_por_cliente.to_dict(orient='records'))
except Exception as e:
    print(f"Error updating sgto_top_20_participacion_operaciones_usd_por_cliente: {e}")

##### SECCION HISTORICO
from datetime import timedelta
#Operaciones
sheet_url = 'https://docs.google.com/spreadsheets/d/1g3A6eKSYV7rZ0LHDv0JIMCwDt0LSPYyqO0Lncri2fxI'
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Sgto')

#Datos generales
columns1 = ['Ano', 'Dia', 'Mes', 'Operador', 'Categoria', 'Cliente', 'Categoria', 'libre1', 'Monto', 'TC']
data_range1 = worksheet.get('B43429:K71547')
data1 = pd.DataFrame(data_range1, columns=columns1)
data1['Fecha'] = pd.to_datetime(data1[['Ano', 'Mes', 'Dia']].astype(int).astype(str).agg('-'.join, axis=1), errors='coerce')
data1 = data1.drop(columns=['Ano', 'Dia', 'Mes'])

data2 = data1[['Fecha', 'Operador', 'Cliente', 'Monto', 'TC']].copy()

# Convert Monto and TC to numeric values
data2 = data2.dropna(subset=['Monto'])
data2['Monto'] = data2['Monto'].apply(convert_to_numeric)
data2['TC'] = data2['TC'].apply(convert_to_numeric)

# Ensure consistent date formatting for both DataFrames
data2['Fecha'] = pd.to_datetime(data2['Fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
operaciones_usd['Fecha'] = pd.to_datetime(operaciones_usd['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

# Ensure consistent data types
data2['Monto'] = pd.to_numeric(data2['Monto'], errors='coerce')
data2['TC'] = pd.to_numeric(data2['TC'], errors='coerce')

# Add missing columns to data2 to match operaciones_usd structure
data2['Moneda'] = 'USD'
data2['Caja'] = 'Historical'
data2['MontoxTC'] = data2['Monto'] * data2['TC']
operaciones_usd_historico = pd.concat([data2, operaciones_usd], ignore_index=True)

# Group by Cliente and calculate the required metrics
operaciones_por_cliente_historico = operaciones_usd_historico.groupby('Cliente').agg({
    'Monto': lambda x: abs(pd.to_numeric(x, errors='coerce')).sum(),
    'TC': lambda x: pd.to_numeric(x, errors='coerce').replace(0, None).mean(),
    'Fecha': 'max' 
}).rename(columns={
    'Monto': 'Monto total operado',
    'TC': 'TC prom',
    'Fecha': 'Ultima fecha'
}).sort_values(by='Monto total operado', ascending=False).reset_index()

# Calculate the status based on the most recent operation date

today = datetime.now()
two_months_ago = today - timedelta(days=60)
six_months_ago = today - timedelta(days=180)

def classify_client_status(last_date):
    if pd.isna(last_date):
        return "Perdido"
    
    # Convert string date to datetime for comparison
    last_date_dt = pd.to_datetime(last_date, errors='coerce')
    if pd.isna(last_date_dt):
        return "Perdido"
    
    if last_date_dt >= two_months_ago:
        return "Activo"
    elif last_date_dt >= six_months_ago:
        return "Inactivo"
    else:
        return "Perdido"

operaciones_por_cliente_historico['Tipo'] = operaciones_por_cliente_historico['Ultima fecha'].apply(classify_client_status)

operaciones_por_cliente_historico = operaciones_por_cliente_historico.fillna({'TC prom': 0})

try: 
    supabase_client.from_('sgto_operaciones_por_cliente_historico').delete().neq('id', 0).execute()
    # Replace NaN values with None before converting to dict
    supabase_client.from_('sgto_operaciones_por_cliente_historico').insert(operaciones_por_cliente_historico.to_dict(orient='records')).execute()
except Exception as e:
    print(f"Error updating supabase table: {e}")



update_log()

print("Actualización completada.")