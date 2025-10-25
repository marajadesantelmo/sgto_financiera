


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
    df_matriz = fetch_table_data("sgto_matriz_operadores_dias")
    df_operaciones = fetch_table_data("sgto_operaciones_operador_por_dia")
    metricas = fetch_table_data("sgto_montos_usd_tdc")
    tabla_tdc = fetch_table_data("sgto_tabla_tdc")

    # Initialize display DataFrames
    matriz_display = pd.DataFrame()

    # Process each DataFrame safely
    try:
        # Process df_matriz
        if df_matriz is not None and not df_matriz.empty:
            df_matriz['Fecha'] = pd.to_datetime(df_matriz['Fecha'], format='%d/%m/%Y')
            matriz_display = df_matriz.copy()

        # Process df_operaciones
        if df_operaciones is not None and not df_operaciones.empty:
            df_operaciones['Fecha'] = pd.to_datetime(df_operaciones['Fecha'], format='%d/%m/%Y')
        
        # Process tabla_tdc
        if tabla_tdc is not None and not tabla_tdc.empty:
            tabla_tdc['Fecha'] = pd.to_datetime(tabla_tdc['Fecha'])
            tabla_tdc = tabla_tdc.sort_values('Fecha')
            
        # Check if any essential data is missing
        missing_data = []
        if matriz_display.empty:
            missing_data.append("Matriz de Operadores")
            
        if missing_data:
            st.warning(f"Algunos datos no están disponibles: {', '.join(missing_data)}")
            
    except Exception as e:
        st.error(f"Error al procesar los datos: {str(e)}")
        st.stop()

    # App title
    st.title("📊 Análisis de Operaciones Financieras")
    st.info(f"Última actualización: {last_update}")

    # Layout setup
    col1a, col2a = st.columns(2)

    with col1a:
        # Mostrar métricas principales
        st.header("Métricas Principales")
        
        # Formatear los números en formato español con 2 decimales
        if metricas is not None and not metricas.empty:
            try:
                monto_usd_ayer = f"${metricas['Monto USD ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                tdc_ayer = f"$ {metricas['TdC ayer'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                monto_usd_hoy = f"${metricas['Monto USD hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                tdc_hoy = f"$ {metricas['TdC hoy'].iloc[0]:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (KeyError, IndexError):
                monto_usd_ayer = tdc_ayer = monto_usd_hoy = tdc_hoy = "No disponible"
        else:
            monto_usd_ayer = tdc_ayer = monto_usd_hoy = tdc_hoy = "No disponible"

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
        if df_matriz is not None and not df_matriz.empty:
            try:
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
                    color = f'background-color: rgba(0, 20, 255, {normalized_val})'
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
            except Exception as e:
                st.error(f"Error al procesar la matriz de operadores: {str(e)}")

        # Grafico de lineas con tipo de cambio promedio max y min
        if tabla_tdc is not None and not tabla_tdc.empty:
            try:
                tabla_tdc['Fecha'] = pd.to_datetime(tabla_tdc['Fecha'])
                # Sort by date
                tabla_tdc = tabla_tdc.sort_values('Fecha')
            except Exception as e:
                st.error(f"Error al procesar los datos de tipo de cambio: {str(e)}")

        # Create figure with secondary y axis
        fig_tdc = px.line(tabla_tdc, x='Fecha', y=['TC Prom', 'TC_min', 'TC_max'],
                        title='Evolución del Tipo de Cambio',
                        labels={'TC_min': 'Min', 'TC_max': 'Max'})

        fig_tdc.update_layout(
            height=600,
            xaxis=dict(tickformat='%d/%m/%Y', title=''),
            showlegend=False,
            yaxis=dict(range=[1300, 1800], title='')
        )

        st.plotly_chart(fig_tdc, use_container_width=True)

    with col2a:
        st.header("Operaciones por Operador")

        try:
            if df_operaciones is not None and not df_operaciones.empty:
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
            else:
                st.warning("No hay datos de operaciones disponibles")
                df_filtrado = pd.DataFrame()
        except Exception as e:
            st.error(f"Error al procesar datos de operaciones: {str(e)}")
            df_filtrado = pd.DataFrame()

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