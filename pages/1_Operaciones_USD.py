import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from supabase_connection import fetch_table_data

def fetch_data():
    """Fetch required data for USD Operations page"""
    data = {
        'metricas': fetch_table_data("sgto_montos_usd_tdc"),
        'matriz': fetch_table_data("sgto_matriz_operadores_dias"),
        'operaciones': fetch_table_data("sgto_operaciones_operador_por_dia"),
        'tabla_tdc': fetch_table_data("sgto_tabla_tdc")
    }
    
    # Convert dates
    data['matriz']['Fecha'] = pd.to_datetime(data['matriz']['Fecha'], format='%d/%m/%Y')
    data['operaciones']['Fecha'] = pd.to_datetime(data['operaciones']['Fecha'], format='%d/%m/%Y')
    data['tabla_tdc']['Fecha'] = pd.to_datetime(data['tabla_tdc']['Fecha'])
    
    return data

# Page config
st.set_page_config(page_title="Operaciones USD", page_icon="💵", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Por favor, inicie sesión en la página principal.")
    st.stop()

# Auto-refresh setup
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = pd.Timestamp.now()

# Check if 3 minutes have passed since last refresh
if (pd.Timestamp.now() - st.session_state['last_refresh']).total_seconds() > 180:
    st.session_state['last_refresh'] = pd.Timestamp.now()
    st.rerun()

# Fetch data
data = fetch_data()

# Title and layout
st.title("💵 Operaciones USD")
col1, col2 = st.columns(2)

with col1:
    # Métricas Principales
    st.header("Métricas Principales")
    
    # Format numbers in Spanish format
    monto_usd_ayer = f"${data['metricas']['Monto USD ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tdc_ayer = f"$ {data['metricas']['TdC ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_usd_hoy = f"${data['metricas']['Monto USD hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tdc_hoy = f"$ {data['metricas']['TdC hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    with met_col1:
        st.metric(label="Monto USD Ayer", value=monto_usd_ayer)
    with met_col2:        
        st.metric(label="Tasa de Cambio Ayer", value=tdc_ayer)
    with met_col3:
        st.metric(label="Monto USD Hoy", value=monto_usd_hoy)
    with met_col4:
        st.metric(label="Tasa de Cambio Hoy", value=tdc_hoy)

    # Matriz de Operadores
    st.header("Matriz de Operadores por Día")
    matriz_display = data['matriz'].copy()
    matriz_display['Fecha'] = matriz_display['Fecha'].dt.strftime('%d/%m/%Y')
    columnas_operadores = ['Fecha', 'BS AS', 'CA', 'EP', 'FB', 'MT', 'NP', 'TDLA']
    matriz_display = matriz_display[columnas_operadores]
    matriz_display.set_index('Fecha', inplace=True)
    
    def highlight_values(val):
        if pd.isna(val):
            return ''
        normalized_val = (val - matriz_display.select_dtypes(include=[np.number]).min().min()) / \
                        (matriz_display.select_dtypes(include=[np.number]).max().max() - 
                         matriz_display.select_dtypes(include=[np.number]).min().min())
        return f'background-color: rgba(255, 99, 71, {normalized_val})'
    
    st.dataframe(
        matriz_display.style
        .apply(lambda x: [highlight_values(v) for v in x])
        .format("{:.0f}")
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black')]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ])
        .hide(axis='index'),
        height=400
    )

    # Gráfico de tipo de cambio
    fig_tdc = px.line(
        data['tabla_tdc'].sort_values('Fecha'),
        x='Fecha',
        y=['TC Prom', 'TC_min', 'TC_max'],
        title='Evolución del Tipo de Cambio',
        labels={'TC_min': 'Min', 'TC_max': 'Max'}
    )

    fig_tdc.update_layout(
        height=600,
        xaxis=dict(tickformat='%d/%m/%Y', title=''),
        showlegend=False,
        yaxis=dict(range=[1300, 1600], title='')
    )

    st.plotly_chart(fig_tdc, use_container_width=True)

with col2:
    st.header("Operaciones por Operador")
    
    operadores = sorted(data['operaciones']['Operador'].unique())
    operadores_seleccionados = st.multiselect(
        'Seleccionar Operadores:',
        operadores,
        default=operadores
    )

    df_filtrado = data['operaciones'][
        data['operaciones']['Operador'].isin(operadores_seleccionados)
    ]
    df_filtrado = df_filtrado[df_filtrado['Cantidad Operaciones'] > 0]
    df_filtrado = df_filtrado.sort_values('Fecha')
    df_filtrado['Fecha_str'] = df_filtrado['Fecha'].dt.strftime('%d/%m/%Y')

    fig_barras = px.bar(
        df_filtrado,
        x='Fecha_str',
        y='Cantidad Operaciones',
        color='Operador',
        title='Operaciones por Operador y Día',
        barmode='group'
    )

    fig_barras.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Cantidad de Operaciones',
        xaxis_tickangle=-45,
        showlegend=True,
        height=600,
        xaxis={'type': 'category'},
        xaxis_tickmode='array'
    )

    st.plotly_chart(fig_barras, use_container_width=True)