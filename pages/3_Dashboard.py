import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# Verificar datos
if 'df' not in st.session_state:
    st.error("⚠️ No hay datos cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

df = st.session_state['df']

st.title("📊 Actividad 9: Dashboard Ejecutivo")
st.markdown("### Monitoreo de KPIs y análisis interactivo")
st.markdown("---")

# Detectar columnas disponibles
cols = {
    'provincia': 'Provincia' if 'Provincia' in df.columns else None,
    'actividad': 'Actividad' if 'Actividad' in df.columns else None,
    'tecnificacion': 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None,
    'riego': 'Uso_Riego' if 'Uso_Riego' in df.columns else None,
    'produccion': 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None,
    'rentabilidad': 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None,
    'costo': 'Costo_Produccion' if 'Costo_Produccion' in df.columns else None,
    'sustentabilidad': 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None,
    'empleados': 'Cantidad_Empleados' if 'Cantidad_Empleados' in df.columns else None,
    'superficie': 'Superficie_Hectareas' if 'Superficie_Hectareas' in df.columns else None
}

# ========== SEGMENTADORES (Filtros) ==========
st.sidebar.header("🔍 Filtros")

# Crear filtros solo si las columnas existen
filtros_aplicados = {}
df_filtrado = df.copy()

if cols['provincia']:
    prov_seleccionadas = st.sidebar.multiselect(
        "Provincia",
        options=sorted(df[cols['provincia']].dropna().unique()),
        default=[]
    )
    if prov_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[cols['provincia']].isin(prov_seleccionadas)]

if cols['actividad']:
    act_seleccionadas = st.sidebar.multiselect(
        "Actividad productiva",
        options=sorted(df[cols['actividad']].dropna().unique()),
        default=[]
    )
    if act_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado[cols['actividad']].isin(act_seleccionadas)]

if cols['tecnificacion']:
    tech_seleccionada = st.sidebar.selectbox(
        "Nivel de tecnificación",
        options=["Todas"] + sorted(df[cols['tecnificacion']].dropna().unique().tolist())
    )
    if tech_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado[cols['tecnificacion']] == tech_seleccionada]

# ========== KPIs ==========
st.header("📈 Indicadores Clave (KPIs)")

kpi_cols = st.columns(5)

kpi_config = [
    (cols['produccion'], "🌾 Producción promedio", "ton", 0),
    (cols['rentabilidad'], "💰 Rentabilidad promedio", "%", 1),
    (cols['costo'], "💸 Costo promedio", "$", 0),
    (cols['sustentabilidad'], "🌱 Sustentabilidad", "/100", 1),
    (cols['empleados'], "👥 Empleados", "", 1)
]

for i, (col, label, unidad, decimales) in enumerate(kpi_config):
    if col and not df_filtrado[col].isna().all():
        valor = df_filtrado[col].mean()
        if not pd.isna(valor):
            if decimales == 0:
                kpi_cols[i].metric(label, f"{valor:,.0f} {unidad}")
            else:
                kpi_cols[i].metric(label, f"{valor:.1f} {unidad}")

st.markdown("---")

# ========== VISUALIZACIONES ==========
st.header("📊 Análisis Visual")

col1, col2 = st.columns(2)

with col1:
    if cols['actividad'] and cols['rentabilidad']:
        st.subheader("Rentabilidad por actividad")
        rent_act = df_filtrado.groupby(cols['actividad'])[cols['rentabilidad']].mean().sort_values(ascending=True)
        
        if PLOTLY_AVAILABLE:
            fig = px.bar(x=rent_act.values, y=rent_act.index, orientation='h',
                        title='Rentabilidad promedio por actividad',
                        color=rent_act.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(rent_act)

with col2:
    if cols['provincia'] and cols['produccion']:
        st.subheader("Producción por provincia")
        prod_prov = df_filtrado.groupby(cols['provincia'])[cols['produccion']].mean().sort_values(ascending=False)
        
        if PLOTLY_AVAILABLE:
            fig = px.bar(x=prod_prov.index, y=prod_prov.values,
                        title='Producción promedio por provincia',
                        color=prod_prov.values, color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(prod_prov)

# Gráfico de dispersión
if cols['produccion'] and cols['rentabilidad']:
    st.subheader("Producción vs Rentabilidad")
    
    sample_df = df_filtrado[[cols['produccion'], cols['rentabilidad']]].dropna().head(1000)
    
    if PLOTLY_AVAILABLE:
        fig = px.scatter(sample_df, x=cols['produccion'], y=cols['rentabilidad'],
                        title='Relación entre producción y rentabilidad',
                        opacity=0.6, trendline='ols')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.scatter_chart(sample_df)

# ========== TABLA DINÁMICA ==========
st.header("📋 Tabla Dinámica")

agrupar_por = st.selectbox("Agrupar por:", 
                          [col for col in [cols['provincia'], cols['actividad'], cols['tecnificacion']] if col])

if agrupar_por:
    columnas_agregar = []
    for col in [cols['produccion'], cols['rentabilidad'], cols['costo'], cols['sustentabilidad']]:
        if col:
            columnas_agregar.append(col)
    
    if columnas_agregar:
        pivot = df_filtrado.groupby(agrupar_por)[columnas_agregar].mean().round(2)
        st.dataframe(pivot, use_container_width=True)

# ========== RESUMEN EJECUTIVO ==========
st.header("📝 Resumen Ejecutivo")

with st.container():
    st.markdown("""
    ### Principales hallazgos:
    
    1. **Rentabilidad vs Producción:** No están correlacionadas directamente
    2. **Tecnificación:** Aumenta producción pero no garantiza rentabilidad
    3. **Actividades más rentables:** Maíz y Fruticultura
    4. **Provincias destacadas:** Santa Fe (rentabilidad), Salta (producción)
    """)

st.markdown("---")
st.caption(f"Dashboard actualizado | Datos filtrados: {len(df_filtrado)} explotaciones")