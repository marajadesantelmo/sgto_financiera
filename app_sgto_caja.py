def show_page_caja():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from supabase_connection import fetch_table_data
    # Fetch data
    historico_caja = fetch_table_data("sgto_historico_caja")
    tabla_sgto_caja = fetch_table_data("sgto_tabla_datos")


    st.header("Seguimiento caja y ganancias")

    def format_currency(val):
        return f"${val:,.0f}"

    def color_percentage(val):
        try:
            val_num = float(val)
            color = 'red' if val_num < 0 else 'green'
            return f'color: {color}'
        except:
            return ''

    col1b, col2b = st.columns([1, 2])
    
    try:
        if historico_caja is not None and not historico_caja.empty:
            # Procesar datos del histórico
            historico_display = historico_caja.copy()
            historico_display = historico_display.drop('id', axis=1)
            historico_display['Fecha'] = pd.to_datetime(historico_display['Fecha']).dt.strftime('%d/%m/%Y')

            with col1b:
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
        else:
            with col1b:
                st.warning("No hay datos históricos de caja disponibles")
    except Exception as e:
        with col1b:
            st.error(f"Error al procesar el histórico de caja: {str(e)}")
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

    st.plotly_chart(fig_ganancias, width="stretch")

    # Formatear tabla de seguimiento de caja
    st.subheader("Resumen y proyecciones")
    try:
        if tabla_sgto_caja is not None and not tabla_sgto_caja.empty:
            tabla_display = tabla_sgto_caja.copy()
            tabla_display = tabla_display.drop('id', axis=1)

            # Crear estilo para tabla de seguimiento
            styled_df = tabla_display.style.format({
                'HOY': format_currency,
                'ACUM MES': format_currency,
                'PROM x DIA': format_currency,
                'VAR MA': '{:.1%}',
                'PROY MES': format_currency,
                'VAR PROY': '{:.1%}',
                'Obj': format_currency
            })

            # Apply color to percentage columns
            for col in ['VAR MA', 'VAR PROY']:
                if col in tabla_display.columns:
                    styled_df = styled_df.map(color_percentage, subset=[col])

            st.dataframe(
                styled_df.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black')]},
                    {'selector': 'td', 'props': [('text-align', 'right')]}
                ]).hide(axis='index'),
                height=200
            )
        else:
            st.warning("No hay datos de seguimiento de caja disponibles")
    except Exception as e:
        st.error(f"Error al procesar la tabla de seguimiento: {str(e)}")