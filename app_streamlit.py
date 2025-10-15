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
import numpy as np
import os
from supabase_connection import fetch_table_data

# Título principal
st.title("📊 Análisis de Operaciones Financieras")

df_matriz = fetch_table_data("sgto_matriz_operadores_dias")
df_operaciones = fetch_table_data("sgto_operaciones_operador_por_dia")

# Convertir fechas al formato correcto
df_matriz['Fecha'] = pd.to_datetime(df_matriz['Fecha'], format='%d/%m/%Y')
df_operaciones['Fecha'] = pd.to_datetime(df_operaciones['Fecha'], format='%d/%m/%Y')

# Crear dos columnas para el layout
col1, col2 = st.columns(2)

with col1:
    st.header("Matriz de Operadores por Día")
    
    # Preparar datos para la matriz
    matriz_display = df_matriz.copy()
    # Convertir fecha a formato dd/mm/yyyy
    matriz_display['Fecha'] = matriz_display['Fecha'].dt.strftime('%d/%m/%Y')
    # Eliminar columnas id y mantener solo las columnas necesarias
    columnas_operadores = ['Fecha', 'BS AS', 'CA', 'EP', 'FB', 'MT', 'NP', 'TDLA']
    matriz_display = matriz_display[columnas_operadores]
    # Establecer Fecha como índice
    matriz_display.set_index('Fecha', inplace=True)
    
    # Crear un estilo para el heatmap
    def highlight_values(val):
        if pd.isna(val):
            return ''
        normalized_val = (val - matriz_display.select_dtypes(include=[np.number]).min().min()) / \
                        (matriz_display.select_dtypes(include=[np.number]).max().max() - 
                         matriz_display.select_dtypes(include=[np.number]).min().min())
        color = f'background-color: rgba(255, 99, 71, {normalized_val})'
        return color
    
    # Aplicar estilo y mostrar la matriz
    st.dataframe(
        matriz_display.style
        .apply(lambda x: [highlight_values(v) for v in x])
        .format("{:.0f}")
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black')]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ]),
        height=400
    )

with col2:
    st.header("Operaciones por Operador")

    # Obtener lista única de operadores
    operadores = sorted(df_operaciones['Operador'].unique())

    # Crear filtro multiselect para operadores
    operadores_seleccionados = st.multiselect(
        'Seleccionar Operadores:',
        operadores,
        default=operadores
    )

    # Filtrar primero por operadores seleccionados
    df_filtrado = df_operaciones[
        df_operaciones['Operador'].isin(operadores_seleccionados)
    ]
    
    # Filtrar solo los registros que tienen cantidad de operaciones mayor a 0
    df_filtrado = df_filtrado[df_filtrado['Cantidad Operaciones'] > 0]
    
    # Ordenar por fecha
    df_filtrado = df_filtrado.sort_values('Fecha')

    # Convertir las fechas a formato string para tratarlas como categorías
    df_filtrado['Fecha_str'] = df_filtrado['Fecha'].dt.strftime('%d/%m/%Y')

    # Crear gráfico de barras interactivo con Plotly
    fig_barras = px.bar(
        df_filtrado,
        x='Fecha_str',  # Usar la versión string de la fecha
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
        height=600,
        xaxis={'type': 'category'},  # Forzar eje x como categoría
        xaxis_tickmode='array'  # Asegurar que se muestren todas las fechas
    )

    # Mostrar el gráfico
    st.plotly_chart(fig_barras, use_container_width=True)