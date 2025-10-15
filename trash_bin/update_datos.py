import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import os

gc = gspread.service_account(filename='\\\\dc01\\Usuarios\\PowerBI\\flastra\\Documents\\pablo_financiera\\credenciales_gsheets.json')

sheet_url = 'https://docs.google.com/spreadsheets/d/1quiYMjvkoE6N9pVxEnPithfOfz-QdY8jEZkR3qC0xzg'
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
df['Total Caja'] = df['Total Caja'].str.replace('.', '').str.replace(',', '.').astype(int)
df['Ganancias'] = df['Ganancias'].str.replace('.', '').str.replace(',', '.').astype(int)

sheet= gc.open('Datos Financiera')
seguimiento_worksheet = sheet.worksheet('Seguimiento')
set_with_dataframe(seguimiento_worksheet, df)

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
df_tabla['HOY'] = df_tabla['HOY'].str.replace('.', '')
df_tabla['ACUM MES'] = df_tabla['ACUM MES'].str.replace('.', '')
df_tabla['PROM x DIA'] = df_tabla['PROM x DIA'].str.replace('.', '')
df_tabla['VAR MA'] = df_tabla['VAR MA'].str.replace('%', '')
df_tabla['PROY MES'] = df_tabla['PROY MES'].str.replace('.', '')
df_tabla['VAR PROY'] = df_tabla['VAR PROY'].str.replace('%', '')
df_tabla['Obj'] = df_tabla['Obj'].str.replace('.', '')
df_tabla['CONCEPTO'] = df_tabla['CONCEPTO'].str.strip() 
# Convert numeric columns to integers
numeric_columns = ['HOY', 'ACUM MES', 'PROM x DIA', 'PROY MES', 'Obj']
for col in numeric_columns:
    df_tabla[col] = pd.to_numeric(df_tabla[col], errors='coerce').fillna(0).astype(int)

# Convert percentage columns to float and divide by 100
percentage_columns = ['VAR MA', 'VAR PROY']
for col in percentage_columns:
    df_tabla[col] = pd.to_numeric(df_tabla[col], errors='coerce').fillna(0) / 100

tablita_worksheet = sheet.worksheet('Tablita')
set_with_dataframe(tablita_worksheet, df_tabla)