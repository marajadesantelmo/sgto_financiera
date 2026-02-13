import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase, sheet_operaciones_url, sheet_control_caja_url
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
import numpy as np

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
#sheet_url = sheet_operaciones_url
sheet_url = 'https://docs.google.com/spreadsheets/d/15r3kWfDsgK84Uf5u0qap8Etcf9NpZA-lzSNv67uhYLk'
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Sgto')
header = worksheet.get('B4:AY4')[0]  
all_rows = worksheet.get('B43428:AY97154') 


base = pd.DataFrame(all_rows, columns=header)
base.columns = ['Año', 'mes', 'dia', 'Operador', 'Categoria', 'Cliente', 'Descripcion', 'libre1', 'Mov'] + header[9:].copy()
base.drop(columns=['libre1'], inplace=True)
base = base.replace('', pd.NA)
base = base.dropna(subset=['Año', 'mes', 'dia'])
base['Fecha'] = pd.to_datetime(base[['Año', 'dia', 'mes']].astype(int).astype(str).agg('-'.join, axis=1), errors='coerce').dt.strftime('%Y-%m-%d')
base = base.drop(columns=['Año', 'dia', 'mes'])
base = base.dropna(subset=['Fecha', 'Operador'])
base = base[['Fecha', 'Operador', 'Categoria', 'Cliente', 'Descripcion', 'Mov'] + [col for col in base.columns if col not in ['Fecha', 'Operador', 'Categoria', 'Cliente', 'Descripcion', 'Mov']]]

# Convert 'Mov' and 'TC' columns to numeric
base['Mov'] = base['Mov'].apply(convert_to_numeric)
base['TC'] = base['TC'].apply(convert_to_numeric)

# Convert to numeric with error handling
base['Mov'] = pd.to_numeric(base['Mov'], errors='coerce')
base['TC'] = pd.to_numeric(base['TC'], errors='coerce')

operaciones = base.iloc[:,0:7].copy()    ### Solo tomo la primera columna, luego se podría incluir más info de Montos para complementar Mov (1era columna)
#operaciones = operaciones[operaciones['Categoria'].isin(['Compra USD', 'Venta USD'])].copy()
operaciones['Cliente'] = operaciones['Cliente'].str.strip().str.title()
operaciones['Operador'] = operaciones['Operador'].str.strip().str.upper()
operaciones = operaciones[~operaciones['Cliente'].str.contains('Apertura De Caja|Ajuste Caja', na=False)]
operaciones = operaciones[operaciones['Cliente'] != "Movimiento De Caja"].copy()    # Excluir movimientos de caja
operaciones = operaciones.dropna(subset=['Cliente'])  # Drop rows with missing Cliente
operaciones[['Mov', 'TC']] = operaciones[['Mov', 'TC']].fillna(0)  # Fill NaN only in numeric columns

### Tablas de Clientes Mensual ###
operaciones_mes_actual = operaciones[pd.to_datetime(operaciones['Fecha']).dt.to_period('M') == pd.to_datetime("today").to_period('M')].copy()
operaciones_usd_por_cliente = operaciones_mes_actual.groupby(['Cliente', 'Categoria']).agg({
    'Mov': ['count', lambda x: x.abs().sum()]
}).reset_index()
operaciones_usd_por_cliente.columns = ['Cliente', 'Moneda', 'Cantidad Operaciones', 'Monto operado en el mes']
operaciones_usd_por_cliente.sort_values(by='Monto operado en el mes', ascending=False, inplace=True)
operaciones_usd_por_cliente.reset_index(drop=True, inplace=True)
operaciones_usd_por_cliente = operaciones_usd_por_cliente[operaciones_usd_por_cliente['Monto operado en el mes'] != 0]
top_20_participacion_operaciones_usd_por_cliente = operaciones_usd_por_cliente.nlargest(20, 'Monto operado en el mes').copy()
total_monto = operaciones_usd_por_cliente['Monto operado en el mes'].sum()
top_20_participacion_operaciones_usd_por_cliente['Porcentaje'] = (top_20_participacion_operaciones_usd_por_cliente['Monto operado en el mes'] / total_monto * 100).round(2)

#Otros
otros_monto = operaciones_usd_por_cliente.iloc[20:]['Monto operado en el mes'].sum()
otros_cantidad = operaciones_usd_por_cliente.iloc[20:]['Cantidad Operaciones'].sum()
otros_porcentaje = (otros_monto / total_monto * 100).round(2)
otros_row = pd.DataFrame({
    'Cliente': ['Otros'],
    'Moneda': ['USD'],
    'Cantidad Operaciones': [otros_cantidad],
    'Monto operado en el mes': [otros_monto],
    'Porcentaje': [otros_porcentaje]
})
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

#Matriz operadores por día
sgto_matriz_operadores_dias = operador_operaciones_pivot.reset_index()
columns_to_keep = ['BS', 'BS AS', 'CA', 'EP', 'FB', 'MT', 'NP', 'NS', 'TDLA', 'Total']
available_columns = [col for col in columns_to_keep if col in sgto_matriz_operadores_dias.columns]
sgto_matriz_operadores_dias = sgto_matriz_operadores_dias[['Fecha'] + available_columns]
sgto_matriz_operadores_dias['BS AS'] = sgto_matriz_operadores_dias['BS'] + sgto_matriz_operadores_dias['BS AS']
sgto_matriz_operadores_dias.drop(columns=['BS'], inplace=True)

sgto_matriz_operadores_dias = sgto_matriz_operadores_dias[sgto_matriz_operadores_dias['Fecha'].str.strip() != ''].copy()
sgto_matriz_operadores_dias['Fecha'] = pd.to_datetime(sgto_matriz_operadores_dias['Fecha'], format='%Y-%m-%d', errors='coerce')
sgto_matriz_operadores_dias = sgto_matriz_operadores_dias.sort_values('Fecha')
sgto_matriz_operadores_dias['Fecha'] = sgto_matriz_operadores_dias['Fecha'].dt.strftime('%Y-%m-%d')

### Tabla Montos operados para operaciones en USD ###
operaciones_usd = operaciones.copy()
operaciones_usd.rename(columns={'Mov': 'Monto', 'Categoria': 'Moneda'}, inplace=True)
operaciones_usd.loc[:, 'Monto'] = operaciones_usd['Monto'].abs()
operaciones_usd['MontoxTC'] = operaciones_usd['Monto'] * operaciones_usd['TC']
tabla_monto_operado = operaciones_usd.groupby('Fecha').agg({
    'Monto': 'sum'
}).reset_index()

### Tabla Tipo de Cambio Promedio por día ###
operaciones_usd_tdc_clean = operaciones_usd[operaciones_usd['TC'] > 1000].copy()   # Filtrar operaciones con TC válido # Qué hacer con los casos donde TC es NaN??
tabla_tipo_de_cambio_por_dia = operaciones_usd_tdc_clean.groupby('Fecha').agg({         
    'Monto': 'sum',    
    'MontoxTC': 'sum'
}).reset_index()

tabla_tipo_de_cambio_por_dia['TC Prom'] = tabla_tipo_de_cambio_por_dia['MontoxTC'] / tabla_tipo_de_cambio_por_dia['Monto']
tabla_tipo_de_cambio_por_dia = tabla_tipo_de_cambio_por_dia[['Fecha', 'TC Prom']]
sgto_montos_usd_tdc = operaciones_usd_tdc_clean.groupby('Fecha').agg({
    'TC': [lambda x: x.quantile(0.05), lambda x: x.quantile(0.95)]
}).reset_index()
sgto_montos_usd_tdc_flat = sgto_montos_usd_tdc.copy()
sgto_montos_usd_tdc_flat.columns = ['Fecha', 'TC_min', 'TC_max']
tabla_tdc = tabla_tipo_de_cambio_por_dia[['Fecha', 'TC Prom']].merge(
    sgto_montos_usd_tdc_flat,
    on='Fecha',
    how='left')
tabla_tdc = tabla_tdc.merge(
    tabla_monto_operado,
    on='Fecha',
    how='left')

#### Cálculo de métricas principales ###

ayer = pd.to_datetime("today") - pd.Timedelta(days=1)
ayer_formatted = ayer.strftime('%Y-%m-%d')
ante_ayer = pd.to_datetime("today") - pd.Timedelta(days=2)
ante_ayer_formatted = ante_ayer.strftime('%Y-%m-%d')

# Get metrics from tabla_tdc for yesterday
if ayer_formatted in tabla_tdc['Fecha'].values:
    ayer_data = tabla_tdc[tabla_tdc['Fecha'] == ayer_formatted].iloc[0]
    monto_usd_ayer = ayer_data['Monto']
    tdc_ayer = ayer_data['TC Prom']
else:
    monto_usd_ayer = 0
    tdc_ayer = 0

# Get metrics from tabla_tdc for today
if ante_ayer_formatted in tabla_tdc['Fecha'].values:
    ante_ayer_data = tabla_tdc[tabla_tdc['Fecha'] == ante_ayer_formatted].iloc[0]
    monto_usd_ante_ayer = ante_ayer_data['Monto']
    tdc_ante_ayer = ante_ayer_data['TC Prom']
else:
    monto_usd_ante_ayer = 0
    tdc_ante_ayer = 0
metricas_df = pd.DataFrame([{
    'Monto USD ayer': monto_usd_ayer,
    'TdC ayer': tdc_ayer,
    'Monto USD anteayer': monto_usd_ante_ayer,
    'TdC anteayer': tdc_ante_ayer
}])

#### Analisis de clientes para lista de difusion

clientes_worksheet = sh.worksheet('Cliente Diego y Joaco')
clientes_diego = clientes_worksheet.get('B3:B500')
clientes_diego_list = [item[0].strip().title() for item in clientes_diego if item and item[0].strip() != '']

clientes_joaco = clientes_worksheet.get('F3:F500')
clientes_joaco_list = [item[0].strip().title() for item in clientes_joaco if item and item[0].strip() != '']

# Create combined client list with vendedor
clientes_con_vendedor = []
for cliente in clientes_diego_list:
    clientes_con_vendedor.append({'Cliente': cliente, 'Vendedor': 'Diego'})
for cliente in clientes_joaco_list:
    clientes_con_vendedor.append({'Cliente': cliente, 'Vendedor': 'Joaco'})

# Function to find best fuzzy match
def find_best_match(cliente_lista, operaciones_clientes, threshold=80):
    best_match = None
    best_score = 0
    for op_cliente in operaciones_clientes:
        score = fuzz.ratio(cliente_lista.lower(), op_cliente.lower())
        if score > best_score and score >= threshold:
            best_score = score
            best_match = op_cliente
    return best_match

# Get unique clients from operaciones
operaciones_clientes = operaciones['Cliente'].unique()

# Current month period
current_month = pd.to_datetime("today").to_period('M')

# Create analysis dataframe
clientes_difusion = []

for cliente_info in clientes_con_vendedor:
    cliente_lista = cliente_info['Cliente']
    vendedor = cliente_info['Vendedor']
    
    # Find fuzzy match
    matched_cliente = find_best_match(cliente_lista, operaciones_clientes)
    
    if matched_cliente:
        # Filter operations for this client
        ops_cliente = operaciones[operaciones['Cliente'] == matched_cliente].copy()
        
        # Check if operated in current month
        ops_mes_actual = ops_cliente[pd.to_datetime(ops_cliente['Fecha']).dt.to_period('M') == current_month]
        opero_mes_actual = len(ops_mes_actual) > 0
        
        # Last operation date
        ultima_operacion = ops_cliente['Fecha'].max() if not ops_cliente.empty else None
        
        # Total operations count
        cantidad_operaciones = len(ops_cliente)
        
        # Total amount (sum of absolute values of Mov)
        monto_total = ops_cliente['Mov'].abs().sum()
        
        # Average TC (excluding zeros)
        tc_no_zero = ops_cliente[ops_cliente['TC'] != 0]['TC']
        tc_promedio = tc_no_zero.mean() if not tc_no_zero.empty else 0
        
    else:
        # No match found
        opero_mes_actual = False
        ultima_operacion = None
        cantidad_operaciones = 0
        monto_total = 0
        tc_promedio = 0
    
    clientes_difusion.append({
        'Cliente Difusion': cliente_lista,
        'Matcheo en base de datos': matched_cliente,
        'Vendedor': vendedor,
        'Opero mes actual': opero_mes_actual,
        'Ultima operacion': ultima_operacion,
        'Cantidad de operaciones': cantidad_operaciones,
        'Monto total': monto_total,
        'TC promedio': tc_promedio
    })

clientes_difusion = pd.DataFrame(clientes_difusion)

clientes_difusion['Opero mes actual'] = clientes_difusion['Opero mes actual'].map({True: 'Si', False: 'No'})


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
    if not metricas_df.empty:
        supabase_client.table('sgto_montos_usd_tdc').delete().neq('id', 0).execute()
        insert_table_data('sgto_montos_usd_tdc', metricas_df.to_dict(orient='records'))
        print("Métricas principales actualizadas.")
    else:
        print("No se actualiza sgto_montos_usd_tdc porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_montos_usd_tdc: {e}")

try:
    if not sgto_matriz_operadores_dias.empty:
        supabase_client.table('sgto_matriz_operadores_dias').delete().neq('id', 0).execute()
        insert_table_data('sgto_matriz_operadores_dias', sgto_matriz_operadores_dias.to_dict(orient='records'))
        print("Métricas de operadores por día actualizadas.")
    else:
        print("No se actualiza sgto_matriz_operadores_dias porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_matriz_operadores_dias: {e}")

try:
    if not operaciones_operador_por_dia.empty:
        supabase_client.table('sgto_operaciones_operador_por_dia').delete().neq('id', 0).execute()
        insert_table_data('sgto_operaciones_operador_por_dia', operaciones_operador_por_dia.to_dict(orient='records'))
    else:
        print("No se actualiza sgto_operaciones_operador_por_dia porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_operaciones_operador_por_dia: {e}")

try:
    if not tabla_tdc.empty:
        supabase_client.table('sgto_tabla_tdc').delete().neq('id', 0).execute()
        insert_table_data('sgto_tabla_tdc', tabla_tdc.to_dict(orient='records'))
    else:
        print("No se actualiza sgto_tabla_tdc porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_tabla_tdc: {e}")

try:
    if not operaciones_usd_por_cliente.empty:
        supabase_client.table('sgto_operaciones_usd_por_cliente').delete().neq('id', 0).execute()
        insert_table_data('sgto_operaciones_usd_por_cliente', operaciones_usd_por_cliente.to_dict(orient='records'))
        print("Métricas de operaciones USD por cliente actualizadas.")
    else:
        print("No se actualiza sgto_operaciones_usd_por_cliente porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_operaciones_usd_por_cliente: {e}")

try:
    if not top_20_participacion_operaciones_usd_por_cliente.empty:
        supabase_client.table('sgto_top_20_participacion_operaciones_usd_por_cliente').delete().neq('id', 0).execute()
        insert_table_data('sgto_top_20_participacion_operaciones_usd_por_cliente', top_20_participacion_operaciones_usd_por_cliente.to_dict(orient='records'))
    else:
        print("No se actualiza sgto_top_20_participacion_operaciones_usd_por_cliente porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_top_20_participacion_operaciones_usd_por_cliente: {e}")

try:
    if not clientes_difusion.empty:
        supabase_client.table('sgto_clientes_difusion').delete().neq('id', 0).execute()
        insert_table_data('sgto_clientes_difusion', clientes_difusion.to_dict(orient='records'))
        print("Análisis de clientes para lista de difusión actualizado.")
    else:
        print("No se actualiza sgto_clientes_difusion porque el DataFrame está vacío.")
except Exception as e:
    print(f"Error updating sgto_clientes_difusion: {e}")

update_log()

print("Actualización completada.")