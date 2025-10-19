import streamlit as st
import pandas as pd
import plotly.express as px
from supabase_connection import fetch_table_data

def fetch_data():
    """Fetch required data for Cash Monitoring page"""
    data = {
        'historico_caja': fetch_table_data("sgto_historico_caja"),
        'tabla_sgto_caja': fetch_table_data("sgto_tabla_datos")
    }
    
    # Convert dates
    data['historico_caja']['Fecha'] = pd.to_datetime(data['historico_caja']['Fecha'])
    
    return data

# Page config
st.set_page_config(page_title="Seguimiento Caja", page_icon="💰", layout="wide")

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

# Title
st.title("💰 Seguimiento de Caja y Ganancias")

def format_currency(val):
    return f"${val:,.0f}"

def color_percentage(val):
    try:
        val_num = float(val)
        color = 'red' if val_num < 0 else 'green'
        return f'color: {color}'
    except:
        return ''

# Display historical data and chart
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Histórico de Caja")
    historico_display = data['historico_caja'].copy()
    historico_display = historico_display.drop('id', axis=1)
    historico_display['Fecha'] = historico_display['Fecha'].dt.strftime('%d/%m/%Y')
    
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

with col2:
    fig_ganancias = px.line(
        data['historico_caja'],
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

# Summary and projections table
st.subheader("Resumen y proyecciones")
tabla_display = data['tabla_sgto_caja'].copy()
tabla_display = tabla_display.drop('id', axis=1)

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