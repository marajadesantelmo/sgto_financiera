import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)
from datetime import datetime

print("Iniciando actualización de datos de operaciones...")
if os.path.exists('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json'):
    gc = gspread.service_account('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json')
elif os.path.exists('credenciales_gsheets.json'):
    gc = gspread.service_account(filename='credenciales_gsheets.json')

sheet_url = 'https://docs.google.com/spreadsheets/d/1luAwlud_R8-GDIYZRiQuuSIOnF5RuPATZdqdIDm-0j8'
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Operaciones Octubre 2025')


columns1 = ['Fecha', 'Operador', 'Cliente']

columns2 = ['USD - Monto', 'USD - TC', 'USD - Total pesos', 'USD - Caja Acum', 'Libre1', 'PESOS - Monto', 'PESOS - Caja Acum', 'Libre2',
           'TFS SALTA - Monto', 'TFS Salta - Caja Acum']

# Get data from the specified range A4:M3961
data_range1 = worksheet.get('A4:C3961')
data_range2 = worksheet.get('F4:P3961')


print("Datos obtenidos de Google Sheets, procesando...")
data1 = pd.DataFrame(data_range1, columns=columns1)
data2 = pd.DataFrame(data_range2, columns=columns2)

data2 = data2.drop(columns=['Libre1', 'Libre2'])
operaciones = pd.concat([data1, data2], axis=1)
operaciones = operaciones.dropna(subset=['Fecha'])
operaciones = operaciones[operaciones['Operador'] != '']
operaciones = operaciones[operaciones['Operador'].notna()]
# Create a new dataframe to store the transformed data
transformed = []

for _, row in operaciones.iterrows():
    # Common fields for all rows
    base_data = {
        'Fecha': row['Fecha'],
        'Operador': row['Operador'],
        'Cliente': row['Cliente']
    }
    
    # Check USD data
    if pd.notna(row['USD - Monto']) and str(row['USD - Monto']).strip() not in ['', '-']:
        usd_data = base_data.copy()
        usd_data['Tipo'] = 'USD'
        usd_data['Monto'] = row['USD - Monto']
        usd_data['TC'] = row['USD - TC']
        usd_data['Total pesos'] = row['USD - Total pesos']
        usd_data['Caja Acum'] = row['USD - Caja Acum']
        transformed.append(usd_data)
    
    # Check PESOS data
    if pd.notna(row['PESOS - Monto']) and str(row['PESOS - Monto']).strip() not in ['', '-']:
        pesos_data = base_data.copy()
        pesos_data['Tipo'] = 'PESOS'
        pesos_data['Monto'] = row['PESOS - Monto']
        pesos_data['TC'] = None
        pesos_data['Total pesos'] = row['PESOS - Monto']  # Same as monto for pesos
        pesos_data['Caja Acum'] = row['PESOS - Caja Acum']
        transformed.append(pesos_data)
    
    # Check TFS SALTA data
    if pd.notna(row['TFS SALTA - Monto']) and str(row['TFS SALTA - Monto']).strip() not in ['', '-']:
        tfs_data = base_data.copy()
        tfs_data['Tipo'] = 'TFS SALTA'
        tfs_data['Monto'] = row['TFS SALTA - Monto']
        tfs_data['TC'] = None
        tfs_data['Total pesos'] = None
        tfs_data['Caja Acum'] = row['TFS Salta - Caja Acum']
        transformed.append(tfs_data)

# Create final transformed dataframe
operaciones_transformed = pd.DataFrame(transformed)

# Replace the original operaciones dataframe
operaciones = operaciones_transformed
operaciones.fillna("0", inplace=True)


def convert_to_numeric(value):
    if isinstance(value, str):
        # Remove spaces, replace commas with dots (if European format)
        cleaned = value.strip().replace(' ', '')
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

# Apply numeric conversion to appropriate columns
numeric_columns = ['Monto', 'TC', 'Total pesos', 'Caja Acum']
for col in numeric_columns:
    operaciones[col] = operaciones[col].apply(convert_to_numeric)

# Convert data types explicitly
operaciones['Monto'] = pd.to_numeric(operaciones['Monto'], errors='coerce')
operaciones['TC'] = pd.to_numeric(operaciones['TC'], errors='coerce')
operaciones['Total pesos'] = pd.to_numeric(operaciones['Total pesos'], errors='coerce')
operaciones['Caja Acum'] = pd.to_numeric(operaciones['Caja Acum'], errors='coerce')

operaciones_operador_por_dia = operaciones.groupby(['Fecha', 'Operador']).size().reset_index(name='Cantidad Operaciones')

operador_operaciones_pivot = operaciones_operador_por_dia.pivot_table(
    index='Fecha', 
    columns='Operador', 
    values='Cantidad Operaciones', 
    fill_value=0
)

operador_operaciones_pivot['Total'] = operador_operaciones_pivot.sum(axis=1)
sgto_matriz_operadores_dias = operador_operaciones_pivot.reset_index()
sgto_matriz_operadores_dias['Fecha'] = pd.to_datetime(sgto_matriz_operadores_dias['Fecha'], format='%d/%m/%Y')
sgto_matriz_operadores_dias = sgto_matriz_operadores_dias.sort_values('Fecha')
sgto_matriz_operadores_dias['Fecha'] = sgto_matriz_operadores_dias['Fecha'].dt.strftime('%d/%m/%Y')

operaciones_usd = operaciones[(operaciones['Tipo'] == 'USD') & (operaciones['TC'].notna())].copy()   # Qué hacer con los casos donde TC es NaN??
operaciones_usd.loc[:, 'Monto'] = operaciones_usd['Monto'].abs()
operaciones_usd['MontoxTC'] = operaciones_usd['Monto'] * operaciones_usd['TC']
ayer = pd.to_datetime("today") - pd.Timedelta(days=1)
ayer = ayer.strftime('%d/%m/%Y')

if ayer in operaciones_usd['Fecha'].values:
    operaciones_usd_ayer = operaciones_usd[operaciones_usd['Fecha'] == ayer]
    monto_usd_ayer = operaciones_usd_ayer['Monto'].sum()
    montoxTC_usd_ayer = operaciones_usd_ayer['MontoxTC'].sum()
    tdc_ayer = montoxTC_usd_ayer / monto_usd_ayer
else: 
    monto_usd_ayer = 0
    tdc_ayer = 0

hoy = pd.to_datetime("today").strftime('%d/%m/%Y')
if hoy in sgto_matriz_operadores_dias['Fecha'].values:
    operaciones_usd_hoy = operaciones_usd[operaciones_usd['Fecha'] == hoy]
    monto_usd_hoy = operaciones_usd_hoy['Monto'].sum()
    montoxTC_usd_hoy = operaciones_usd_hoy['MontoxTC'].sum()
    tdc_hoy = montoxTC_usd_hoy / monto_usd_hoy
else: 
    monto_usd_hoy = 0
    tdc_hoy = 0    

metricas_df = pd.DataFrame([{
    'Monto USD ayer': monto_usd_ayer,
    'TdC ayer': tdc_ayer,
    'Monto USD hoy': monto_usd_hoy,
    'TdC hoy': tdc_hoy
}])


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
    supabase_client.from_("sgto_log_entry").insert(log_entry).execute()


supabase_client.table('sgto_montos_usd_tdc').delete().neq('id', 0).execute()
supabase_client.table('sgto_matriz_operadores_dias').delete().neq('id', 0).execute()
supabase_client.table('sgto_operaciones_operador_por_dia').delete().neq('id', 0).execute()

insert_table_data('sgto_montos_usd_tdc', metricas_df.to_dict(orient='records'))
insert_table_data('sgto_matriz_operadores_dias', sgto_matriz_operadores_dias.to_dict(orient='records'))
insert_table_data('sgto_operaciones_operador_por_dia', operaciones_operador_por_dia.to_dict(orient='records'))

update_log()

print("Actualización completada.")