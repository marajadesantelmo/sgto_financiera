import streamlit as st
st.set_page_config(page_title="Seguimiento de operaciones financieras", 
                   page_icon="📊", 
                   layout="wide")
from supabase_connection import fetch_table_data

sgto_matriz_operadores_dias = fetch_table_data("sgto_matriz_operadores_dias")
sgto_operaciones_operador_por_dia = fetch_table_data("sgto_operaciones_operador_por_dia")


st.title("📊 Seguimiento de operaciones financieras" )