


def show_page_operaciones():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    from supabase_connection import fetch_table_data

    # Fetch and display last update info


    def fetch_last_update():
        update_log = fetch_table_data("sgto_log_entry")
        if update_log is not None and not update_log.empty:
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

    # Fetch all necessary data
    sgto_operaciones_usd_por_cliente = fetch_table_data("sgto_operaciones_usd_por_cliente")
    top20 = fetch_table_data("sgto_top_20_participacion_operaciones_usd_por_cliente")



    st.markdown("""---""")