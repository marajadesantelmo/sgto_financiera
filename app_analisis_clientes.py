def show_page_analisis_clientes():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from supabase_connection import fetch_table_data

    # Fetch data
    sgto_operaciones_usd_por_cliente = fetch_table_data("sgto_operaciones_usd_por_cliente")
    top20 = fetch_table_data("sgto_top_20_participacion_operaciones_usd_por_cliente")

    st.title("📊 Análisis de Clientes")

    # Check if data is available
    if sgto_operaciones_usd_por_cliente is None or sgto_operaciones_usd_por_cliente.empty:
        st.warning("No hay datos de operaciones por cliente disponibles")
        return

    if top20 is None or top20.empty:
        st.warning("No hay datos de top 20 clientes disponibles")
        return

    # Layout with two columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Top 20 Clientes por Participación")
        
        # Prepare top20 display
        try:
            top20_display = top20.copy()
            if 'id' in top20_display.columns:
                top20_display = top20_display.drop('id', axis=1)
            
            # Format currency columns
            def format_currency(val):
                try:
                    return f"${val:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    return val

            def format_percentage(val):
                try:
                    return f"{val:.2f}%"
                except:
                    return val

            # Display styled table
            st.dataframe(
                top20_display.style
                .format({
                    'Monto operado en el mes': format_currency,
                    'Porcentaje': format_percentage
                })
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black'), ('font-weight', 'bold')]},
                    {'selector': 'td', 'props': [('text-align', 'right')]}
                ])
                .hide(axis='index'),
                height=600,
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al procesar la tabla Top 20: {str(e)}")

    with col2:
        st.header("Distribución de Participación")
        
        # Create pie chart
        try:
            # Prepare data for pie chart
            pie_data = top20.copy()
            
            # Create pie chart with plotly
            fig = px.pie(
                pie_data,
                values='Porcentaje',
                names='Cliente',
                title='Participación por Cliente (%)',
                hole=0.4  # Donut chart
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>Participación: %{value:.2f}%<br>Monto: $%{customdata:,.0f}<extra></extra>',
                customdata=pie_data['Monto operado en el mes']
            )
            
            fig.update_layout(
                height=600,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(size=9)
                ),
                margin=dict(l=20, r=150, t=50, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al generar el gráfico: {str(e)}")

    # Full table section
    st.markdown("---")
    st.header("Detalle Completo de Operaciones por Cliente")
    
    try:
        # Add search/filter functionality
        search_term = st.text_input("🔍 Buscar cliente", placeholder="Ingrese nombre del cliente...")
        
        # Prepare full table display
        full_display = sgto_operaciones_usd_por_cliente.copy()
        if 'id' in full_display.columns:
            full_display = full_display.drop('id', axis=1)
        
        # Filter by search term
        if search_term:
            full_display = full_display[
                full_display['Cliente'].str.contains(search_term, case=False, na=False)
            ]
        
        # Add metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            total_clientes = len(full_display)
            st.metric("Total Clientes", f"{total_clientes:,}")
        with col_b:
            total_operaciones = full_display['Cantidad Operaciones'].sum() if not full_display.empty else 0
            st.metric("Total Operaciones", f"{total_operaciones:,}")
        with col_c:
            total_monto = full_display['Monto operado en el mes'].sum() if not full_display.empty else 0
            st.metric("Monto Total USD", f"${total_monto:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Display full table
        st.dataframe(
            full_display.style
            .format({
                'Monto operado en el mes': format_currency
            })
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('text-align', 'right')]}
            ])
            .hide(axis='index'),
            height=400,
            use_container_width=True
        )
        
        st.caption(f"Mostrando {len(full_display)} de {len(sgto_operaciones_usd_por_cliente)} clientes")
        
    except Exception as e:
        st.error(f"Error al procesar la tabla completa: {str(e)}")
