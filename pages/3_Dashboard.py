import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")
st.title("📊 Dashboard Ejecutivo - Sector Agropecuario")
st.markdown("### Monitoreo de KPIs y análisis interactivo")

# Cargar datos
if 'df_clean' in st.session_state:
    df = st.session_state['df_clean']
else:
    # Datos simulados
    np.random.seed(42)
    df = pd.DataFrame({
        'Provincia': np.random.choice(['Buenos Aires', 'Córdoba', 'Santa Fe', 'Entre Ríos', 'Salta', 'Mendoza', 'La Pampa', 'Chaco'], 5000),
        'Actividad': np.random.choice(['Soja', 'Maíz', 'Trigo', 'Ganadería', 'Lechería', 'Fruticultura'], 5000),
        'Nivel_Tecnificacion': np.random.choice(['Bajo', 'Medio', 'Alto'], 5000, p=[0.3, 0.4, 0.3]),
        'Uso_Riego': np.random.choice(['Sí', 'No'], 5000),
        'Superficie_Hectareas': np.random.exponential(300, 5000).astype(int),
        'Produccion_Toneladas': np.random.normal(310, 150, 5000),
        'Costo_Produccion': np.random.normal(84120, 60000, 5000),
        'Rentabilidad_Porcentaje': np.random.normal(116, 100, 5000),
        'Indice_Sustentabilidad': np.random.uniform(40, 90, 5000),
        'Cantidad_Empleados': np.random.poisson(6, 5000)
    })
    df = df[df['Superficie_Hectareas'] > 0]
    df = df[df['Rentabilidad_Porcentaje'].between(-90, 500)]

# ========== SEGMENTADORES (filtros) ==========
st.sidebar.header("🔍 Segmentadores")
st.sidebar.markdown("---")

provincia_sel = st.sidebar.multiselect(
    "🌍 Provincia",
    options=sorted(df['Provincia'].unique()),
    default=sorted(df['Provincia'].unique())[:4]
)

actividad_sel = st.sidebar.multiselect(
    "🌱 Actividad productiva",
    options=sorted(df['Actividad'].unique()),
    default=sorted(df['Actividad'].unique())[:4]
)

tecnificacion_sel = st.sidebar.multiselect(
    "⚙️ Nivel de tecnificación",
    options=sorted(df['Nivel_Tecnificacion'].unique()),
    default=sorted(df['Nivel_Tecnificacion'].unique())
)

riego_sel = st.sidebar.multiselect(
    "💧 Uso de riego",
    options=sorted(df['Uso_Riego'].unique()),
    default=sorted(df['Uso_Riego'].unique())
)

# Aplicar filtros
df_filtered = df[
    (df['Provincia'].isin(provincia_sel)) &
    (df['Actividad'].isin(actividad_sel)) &
    (df['Nivel_Tecnificacion'].isin(tecnificacion_sel)) &
    (df['Uso_Riego'].isin(riego_sel))
]

# ========== KPIs ==========
st.header("📈 Indicadores Clave (KPIs)")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    prod_promedio = df_filtered['Produccion_Toneladas'].mean()
    st.metric(
        label="🌾 Producción promedio",
        value=f"{prod_promedio:,.0f} ton",
        delta=f"vs nacional: {(prod_promedio - df['Produccion_Toneladas'].mean()):+.0f}",
        delta_color="normal"
    )

with kpi_col2:
    rent_promedio = df_filtered['Rentabilidad_Porcentaje'].mean()
    st.metric(
        label="💰 Rentabilidad promedio",
        value=f"{rent_promedio:+.1f}%",
        delta=f"vs nacional: {(rent_promedio - df['Rentabilidad_Porcentaje'].mean()):+.1f}%",
        delta_color="normal" if rent_promedio > 0 else "inverse"
    )

with kpi_col3:
    costo_promedio = df_filtered['Costo_Produccion'].mean()
    st.metric(
        label="💸 Costo de producción",
        value=f"${costo_promedio:,.0f}",
        delta=f"vs nacional: ${(costo_promedio - df['Costo_Produccion'].mean()):+,.0f}",
        delta_color="inverse"  # costo menor es mejor
    )

with kpi_col4:
    sust_promedio = df_filtered['Indice_Sustentabilidad'].mean()
    st.metric(
        label="🌱 Sustentabilidad",
        value=f"{sust_promedio:.1f}/100",
        delta=f"vs nacional: {(sust_promedio - df['Indice_Sustentabilidad'].mean()):+.1f}",
        delta_color="normal"
    )

with kpi_col5:
    empleados_promedio = df_filtered['Cantidad_Empleados'].mean()
    st.metric(
        label="👥 Empleados por explotación",
        value=f"{empleados_promedio:.1f}",
        delta=f"vs nacional: {(empleados_promedio - df['Cantidad_Empleados'].mean()):+.1f}"
    )

st.markdown("---")

# ========== VISUALIZACIONES ==========
st.header("📊 Visualizaciones Interactivas")

# Fila 1: Dos gráficos
col1, col2 = st.columns(2)

with col1:
    # Gráfico de barras: Rentabilidad por actividad
    rent_act = df_filtered.groupby('Actividad')['Rentabilidad_Porcentaje'].mean().sort_values(ascending=True)
    fig = px.bar(x=rent_act.values, y=rent_act.index, orientation='h',
                 title='Rentabilidad promedio por actividad',
                 color=rent_act.values, color_continuous_scale='Viridis',
                 labels={'x': 'Rentabilidad (%)', 'y': ''})
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Gráfico de dispersión: Superficie vs Producción
    fig = px.scatter(df_filtered.sample(min(1000, len(df_filtered))), 
                     x='Superficie_Hectareas', y='Produccion_Toneladas',
                     color='Nivel_Tecnificacion', size='Rentabilidad_Porcentaje',
                     hover_data=['Provincia', 'Actividad'],
                     title='Superficie vs Producción (tamaño = rentabilidad)',
                     labels={'Superficie_Hectareas': 'Superficie (hectáreas)',
                             'Produccion_Toneladas': 'Producción (toneladas)'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Fila 2: Dos gráficos
col3, col4 = st.columns(2)

with col3:
    # Gráfico de líneas: Rentabilidad por rango de superficie
    df_filtered['Rango_Superficie'] = pd.cut(df_filtered['Superficie_Hectareas'],
                                              bins=[0, 100, 250, 500, float('inf')],
                                              labels=['<100 ha', '100-250 ha', '250-500 ha', '>500 ha'])
    rent_sup = df_filtered.groupby('Rango_Superficie', observed=False)['Rentabilidad_Porcentaje'].mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rent_sup.index, y=rent_sup.values, mode='lines+markers',
                             line=dict(width=3, color='green'), marker=dict(size=10)))
    fig.update_layout(title='Rentabilidad según superficie explotada',
                      yaxis_title='Rentabilidad (%)', xaxis_title='Rango de superficie')
    st.plotly_chart(fig, use_container_width=True)

with col4:
    # Gráfico de barras apiladas: Composición por provincia
    prov_tech = pd.crosstab(df_filtered['Provincia'], df_filtered['Nivel_Tecnificacion'])
    fig = px.bar(prov_tech, x=prov_tech.index, y=['Bajo', 'Medio', 'Alto'],
                 title='Distribución de niveles de tecnificación por provincia',
                 labels={'value': 'Cantidad de explotaciones', 'variable': 'Nivel', 'Provincia': ''},
                 color_discrete_map={'Bajo': '#ff9999', 'Medio': '#66b3ff', 'Alto': '#99ff99'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ========== TABLA DINÁMICA ==========
st.header("📋 Tabla Dinámica - Detalle por segmento")

# Selector de agregación
aggr_col = st.selectbox("Seleccionar dimensión para agrupar", 
                        ['Provincia', 'Actividad', 'Nivel_Tecnificacion', 'Uso_Riego'])

pivot_table = df_filtered.groupby(aggr_col).agg({
    'Produccion_Toneladas': 'mean',
    'Rentabilidad_Porcentaje': '