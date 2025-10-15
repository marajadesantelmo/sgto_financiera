import streamlit as st
st.set_page_config(
    page_title="Análisis de Operaciones Financieras",
    page_icon="📊",
    layout="wide"
)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
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

st.dataframe(df_matriz)

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

# Crear gráfico de barras interactivo con Plotly
fig_barras = px.bar(
    df_filtrado,
    x='Fecha',
    y='Cantidad Operaciones',
    color='Operador',
    title='Operaciones por Operador y Día',
    barmode='group'
)

# Customizar el diseño
fig_barras.update_layout(
    xaxis_title='Fecha',
    yaxis_title='Cantidad de Operaciones',
    xaxis_tickangle=-45,
    showlegend=True,
    height=600
)

# Mostrar el gráfico
st.plotly_chart(fig_barras, use_container_width=True)