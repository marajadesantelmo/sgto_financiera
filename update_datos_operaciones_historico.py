import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)
from datetime import datetime, timedelta

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
    gc = gspread.service_account('\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json') # type: ignore
elif os.path.exists('credenciales_gsheets.json'):
    gc = gspread.service_account(filename='credenciales_gsheets.json') # type: ignore
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

data1 = data1[['Fecha', 'Operador', 'Cliente']].copy()

#Datos de monto, moneda, caja y tc
columns_usd = ['Monto', 'TC']
columns_pesos = ['Monto']

data_range2 = worksheet.get('F4:G3961')
data2 = pd.DataFrame(data_range2, columns=columns_usd)

data2 = pd.concat([data1, data2], axis=1)
data2 = data2.dropna(subset=['Monto'])
data2['Moneda'] = 'USD'
data2['Caja'] = 'Salta'


# Convert Monto and TC to numeric values
data2['Monto'] = data2['Monto'].apply(convert_to_numeric)
data2['TC'] = data2['TC'].apply(convert_to_numeric)

# Group by Cliente and calculate the required metrics
operaciones_por_cliente_historico = data2.groupby('Cliente').agg({
    'Monto': lambda x: abs(pd.to_numeric(x, errors='coerce')).sum(),
    'TC': lambda x: pd.to_numeric(x, errors='coerce').replace([0, None]).dropna().mean() if not pd.to_numeric(x, errors='coerce').replace([0, None]).dropna().empty else None,
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
    if last_date >= two_months_ago:
        return "Activo"
    elif last_date >= six_months_ago:
        return "Inactivo"
    else:
        return "Perdido"

operaciones_por_cliente_historico['Tipo'] = operaciones_por_cliente_historico['Ultima fecha'].apply(classify_client_status)

try: 
    supabase_client.from_('sgto_operaciones_por_cliente_historico').delete().neq('id', 0).execute()
    # Replace NaN values with None before converting to dict
    operaciones_clean = operaciones_por_cliente_historico.fillna(None)
    supabase_client.from_('sgto_operaciones_por_cliente_historico').insert(operaciones_clean.to_dict(orient='records')).execute()
except Exception as e:
    print(f"Error updating supabase table: {e}")
    
print("Actualización de datos de operaciones completada.")