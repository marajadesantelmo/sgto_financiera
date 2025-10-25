import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase, sheet_operaciones_url, sheet_control_caja_url
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)
from datetime import datetime

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


print("Iniciando actualización de datos de operaciones...")
if os.path.exists('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json'):
    gc = gspread.service_account('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json')
elif os.path.exists('credenciales_gsheets.json'):
    gc = gspread.service_account(filename='credenciales_gsheets.json')
#Operaciones
sheet_url = sheet_operaciones_url
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Operaciones Octubre 2025')

#Datos generales
columns1 = ['Fecha', 'Operador', 'Cliente']
data_range1 = worksheet.get('A4:C3961')
data1 = pd.DataFrame(data_range1, columns=columns1)

#Datos de monto, moneda, caja y tc
columns_usd = ['Monto', 'TC']
columns_pesos = ['Monto']

data_range2 = worksheet.get('F4:G3961')
data2 = pd.DataFrame(data_range2, columns=columns_usd)

data2 = pd.concat([data1, data2], axis=1)
data2 = data2.dropna(subset=['Monto'])
data2['Moneda'] = 'USD'
data2['Caja'] = 'Salta'

data_range3 = worksheet.get('K4:K3961')
data3 = pd.DataFrame(data_range3, columns=columns_pesos)
data3 = pd.concat([data1, data3], axis=1)
data3 = data3.dropna(subset=['Monto'])
data3['Moneda'] = 'Pesos'
data3['Caja'] = 'Salta'

data_range4 = worksheet.get('N4:N3961')
data4 = pd.DataFrame(data_range4, columns=columns_pesos)
data4 = pd.concat([data1, data4], axis=1)
data4 = data4.dropna(subset=['Monto'])
data4['Moneda'] = 'Transferencia'
data4['Caja'] = 'Salta'

data_range5 = worksheet.get('Q4:R3961')
data5 = pd.DataFrame(data_range5, columns=columns_usd)
data5 = pd.concat([data1, data5], axis=1)
data5 = data5.dropna(subset=['Monto'])
data5['Moneda'] = 'USD'
data5['Caja'] = 'Office Park'

data_range6 = worksheet.get('V4:V3961')
data6 = pd.DataFrame(data_range6, columns=columns_pesos)
data6 = pd.concat([data1, data6], axis=1)
data6 = data6.dropna(subset=['Monto'])
data6['Moneda'] = 'Pesos'
data6['Caja'] = 'Office Park'

data_range7 = worksheet.get('Y4:Y3961')
data7 = pd.DataFrame(data_range7, columns=columns_pesos)
data7 = pd.concat([data1, data7], axis=1)
data7 = data7.dropna(subset=['Monto'])
data7['Moneda'] = 'Transferencia'
data7['Caja'] = 'Office Park'

data_range8 = worksheet.get('AB4:AB3961')
data8 = pd.DataFrame(data_range8, columns=columns_pesos)
data8 = pd.concat([data1, data8], axis=1)
data8 = data8.dropna(subset=['Monto'])
data8['Moneda'] = 'Euros'
data8['Caja'] = 'Office Park'

data_range9 = worksheet.get('AE4:AE3961')
data9 = pd.DataFrame(data_range9, columns=columns_pesos)
data9 = pd.concat([data1, data9], axis=1)
data9 = data9.dropna(subset=['Monto'])
data9['Moneda'] = 'Euros'
data9['Caja'] = 'Salta'

data_range10 = worksheet.get('AH4:AH3961')
data10 = pd.DataFrame(data_range10, columns=columns_pesos)
data10 = pd.concat([data1, data10], axis=1)
data10 = data10.dropna(subset=['Monto'])
data10['Moneda'] = 'USDT'
data10['Caja'] = 'Salta'

data_range11 = worksheet.get('AK4:AK3961')
data11 = pd.DataFrame(data_range11, columns=columns_pesos)
data11 = pd.concat([data1, data11], axis=1)
data11 = data11.dropna(subset=['Monto'])
data11['Moneda'] = 'USD'
data11['Caja'] = 'Mindful'

data_range12 = worksheet.get('AN4:AO3961')
data12 = pd.DataFrame(data_range12, columns=columns_usd)
data12 = pd.concat([data1, data12], axis=1)
data12 = data12.dropna(subset=['Monto'])
data12['Moneda'] = 'USD'
data12['Caja'] = 'Reconquista CABA'

data_range13 = worksheet.get('AS4:AS3961')
data13 = pd.DataFrame(data_range13, columns=columns_pesos)
data13 = pd.concat([data1, data13], axis=1)
data13 = data13.dropna(subset=['Monto'])
data13['Moneda'] = 'Pesos'
data13['Caja'] = 'Reconquista CABA'

data_range14 = worksheet.get('AV4:AV3961')
data14 = pd.DataFrame(data_range14, columns=columns_pesos)
data14 = pd.concat([data1, data14], axis=1)
data14 = data14.dropna(subset=['Monto'])
data14['Moneda'] = 'Transferencia'
data14['Caja'] = 'Reconquista CABA'

data_range15 = worksheet.get('AY4:AY3961')
data15 = pd.DataFrame(data_range15, columns=columns_pesos)
data15 = pd.concat([data1, data15], axis=1)
data15 = data15.dropna(subset=['Monto'])
data15['Moneda'] = 'Euros'
data15['Caja'] = 'Reconquista CABA'

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
sgto_matriz_operadores_dias.drop(columns=['', '0'], inplace=True)
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

tabla_tipo_de_cambio_por_dia = operaciones_usd[operaciones_usd['TC'] != 0].groupby('Fecha').agg({         # Qué hacer con los casos donde TC es NaN??
    'Monto': 'sum',    
    'MontoxTC': 'sum'
}).reset_index()

tabla_tipo_de_cambio_por_dia['TC Prom'] = tabla_tipo_de_cambio_por_dia['MontoxTC'] / tabla_tipo_de_cambio_por_dia['Monto']
tabla_tipo_de_cambio_por_dia = tabla_tipo_de_cambio_por_dia[['Fecha', 'TC Prom']]

# Calculo de tipo de cambio maximo y minimo por dia
sgto_montos_usd_tdc = operaciones_usd[operaciones_usd['TC'] > 1000].groupby('Fecha').agg({
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


supabase_client.table('sgto_montos_usd_tdc').delete().neq('id', 0).execute()
supabase_client.table('sgto_matriz_operadores_dias').delete().neq('id', 0).execute()
supabase_client.table('sgto_operaciones_operador_por_dia').delete().neq('id', 0).execute()
supabase_client.table('sgto_tabla_datos').delete().neq('id', 0).execute()
supabase_client.table('sgto_historico_caja').delete().neq('id', 0).execute()
supabase_client.table('sgto_tabla_tdc').delete().neq('id', 0).execute()
supabase_client.table('sgto_operaciones_usd_por_cliente').delete().neq('id', 0).execute()
supabase_client.table('sgto_top_20_participacion_operaciones_usd_por_cliente').delete().neq('id', 0).execute()

insert_table_data('sgto_montos_usd_tdc', metricas_df.to_dict(orient='records'))
insert_table_data('sgto_matriz_operadores_dias', sgto_matriz_operadores_dias.to_dict(orient='records'))
insert_table_data('sgto_operaciones_operador_por_dia', operaciones_operador_por_dia.to_dict(orient='records'))
insert_table_data('sgto_tabla_datos', df_tabla.to_dict(orient='records'))
insert_table_data('sgto_historico_caja', df.to_dict(orient='records'))
insert_table_data('sgto_tabla_tdc', tabla_tdc.to_dict(orient='records'))
insert_table_data('sgto_operaciones_usd_por_cliente', operaciones_usd_por_cliente.to_dict(orient='records'))
insert_table_data('sgto_top_20_participacion_operaciones_usd_por_cliente', top_20_participacion_operaciones_usd_por_cliente.to_dict(orient='records'))
update_log()

print("Actualización completada.")