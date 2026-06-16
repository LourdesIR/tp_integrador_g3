import streamlit as st
import pandas as pd
import numpy as np


# ========== PRIMERO DEFINIR PLOTLY_AVAILABLE ==========
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ========== REVISIÓN: Forzar reinstalación si no está disponible ==========
if not PLOTLY_AVAILABLE:
    st.warning("⚠️ Plotly no está instalado. Las visualizaciones se mostrarán en versión simplificada.")
    st.info("💡 Para mejores gráficos, asegurate que plotly esté en requirements.txt y reiniciá la app.")

st.set_page_config(page_title="Análisis Exploratorio", layout="wide")

# Verificar datos
if 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos limpios cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

df = st.session_state['df_limpio'].copy()

st.title("📈 Actividades 5-8: Estadística Descriptiva y Visualizaciones")
st.markdown("---")

# ========== FILTROS DINÁMICOS GLOBALES ==========
st.sidebar.header("🔍 Filtros Dinámicos")

# Detectar columnas disponibles
columnas_disponibles = {
    'provincia': 'Provincia' if 'Provincia' in df.columns else None,
    'actividad': 'Actividad' if 'Actividad' in df.columns else None,
    'tecnificacion': 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None,
    'riego': 'Uso_Riego' if 'Uso_Riego' in df.columns else None,
    'produccion': 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None,
    'rentabilidad': 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None,
    'costo': 'Costo_Produccion' if 'Costo_Produccion' in df.columns else None,
    'sustentabilidad': 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None,
    'superficie': 'Superficie_Hectareas' if 'Superficie_Hectareas' in df.columns else None,
    'empleados': 'Cantidad_Empleados' if 'Cantidad_Empleados' in df.columns else None
}

# Inicializar df_filtrado
df_filtrado = df.copy()

# Filtro por Provincia
if columnas_disponibles['provincia']:
    prov_seleccionadas = st.sidebar.multiselect(
        "🌍 Seleccionar Provincia(s)",
        options=sorted(df[columnas_disponibles['provincia']].dropna().unique()),
        default=[],
        help="Filtrar por una o más provincias"
    )
    if prov_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas_disponibles['provincia']].isin(prov_seleccionadas)]

# Filtro por Actividad
if columnas_disponibles['actividad']:
    act_seleccionadas = st.sidebar.multiselect(
        "🌱 Seleccionar Actividad(es)",
        options=sorted(df[columnas_disponibles['actividad']].dropna().unique()),
        default=[],
        help="Filtrar por tipo de producción"
    )
    if act_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas_disponibles['actividad']].isin(act_seleccionadas)]

# Filtro por Nivel de Tecnificación
if columnas_disponibles['tecnificacion']:
    tech_seleccionadas = st.sidebar.multiselect(
        "⚙️ Nivel de Tecnificación",
        options=sorted(df[columnas_disponibles['tecnificacion']].dropna().unique()),
        default=[],
        help="Filtrar por nivel tecnológico"
    )
    if tech_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas_disponibles['tecnificacion']].isin(tech_seleccionadas)]

# Filtro por Uso de Riego
if columnas_disponibles['riego']:
    riego_seleccionado = st.sidebar.radio(
        "💧 Uso de Riego",
        options=["Todos", "Sí", "No"],
        horizontal=True
    )
    if riego_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado[columnas_disponibles['riego']].astype(str).str.capitalize() == riego_seleccionado]

# Filtro por rango de superficie
if columnas_disponibles['superficie']:
    superficie_min, superficie_max = st.sidebar.slider(
        "📏 Rango de Superficie (hectáreas)",
        min_value=float(df[columnas_disponibles['superficie']].min()),
        max_value=float(df[columnas_disponibles['superficie']].max()),
        value=(float(df[columnas_disponibles['superficie']].min()), 
               float(df[columnas_disponibles['superficie']].max()))
    )
    df_filtrado = df_filtrado[
        (df_filtrado[columnas_disponibles['superficie']] >= superficie_min) & 
        (df_filtrado[columnas_disponibles['superficie']] <= superficie_max)
    ]

# Mostrar resumen de filtros
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Registros después de filtros: **{len(df_filtrado):,}**")

# Botón para resetear filtros
if st.sidebar.button("🔄 Resetear todos los filtros"):
    st.cache_data.clear()
    st.rerun()

st.markdown(f"**📊 Mostrando {len(df_filtrado):,} registros** (de {len(df):,} totales)")
st.markdown("---")

# ========== ACTIVIDAD 5: ESTADÍSTICA DESCRIPTIVA ==========
st.header("📊 Actividad 5: Estadística Descriptiva")

with st.expander("Ver estadísticas completas", expanded=True):
    columnas_numericas = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()
    
    if columnas_numericas:
        stats = df_filtrado[columnas_numericas].describe().T
        stats['mediana'] = df_filtrado[columnas_numericas].median()
        stats['moda'] = df_filtrado[columnas_numericas].mode().iloc[0] if len(df_filtrado[columnas_numericas].mode()) > 0 else None
        stats['rango'] = stats['max'] - stats['min']
        
        st.dataframe(stats[['mean', 'mediana', 'std', 'min', 'max', 'rango']].round(2), 
                     use_container_width=True)
        
        st.markdown("""
        **📝 Interpretación:**
        - Si la **media > mediana** → hay valores atípicos altos
        - **Desviación estándar alta** → gran variabilidad entre explotaciones
        - **Rango amplio** → diferencia significativa entre explotaciones
        """)

# ========== ACTIVIDAD 6: PERFILES PRODUCTIVOS ==========
st.header("👥 Actividad 6: Perfiles Productivos")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Por Provincia", 
    "🌱 Por Actividad", 
    "⚙️ Por Tecnificación", 
    "💧 Por Riego",
    "📏 Por Superficie"
])

with tab1:
    if columnas_disponibles['provincia']:
        col1, col2 = st.columns(2)
        
        with col1:
            prod_prov = df_filtrado.groupby(columnas_disponibles['provincia'])[columnas_disponibles['produccion']].mean().sort_values(ascending=False)
            st.subheader("🌾 Producción promedio por provincia")
            st.dataframe(prod_prov.to_frame().round(1), use_container_width=True)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(x=prod_prov.index, y=prod_prov.values,
                             title='Producción promedio por provincia',
                             color=prod_prov.values, color_continuous_scale='Greens')
                fig.update_layout(xaxis_title="Provincia", yaxis_title="Producción (toneladas)")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if columnas_disponibles['rentabilidad']:
                rent_prov = df_filtrado.groupby(columnas_disponibles['provincia'])[columnas_disponibles['rentabilidad']].mean().sort_values(ascending=False)
                st.subheader("💰 Rentabilidad promedio por provincia")
                st.dataframe(rent_prov.to_frame().round(1), use_container_width=True)
                
                if PLOTLY_AVAILABLE:
                    fig = px.bar(x=rent_prov.index, y=rent_prov.values,
                                 title='Rentabilidad promedio por provincia',
                                 color=rent_prov.values, color_continuous_scale='Blues')
                    fig.update_layout(xaxis_title="Provincia", yaxis_title="Rentabilidad (%)")
                    st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 **Insight:** Mayor producción no implica mayor rentabilidad")

with tab2:
    if columnas_disponibles['actividad']:
        col1, col2 = st.columns(2)
        
        with col1:
            prod_act = df_filtrado.groupby(columnas_disponibles['actividad'])[columnas_disponibles['produccion']].mean().sort_values(ascending=False)
            st.subheader("🌾 Producción promedio por actividad")
            st.dataframe(prod_act.to_frame().round(1), use_container_width=True)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(x=prod_act.index, y=prod_act.values,
                             title='Producción promedio por actividad',
                             color=prod_act.values, color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if columnas_disponibles['rentabilidad']:
                rent_act = df_filtrado.groupby(columnas_disponibles['actividad'])[columnas_disponibles['rentabilidad']].mean().sort_values(ascending=False)
                st.subheader("💰 Rentabilidad promedio por actividad")
                st.dataframe(rent_act.to_frame().round(1), use_container_width=True)
                
                if PLOTLY_AVAILABLE:
                    fig = px.bar(x=rent_act.index, y=rent_act.values,
                                 title='Rentabilidad promedio por actividad',
                                 color=rent_act.values, color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 **Insight:** Maíz y Fruticultura suelen ser las actividades más rentables")

with tab3:
    if columnas_disponibles['tecnificacion']:
        tech_stats = df_filtrado.groupby(columnas_disponibles['tecnificacion']).agg({
            col: 'mean' for col in [columnas_disponibles['produccion'], 
                                      columnas_disponibles['rentabilidad'],
                                      columnas_disponibles['sustentabilidad']] 
            if col is not None
        }).round(2)
        
        st.dataframe(tech_stats, use_container_width=True)
        
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Producción (ton)', x=tech_stats.index, y=tech_stats[columnas_disponibles['produccion']], 
                                 yaxis='y', marker_color='green'))
            fig.add_trace(go.Bar(name='Rentabilidad (%)', x=tech_stats.index, y=tech_stats[columnas_disponibles['rentabilidad']], 
                                 yaxis='y2', marker_color='blue'))
            if columnas_disponibles['sustentabilidad']:
                fig.add_trace(go.Scatter(name='Sustentabilidad', x=tech_stats.index, y=tech_stats[columnas_disponibles['sustentabilidad']],
                                         yaxis='y2', mode='lines+markers', line=dict(color='red', width=3)))
            
            fig.update_layout(title='Impacto del nivel de tecnificación',
                              yaxis=dict(title='Producción (toneladas)', side='left'),
                              yaxis2=dict(title='Porcentaje (%)', side='right', overlaying='y'))
            st.plotly_chart(fig, use_container_width=True)
        
        st.warning("⚠️ **Conclusión clave:** Mayor tecnificación aumenta producción y sustentabilidad, pero NO garantiza mayor rentabilidad")

with tab4:
    if columnas_disponibles['riego'] and columnas_disponibles['rentabilidad']:
        col1, col2 = st.columns(2)
        
        with col1:
            riego_prod = df_filtrado.groupby(columnas_disponibles['riego'])[columnas_disponibles['produccion']].mean()
            st.subheader("🌾 Producción según riego")
            st.dataframe(riego_prod.to_frame().round(1), use_container_width=True)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(x=riego_prod.index, y=riego_prod.values,
                             title='Producción promedio: Con riego vs Sin riego',
                             color=riego_prod.values, color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            riego_rent = df_filtrado.groupby(columnas_disponibles['riego'])[columnas_disponibles['rentabilidad']].mean()
            st.subheader("💰 Rentabilidad según riego")
            st.dataframe(riego_rent.to_frame().round(1), use_container_width=True)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(x=riego_rent.index, y=riego_rent.values,
                             title='Rentabilidad promedio: Con riego vs Sin riego',
                             color=riego_rent.values, color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Insight:** El riego mejora producción pero no necesariamente rentabilidad por los costos asociados")

with tab5:
    if columnas_disponibles['superficie']:
        # Crear rangos de superficie
        df_filtrado['Rango_Superficie'] = pd.cut(
            df_filtrado[columnas_disponibles['superficie']], 
            bins=[0, 100, 250, 500, float('inf')],
            labels=['Hasta 100 ha', '101-250 ha', '251-500 ha', 'Más de 500 ha']
        )
        
        sup_stats = df_filtrado.groupby('Rango_Superficie', observed=False).agg({
            columnas_disponibles['produccion']: 'mean',
            columnas_disponibles['rentabilidad']: 'mean'
        }).round(2)
        
        st.dataframe(sup_stats, use_container_width=True)
        
        if PLOTLY_AVAILABLE:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=sup_stats.index, y=sup_stats[columnas_disponibles['produccion']], 
                                 name='Producción', marker_color='green'), secondary_y=False)
            fig.add_trace(go.Scatter(x=sup_stats.index, y=sup_stats[columnas_disponibles['rentabilidad']], 
                                     name='Rentabilidad', mode='lines+markers', 
                                     line=dict(color='blue', width=3)), secondary_y=True)
            fig.update_layout(title='Producción y rentabilidad según superficie')
            fig.update_yaxes(title_text="Producción (toneladas)", secondary_y=False)
            fig.update_yaxes(title_text="Rentabilidad (%)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 **Insight:** A mayor superficie, mayor producción, pero la rentabilidad se estabiliza")

# ========== ACTIVIDAD 7: GRÁFICOS ADICIONALES ==========
st.header("🎨 Actividad 7: Visualizaciones Adicionales")

# Gráfico 1: Rentabilidad por actividad (ya lo tenemos, pero lo mostramos destacado)
st.subheader("📊 Gráfico 1: Rentabilidad promedio por actividad productiva")
if columnas_disponibles['actividad'] and columnas_disponibles['rentabilidad'] and PLOTLY_AVAILABLE:
    rent_act = df_filtrado.groupby(columnas_disponibles['actividad'])[columnas_disponibles['rentabilidad']].mean().sort_values(ascending=True)
    fig = px.bar(x=rent_act.values, y=rent_act.index, orientation='h',
                 title='Rentabilidad promedio por actividad',
                 color=rent_act.values, color_continuous_scale='Viridis',
                 labels={'x': 'Rentabilidad (%)', 'y': ''})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Gráfico de barras horizontal para fácil comparación entre actividades")

# Gráfico 2: Producción promedio por provincia
st.subheader("📊 Gráfico 2: Producción promedio por provincia")
if columnas_disponibles['provincia'] and columnas_disponibles['produccion'] and PLOTLY_AVAILABLE:
    prod_prov = df_filtrado.groupby(columnas_disponibles['provincia'])[columnas_disponibles['produccion']].mean().sort_values(ascending=False)
    fig = px.bar(x=prod_prov.index, y=prod_prov.values,
                 title='Producción promedio por provincia',
                 color=prod_prov.values, color_continuous_scale='Greens',
                 labels={'x': 'Provincia', 'y': 'Producción (toneladas)'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Permite identificar provincias líderes en producción")

# Gráfico 3: Distribución de superficie explotada (gráfico de líneas)
st.subheader("📊 Gráfico 3: Distribución de superficie explotada")
if columnas_disponibles['superficie'] and PLOTLY_AVAILABLE:
    superficie_ordenada = df_filtrado[columnas_disponibles['superficie']].sort_values().reset_index(drop=True)
    fig = px.line(x=superficie_ordenada.index, y=superficie_ordenada.values,
                  title='Distribución de superficie explotada',
                  labels={'x': 'Número de explotación (ordenada)', 'y': 'Superficie (hectáreas)'})
    fig.add_hline(y=df_filtrado[columnas_disponibles['superficie']].median(), 
                  line_dash="dash", line_color="red",
                  annotation_text=f"Mediana: {df_filtrado[columnas_disponibles['superficie']].median():.0f} ha")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Muestra la concentración y distribución del tamaño de las explotaciones")

# Gráfico 4: Distribución de costos de producción (gráfico de líneas)
st.subheader("📊 Gráfico 4: Distribución de costos de producción")
if columnas_disponibles['costo'] and PLOTLY_AVAILABLE:
    costos_ordenados = df_filtrado[columnas_disponibles['costo']].sort_values().reset_index(drop=True)
    fig = px.line(x=costos_ordenados.index, y=costos_ordenados.values,
                  title='Distribución de costos de producción',
                  labels={'x': 'Número de explotación (ordenada)', 'y': 'Costo de producción ($)'})
    fig.add_hline(y=df_filtrado[columnas_disponibles['costo']].median(), 
                  line_dash="dash", line_color="red",
                  annotation_text=f"Mediana: ${df_filtrado[columnas_disponibles['costo']].median():,.0f}")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Permite identificar la concentración de costos")

# Gráfico 5: Diagrama de dispersión - Producción vs Rentabilidad
st.subheader("📊 Gráfico 5: Producción vs Rentabilidad")
if columnas_disponibles['produccion'] and columnas_disponibles['rentabilidad'] and PLOTLY_AVAILABLE:
    fig = px.scatter(df_filtrado.sample(min(1000, len(df_filtrado))), 
                 x=columnas_disponibles['produccion'], 
                 y=columnas_disponibles['rentabilidad'],
                 color=columnas_disponibles['tecnificacion'] if columnas_disponibles['tecnificacion'] else None,
                 hover_data=[columnas_disponibles['provincia'], columnas_disponibles['actividad']] if columnas_disponibles['provincia'] else None,
                 title='Relación: Producción vs Rentabilidad',
                 opacity=0.6,
                 labels={columnas_disponibles['produccion']: 'Producción (toneladas)',
                         columnas_disponibles['rentabilidad']: 'Rentabilidad (%)'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Muestra que no hay correlación directa entre producción y rentabilidad")

# Gráfico 6: Nivel de tecnificación vs Rentabilidad (boxplot)
st.subheader("📊 Gráfico 6: Nivel de tecnificación vs Rentabilidad")
if columnas_disponibles['tecnificacion'] and columnas_disponibles['rentabilidad'] and PLOTLY_AVAILABLE:
    fig = px.box(df_filtrado, x=columnas_disponibles['tecnificacion'], 
                 y=columnas_disponibles['rentabilidad'],
                 title='Distribución de rentabilidad por nivel de tecnificación',
                 color=columnas_disponibles['tecnificacion'],
                 points='all')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Boxplot para visualizar dispersión, mediana y outliers por categoría")

# Gráfico 7: Heatmap de correlación
st.subheader("📊 Gráfico 7: Heatmap de correlación entre variables")
columnas_numericas = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()
if len(columnas_numericas) > 1 and PLOTLY_AVAILABLE:
    corr_matrix = df_filtrado[columnas_numericas].corr()
    fig = px.imshow(corr_matrix, text_auto=True, aspect='auto',
                    color_continuous_scale='RdBu_r',
                    title='Matriz de correlación entre variables numéricas',
                    labels=dict(color='Correlación'))
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Identifica qué variables están más relacionadas con la rentabilidad")

# Gráfico 8: Rentabilidad según uso de riego (gráfico comparativo)
st.subheader("📊 Gráfico 8: Rentabilidad según uso de riego")
if columnas_disponibles['riego'] and columnas_disponibles['rentabilidad'] and PLOTLY_AVAILABLE:
    riego_stats = df_filtrado.groupby(columnas_disponibles['riego'])[columnas_disponibles['rentabilidad']].agg(['mean', 'median', 'std']).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Media', x=riego_stats.index, y=riego_stats['mean'], marker_color='steelblue'))
    fig.add_trace(go.Bar(name='Mediana', x=riego_stats.index, y=riego_stats['median'], marker_color='lightblue'))
    fig.update_layout(title='Comparativa de rentabilidad: Con riego vs Sin riego',
                      yaxis_title='Rentabilidad (%)',
                      barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Justificación:** Compara medidas de tendencia central entre grupos")

# ========== ACTIVIDAD 8: INTERPRETACIÓN ==========
st.header("💡 Actividad 8: Interpretación de visualizaciones")

with st.expander("Ver interpretaciones detalladas", expanded=True):
    st.markdown("""
    ### 📊 Gráfico 1: Rentabilidad promedio por actividad productiva
    
    **¿Qué representa?** Muestra qué tipo de producción genera mayor retorno económico porcentual.
    
    **Justificación de elección:** Gráfico de barras horizontal facilita la comparación entre actividades.
    
    **Información que aporta:** Permite identificar qué cultivos/actividades son más rentables.
    
    **Decisiones que respalda:** Orientar la producción hacia actividades más rentables.
    
    ---
    
    ### 📊 Gráfico 5: Producción vs Rentabilidad (dispersión)
    
    **¿Qué representa?** Relación entre el volumen producido y la rentabilidad obtenida.
    
    **Justificación de elección:** Diagrama de dispersión con línea de tendencia muestra correlación.
    
    **Información que aporta:** No hay correlación directa - alta producción no garantiza alta rentabilidad.
    
    **Decisiones que respalda:** No enfocar todos los recursos solo en aumentar volumen.
    
    ---
    
    ### 📊 Gráfico 6: Tecnificación vs Rentabilidad (boxplot)
    
    **¿Qué representa?** Distribución de rentabilidad según nivel de tecnificación.
    
    **Justificación de elección:** Boxplot muestra mediana, dispersión, cuartiles y outliers.
    
    **Información que aporta:** Niveles bajos tienen mayor variabilidad y rentabilidades extremas.
    
    **Decisiones que respalda:** Evaluar caso por caso antes de invertir en tecnología.
    
    ---
    
    ### 📊 Gráfico 7: Heatmap de correlación
    
    **¿Qué representa?** Correlaciones entre todas las variables numéricas.
    
    **Justificación de elección:** Visualización matricial con escala de colores.
    
    **Información que aporta:** Identifica qué variables están más relacionadas con rentabilidad.
    
    **Decisiones que respalda:** Enfocar esfuerzos en variables con mayor correlación.
    
    ---
    
    ### 📊 Gráfico 8: Rentabilidad según uso de riego
    
    **¿Qué representa?** Comparación de rentabilidad entre explotaciones con y sin riego.
    
    **Justificación de elección:** Barras agrupadas para comparar media y mediana.
    
    **Información que aporta:** Las explotaciones SIN riego muestran mayor rentabilidad promedio.
    
    **Decisiones que respalda:** Evaluar costo-beneficio del riego antes de implementarlo.
    """)

# ========== PERFILES DESTACADOS ==========
st.header("🏆 Perfiles con mayores niveles de producción y rentabilidad")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Top 10 - Mayor Producción")
    if columnas_disponibles['produccion']:
        top_produccion = df_filtrado.nlargest(10, columnas_disponibles['produccion'])[
            [col for col in [columnas_disponibles['provincia'], 
                              columnas_disponibles['actividad'],
                              columnas_disponibles['tecnificacion'],
                              columnas_disponibles['produccion']] if col is not None]
        ]
        st.dataframe(top_produccion, use_container_width=True)

with col2:
    st.subheader("💰 Top 10 - Mayor Rentabilidad")
    if columnas_disponibles['rentabilidad']:
        # Excluir outliers extremos para este top
        df_sin_outliers = df_filtrado[df_filtrado[columnas_disponibles['rentabilidad']] <= 500]
        top_rentabilidad = df_sin_outliers.nlargest(10, columnas_disponibles['rentabilidad'])[
            [col for col in [columnas_disponibles['provincia'], 
                              columnas_disponibles['actividad'],
                              columnas_disponibles['tecnificacion'],
                              columnas_disponibles['rentabilidad']] if col is not None]
        ]
        st.dataframe(top_rentabilidad, use_container_width=True)

st.markdown("---")
st.caption("📌 **Conclusión:** Los perfiles de mayor producción no son necesariamente los más rentables. La rentabilidad depende de una combinación compleja de ingresos, costos, actividad productiva y uso de recursos.")