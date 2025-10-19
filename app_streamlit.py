import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import os
from supabase_connection import (
    fetch_table_data, 
    login_user, 
    logout_user, 
    get_user_session
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Operaciones Financieras",
    page_icon="📊",
    layout="wide"
)

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

def login():
    try:
        email = st.session_state.email
        password = st.session_state.password
        
        user = login_user(email, password)
        if user:
            st.session_state['authenticated'] = True
            st.session_state['user'] = user
            st.rerun()
        else:
            st.error('Credenciales incorrectas')
    except Exception as e:
        st.error(f'Error al iniciar sesión: {str(e)}')

def logout():
    if logout_user():
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.rerun()

# Página de login
if not st.session_state['authenticated']:
    st.title("🔐 Acceso al Sistema")
    
    with st.form("login_form"):
        st.text_input("Email", key="email")
        st.text_input("Contraseña", type="password", key="password")
        st.form_submit_button("Iniciar Sesión", on_click=login)

else:
    # Mostrar botón de logout
    st.sidebar.button("Cerrar Sesión", on_click=logout)
    
    # Mostrar email del usuario
    st.sidebar.info(f"Usuario: {st.session_state['user'].email}")
    
    # Contenido principal del dashboard
    st.title("📊 Análisis de Operaciones Financieras")



df_matriz = fetch_table_data("sgto_matriz_operadores_dias")
df_operaciones = fetch_table_data("sgto_operaciones_operador_por_dia")
metricas = fetch_table_data("sgto_montos_usd_tdc")
historico_caja = fetch_table_data("sgto_historico_caja")
tabla_sgto_caja = fetch_table_data("sgto_tabla_datos")
tabla_tdc = fetch_table_data("sgto_tabla_tdc")
def fetch_last_update():
    update_log = fetch_table_data("sgto_log_entry")
    if not update_log.empty:
        last_update = update_log['Ultimo Update'].max()
        try:
            datetime_obj = pd.to_datetime(last_update)
            if pd.isna(datetime_obj):
                return "No disponible"
            return datetime_obj.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return "No disponible"
    return "No disponible"
last_update = fetch_last_update()
# Convertir fechas al formato correcto
df_matriz['Fecha'] = pd.to_datetime(df_matriz['Fecha'], format='%d/%m/%Y')
df_operaciones['Fecha'] = pd.to_datetime(df_operaciones['Fecha'], format='%d/%m/%Y')


# App
st.title("📊 Análisis de Operaciones Financieras")
st.info(f'Última actualización: {last_update}')
col1a, col2a = st.columns(2)

with col1a:
    # Mostrar métricas principales
    st.header("Métricas Principales")
    
    # Formatear los números en formato español con 2 decimales
    monto_usd_ayer = f"${metricas['Monto USD ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tdc_ayer = f"$ {metricas['TdC ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_usd_hoy = f"${metricas['Monto USD hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tdc_hoy = f"$ {metricas['TdC hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Crear cuatro columnas para las métricas
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)

    with met_col1:
        st.metric(label="Monto USD Ayer", value=monto_usd_ayer)
    with met_col2:        
        st.metric(label="Tasa de Cambio Ayer", value=tdc_ayer)
    with met_col3:
        st.metric(label="Monto USD Hoy", value=monto_usd_hoy)
    with met_col4:
        st.metric(label="Tasa de Cambio Hoy", value=tdc_hoy)

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
        ])
        .hide(axis='index'),
        height=400
    )

    # Grafico de lineas con tipo de cambio promedio max y min
    tabla_tdc['Fecha'] = pd.to_datetime(tabla_tdc['Fecha'])
    # Sort by date
    tabla_tdc = tabla_tdc.sort_values('Fecha')

    # Create figure with secondary y axis
    fig_tdc = px.line(tabla_tdc, x='Fecha', y=['TC Prom', 'TC_min', 'TC_max'],
                      title='Evolución del Tipo de Cambio',
                      labels={'TC_min': 'Min', 'TC_max': 'Max'})

    fig_tdc.update_layout(
        height=600,
        xaxis=dict(tickformat='%d/%m/%Y', title=''),
        showlegend=False,
        yaxis=dict(range=[1300, 1600], title='')
    )

    st.plotly_chart(fig_tdc, use_container_width=True)

with col2a:
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

st.markdown("""---""")
# Sección de seguimiento de caja y ganancias
st.header("Seguimiento caja y ganancias")

# Obtener datos
historico_caja = fetch_table_data("sgto_historico_caja")
tabla_sgto_caja = fetch_table_data("sgto_tabla_datos")
historico_caja['Fecha'] = pd.to_datetime(historico_caja['Fecha'])

def format_currency(val):
    return f"${val:,.0f}"

def color_percentage(val):
    try:
        val_num = float(val)
        color = 'red' if val_num < 0 else 'green'
        return f'color: {color}'
    except:
        return ''

historico_display = historico_caja.copy()
historico_display = historico_display.drop('id', axis=1)
historico_display['Fecha'] = historico_display['Fecha'].dt.strftime('%d/%m/%Y')

col1b, col2b = st.columns([1, 2])
with col1b: 
# Crear estilo para histórico de caja
    st.subheader("Histórico de Caja")
    st.dataframe(
        historico_display.style
        .format({
            'Total Caja': format_currency,
            'Ganancias': format_currency
        })
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black')]},
            {'selector': 'td', 'props': [('text-align', 'right')]}
        ])
        .hide(axis='index'),
        height=400
    )
with col2b:
    # Gráfico de línea para Ganancias
    fig_ganancias = px.line(
        historico_caja,
        x='Fecha',
        y='Ganancias',
        title='Evolución de Ganancias',
        markers=True
    )

    fig_ganancias.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Ganancias ($)',
        height=400,
        xaxis_tickformat='%d/%m/%Y',
        yaxis_tickformat='$,.0f'
    )

    st.plotly_chart(fig_ganancias, use_container_width=True)

# Formatear tabla de seguimiento de caja
st.subheader("Resumen y proyecciones")
tabla_display = tabla_sgto_caja.copy()
tabla_display = tabla_display.drop('id', axis=1)

# Crear estilo para tabla de seguimiento
st.dataframe(
    tabla_display.style
    .format({
        'HOY': format_currency,
        'ACUM MES': format_currency,
        'PROM x DIA': format_currency,
        'VAR MA': '{:.1%}',
        'PROY MES': format_currency,
        'VAR PROY': '{:.1%}',
        'Obj': format_currency
    })
    .applymap(color_percentage, subset=['VAR MA', 'VAR PROY'])
    .set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black')]},
        {'selector': 'td', 'props': [('text-align', 'right')]}
    ])
    .hide(axis='index'),
    height=200
)


