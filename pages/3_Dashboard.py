import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# Verificar datos
if 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos limpios cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

df = st.session_state['df_limpio'].copy()

st.title("📊 Actividad 9: Dashboard Ejecutivo")
st.markdown("### Sector Agropecuario Argentino - Producción, Costos y Rentabilidad")
st.markdown("---")

# ========== DETECTAR COLUMNAS DISPONIBLES ==========
columnas = {
    'provincia': 'Provincia' if 'Provincia' in df.columns else None,
    'actividad': 'Actividad' if 'Actividad' in df.columns else None,
    'tecnificacion': 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None,
    'riego': 'Uso_Riego' if 'Uso_Riego' in df.columns else None,
    'produccion': 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None,
    'rentabilidad': 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None,
    'costo': 'Costo_Produccion' if 'Costo_Produccion' in df.columns else None,
    'sustentabilidad': 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None,
    'empleados': 'Cantidad_Empleados' if 'Cantidad_Empleados' in df.columns else None,
    'superficie': 'Superficie_Hectareas' if 'Superficie_Hectareas' in df.columns else None,
    'precio': 'Precio_Venta_Tonelada' if 'Precio_Venta_Tonelada' in df.columns else None,
    'ingresos': 'Ingresos' if 'Ingresos' in df.columns else None
}

# ========== SEGMENTADORES (FILTROS) ==========
st.sidebar.header("🔍 Segmentadores")

# Inicializar df_filtrado
df_filtrado = df.copy()

# Filtro por Provincia
if columnas['provincia']:
    prov_seleccionadas = st.sidebar.multiselect(
        "🌍 Provincia",
        options=sorted(df[columnas['provincia']].dropna().unique()),
        default=[],
        help="Seleccionar una o más provincias"
    )
    if prov_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas['provincia']].isin(prov_seleccionadas)]

# Filtro por Actividad
if columnas['actividad']:
    act_seleccionadas = st.sidebar.multiselect(
        "🌱 Actividad productiva",
        options=sorted(df[columnas['actividad']].dropna().unique()),
        default=[],
        help="Seleccionar una o más actividades"
    )
    if act_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas['actividad']].isin(act_seleccionadas)]

# Filtro por Nivel de Tecnificación
if columnas['tecnificacion']:
    tech_seleccionadas = st.sidebar.multiselect(
        "⚙️ Nivel de tecnificación",
        options=sorted(df[columnas['tecnificacion']].dropna().unique()),
        default=[],
        help="Seleccionar nivel tecnológico"
    )
    if tech_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[columnas['tecnificacion']].isin(tech_seleccionadas)]

# Filtro por Uso de Riego
if columnas['riego']:
    riego_seleccionado = st.sidebar.radio(
        "💧 Uso de riego",
        options=["Todos", "Sí", "No"],
        horizontal=True
    )
    if riego_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado[columnas['riego']].astype(str).str.capitalize() == riego_seleccionado]

# Mostrar resumen de filtros
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Registros filtrados: **{len(df_filtrado):,}** de {len(df):,}")

# Botón reset
if st.sidebar.button("🔄 Resetear filtros", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.markdown(f"**📊 Mostrando {len(df_filtrado):,} explotaciones** (total: {len(df):,})")
st.markdown("---")

# ========== KPIs ==========
st.header("📈 Indicadores Clave de Rendimiento (KPIs)")

# Calcular KPIs sobre datos filtrados
kpis = {}

if columnas['produccion']:
    kpis['produccion'] = df_filtrado[columnas['produccion']].mean()
if columnas['rentabilidad']:
    # Excluir outliers extremos para el KPI
    df_rent_filtrado = df_filtrado[df_filtrado[columnas['rentabilidad']] <= 500]
    kpis['rentabilidad'] = df_rent_filtrado[columnas['rentabilidad']].mean()
if columnas['costo']:
    kpis['costo'] = df_filtrado[columnas['costo']].mean()
if columnas['sustentabilidad']:
    kpis['sustentabilidad'] = df_filtrado[columnas['sustentabilidad']].mean()
if columnas['empleados']:
    kpis['empleados'] = df_filtrado[columnas['empleados']].mean()

# Mostrar KPIs en columnas
col1, col2, col3, col4, col5 = st.columns(5)

kpi_config = [
    (col1, 'produccion', '🌾 Producción promedio', 'ton', 0),
    (col2, 'rentabilidad', '💰 Rentabilidad promedio', '%', 1),
    (col3, 'costo', '💸 Costo promedio', '$', 0),
    (col4, 'sustentabilidad', '🌱 Sustentabilidad', '/100', 1),
    (col5, 'empleados', '👥 Empleados promedio', '', 1)
]

for col, kpi_key, label, unidad, decimales in kpi_config:
    if kpi_key in kpis and kpis[kpi_key] is not None and not pd.isna(kpis[kpi_key]):
        valor = kpis[kpi_key]
        if decimales == 0:
            col.metric(label, f"{valor:,.0f} {unidad}")
        else:
            col.metric(label, f"{valor:.1f} {unidad}")
    else:
        col.metric(label, "N/A")

st.markdown("---")

# ========== VISUALIZACIONES INTERACTIVAS ==========
st.header("📊 Visualizaciones Interactivas")

if not PLOTLY_AVAILABLE:
    st.warning("⚠️ Plotly no está instalado. Las visualizaciones se mostrarán en versión simplificada.")
    
    # Versión simplificada sin plotly
    if columnas['actividad'] and columnas['rentabilidad']:
        st.subheader("Rentabilidad por actividad")
        rent_act = df_filtrado.groupby(columnas['actividad'])[columnas['rentabilidad']].mean().sort_values(ascending=False)
        st.bar_chart(rent_act)
    
    if columnas['provincia'] and columnas['produccion']:
        st.subheader("Producción por provincia")
        prod_prov = df_filtrado.groupby(columnas['provincia'])[columnas['produccion']].mean().sort_values(ascending=False)
        st.bar_chart(prod_prov)
    
    if columnas['produccion'] and columnas['rentabilidad']:
        st.subheader("Producción vs Rentabilidad")
        st.scatter_chart(df_filtrado[[columnas['produccion'], columnas['rentabilidad']]].dropna().head(500))

else:
    # Versión completa con plotly
    # Fila 1: Dos gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Rentabilidad por actividad")
        if columnas['actividad'] and columnas['rentabilidad']:
            rent_act = df_filtrado.groupby(columnas['actividad'])[columnas['rentabilidad']].mean().sort_values(ascending=True)
            fig = px.bar(x=rent_act.values, y=rent_act.index, orientation='h',
                         title='Rentabilidad promedio por actividad productiva',
                         color=rent_act.values, color_continuous_scale='Viridis',
                         labels={'x': 'Rentabilidad (%)', 'y': ''})
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos insuficientes para este gráfico")
    
    with col2:
        st.subheader("🌾 Producción por provincia")
        if columnas['provincia'] and columnas['produccion']:
            prod_prov = df_filtrado.groupby(columnas['provincia'])[columnas['produccion']].mean().sort_values(ascending=False)
            fig = px.bar(x=prod_prov.index, y=prod_prov.values,
                         title='Producción promedio por provincia',
                         color=prod_prov.values, color_continuous_scale='Greens',
                         labels={'x': 'Provincia', 'y': 'Producción (toneladas)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos insuficientes para este gráfico")
    
    # Fila 2: Dispersión
    st.subheader("📈 Producción vs Rentabilidad")
    if columnas['produccion'] and columnas['rentabilidad']:
        sample_df = df_filtrado[[columnas['produccion'], columnas['rentabilidad']]].dropna().head(1000)
        fig = px.scatter(sample_df, x=columnas['produccion'], y=columnas['rentabilidad'],
                 title='Relación entre producción y rentabilidad',
                 opacity=0.6,
                 labels={columnas['produccion']: 'Producción (toneladas)',
                         columnas['rentabilidad']: 'Rentabilidad (%)'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Datos insuficientes para este gráfico")
    
    # Fila 3: Boxplot y Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Rentabilidad por nivel de tecnificación")
        if columnas['tecnificacion'] and columnas['rentabilidad']:
            fig = px.box(df_filtrado, x=columnas['tecnificacion'], y=columnas['rentabilidad'],
                         title='Distribución de rentabilidad según tecnificación',
                         color=columnas['tecnificacion'],
                         points='outliers')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos insuficientes para este gráfico")
    
    with col2:
        st.subheader("🔥 Matriz de correlación")
        columnas_numericas = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()
        if len(columnas_numericas) > 1:
            corr_matrix = df_filtrado[columnas_numericas].corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect='auto',
                            color_continuous_scale='RdBu_r',
                            title='Correlación entre variables')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Se necesitan al menos 2 variables numéricas")
    
    # Fila 4: Riego y Superficie
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Rentabilidad según uso de riego")
        if columnas['riego'] and columnas['rentabilidad']:
            riego_stats = df_filtrado.groupby(columnas['riego'])[columnas['rentabilidad']].agg(['mean', 'median']).round(2)
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Media', x=riego_stats.index, y=riego_stats['mean'], marker_color='steelblue'))
            fig.add_trace(go.Bar(name='Mediana', x=riego_stats.index, y=riego_stats['median'], marker_color='lightblue'))
            fig.update_layout(title='Comparativa: Con riego vs Sin riego',
                              yaxis_title='Rentabilidad (%)',
                              barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos insuficientes para este gráfico")
    
    with col2:
        st.subheader("📏 Rentabilidad por rango de superficie")
        if columnas['superficie'] and columnas['rentabilidad']:
            df_temp = df_filtrado.copy()
            df_temp['Rango'] = pd.cut(df_temp[columnas['superficie']], 
                                       bins=[0, 100, 250, 500, float('inf')],
                                       labels=['<100 ha', '100-250 ha', '250-500 ha', '>500 ha'])
            rent_sup = df_temp.groupby('Rango', observed=False)[columnas['rentabilidad']].mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=rent_sup.index, y=rent_sup.values, mode='lines+markers',
                                     line=dict(width=3, color='green'), marker=dict(size=10)))
            fig.update_layout(title='Rentabilidad según superficie explotada',
                              yaxis_title='Rentabilidad (%)', xaxis_title='Rango de superficie')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Datos insuficientes para este gráfico")

st.markdown("---")

# ========== TABLAS DINÁMICAS ==========
st.header("📋 Tablas Dinámicas")

tab1, tab2, tab3 = st.tabs(["📊 Por Provincia", "🌱 Por Actividad", "⚙️ Por Tecnificación"])

with tab1:
    if columnas['provincia']:
        cols_agrupar = [columnas['provincia']]
        cols_valores = [col for col in [columnas['produccion'], columnas['rentabilidad'], 
                                         columnas['costo'], columnas['sustentabilidad'], 
                                         columnas['superficie'], columnas['empleados']] if col is not None]
        
        if cols_valores:
            pivot_prov = df_filtrado.groupby(cols_agrupar)[cols_valores].mean().round(2)
            st.dataframe(pivot_prov, use_container_width=True)

with tab2:
    if columnas['actividad']:
        cols_agrupar = [columnas['actividad']]
        cols_valores = [col for col in [columnas['produccion'], columnas['rentabilidad'], 
                                         columnas['costo'], columnas['sustentabilidad']] if col is not None]
        
        if cols_valores:
            pivot_act = df_filtrado.groupby(cols_agrupar)[cols_valores].mean().round(2)
            st.dataframe(pivot_act, use_container_width=True)

with tab3:
    if columnas['tecnificacion']:
        cols_agrupar = [columnas['tecnificacion']]
        cols_valores = [col for col in [columnas['produccion'], columnas['rentabilidad'], 
                                         columnas['costo'], columnas['sustentabilidad']] if col is not None]
        
        if cols_valores:
            pivot_tech = df_filtrado.groupby(cols_agrupar)[cols_valores].mean().round(2)
            st.dataframe(pivot_tech, use_container_width=True)

st.markdown("---")

# ========== RESUMEN EJECUTIVO ==========
st.header("📝 Resumen Ejecutivo y Recomendaciones")

with st.container():
    st.markdown("""
    ### Principales Hallazgos:
    
    1. **Rentabilidad vs Producción:** No existe correlación directa. Alta producción no garantiza alta rentabilidad.
    
    2. **Tecnificación:** Aumenta producción y sustentabilidad, pero NO garantiza mayor rentabilidad inmediata.
    
    3. **Actividades más rentables:** Maíz y Fruticultura muestran los mayores márgenes.
    
    4. **Uso de riego:** Mejora producción y sustentabilidad pero no necesariamente rentabilidad.
    
    ### Recomendaciones Estratégicas:
    
    - ✅ **Priorizar gestión de costos** antes que maximizar producción
    - ✅ **Evaluar inversión en tecnología** caso por caso
    - ✅ **Diversificar actividades** según condiciones regionales
    - ✅ **Monitorear sustentabilidad** como ventaja competitiva
    """)

st.markdown("---")
st.caption(f"📅 Dashboard actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Datos: {len(df_filtrado)} explotaciones")