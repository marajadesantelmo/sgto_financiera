import gspread
import pandas as pd
import os
from tokens import url_supabase, key_supabase
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

#Datos de monto, moneda, caja y tc
columns_usd = ['Monto', 'TC']
columns_pesos = ['Monto']

data_range2 = worksheet.get('F4:G3961')
data2 = pd.DataFrame(data_range2, columns=columns_usd)

data2 = pd.concat([data1, data2], axis=1)
data2 = data2.dropna(subset=['Monto'])
data2['Moneda'] = 'USD'
data2['Caja'] = 'Salta'
