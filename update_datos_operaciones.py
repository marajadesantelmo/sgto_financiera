import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import os

gc = gspread.service_account(filename='\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\sgto_financiera\\credenciales_gsheets.json')

sheet_url = 'https://docs.google.com/spreadsheets/d/1luAwlud_R8-GDIYZRiQuuSIOnF5RuPATZdqdIDm-0j8'
sh = gc.open_by_url(sheet_url)
worksheet = sh.worksheet('Operaciones Octubre 2025')


columns1 = ['Fecha', 'Operador', 'Cliente']

columns2 = ['USD - Monto', 'USD - TC', 'USD - Total pesos', 'USD - Caja Acum', 'Libre1', 'PESOS - Monto', 'PESOS - Caja Acum', 'Libre2',
           'TFS SALTA - Monto', 'TFS Salta - Caja Acum']

# Get data from the specified range A4:M3961
data_range1 = worksheet.get('A4:C3961')
data_range2 = worksheet.get('F4:P3961')

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

operador_operaciones_diarios_tidy = operaciones.groupby(['Fecha', 'Operador']).size().reset_index(name='Cantidad_Operaciones')

operador_operaciones_pivot = operador_operaciones_diarios_tidy.pivot_table(
    index='Fecha', 
    columns='Operador', 
    values='Cantidad_Operaciones', 
    fill_value=0
)

operador_operaciones_pivot['Total'] = operador_operaciones_pivot.sum(axis=1)
operador_operaciones_diarios = operador_operaciones_pivot.reset_index()
operador_operaciones_diarios['Fecha'] = pd.to_datetime(operador_operaciones_diarios['Fecha'], format='%d/%m/%Y')
operador_operaciones_diarios = operador_operaciones_diarios.sort_values('Fecha')
operador_operaciones_diarios['Fecha'] = operador_operaciones_diarios['Fecha'].dt.strftime('%d/%m/%Y')

