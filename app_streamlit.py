import streamlit as st
st.set_page_config(
    page_title="Análisis de Operaciones Financieras",
    page_icon="📊",
    layout="wide"
)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from supabase_connection import fetch_table_data


url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

# Título principal
st.title("📊 Análisis de Operaciones Financieras")

df_matriz  = fetch_table_data("sgto_matriz_operadores_dias")
df_operaciones = fetch_table_data("sgto_operaciones_operador_por_dia")

# Convertir fechas al formato correcto
df_matriz['Fecha'] = pd.to_datetime(df_matriz['Fecha'], format='%d/%m/%Y')
df_operaciones['Fecha'] = pd.to_datetime(df_operaciones['Fecha'], format='%d/%m/%Y')

# 1. Heatmap de la matriz de operadores
st.header("Matriz de Operadores por Día")

# Preparar datos para el heatmap
columnas_operadores = ['BS AS', 'CA', 'EP', 'FB', 'MT', 'NP', 'TDLA']
df_heatmap = df_matriz.pivot_table(
    index='Fecha', 
    values=columnas_operadores
)

# Crear el heatmap
fig_heatmap, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(df_heatmap, cmap='YlOrRd', annot=True, fmt='.0f', cbar_kws={'label': 'Cantidad de Operaciones'})
plt.title('Heatmap de Operaciones por Operador')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig_heatmap)

# 2. Gráfico de barras con filtro de operadores
st.header("Operaciones por Operador")

# Obtener lista única de operadores
operadores = sorted(df_operaciones['Operador'].unique())

# Crear filtro multiselect para operadores
operadores_seleccionados = st.multiselect(
    'Seleccionar Operadores:',
    operadores,
    default=operadores
)

# Filtrar datos según la selección
df_filtrado = df_operaciones[df_operaciones['Operador'].isin(operadores_seleccionados)]

# Crear gráfico de barras
fig_barras = plt.figure(figsize=(12, 6))
sns.barplot(data=df_filtrado, x='Fecha', y='Cantidad Operaciones', hue='Operador')
plt.title('Operaciones por Operador y Día')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig_barras)