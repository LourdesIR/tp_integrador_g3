import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Análisis Exploratorio", layout="wide")
st.title("📈 Actividades 5-8: Estadística Descriptiva y Visualizaciones")

# Cargar datos limpios (desde session_state o archivo)
if 'df_clean' in st.session_state:
    df = st.session_state['df_clean']
else:
    # Cargar datos simulados limpios
    np.random.seed(42)
    df = pd.DataFrame({
        'Provincia': np.random.choice(['Buenos Aires', 'Córdoba', 'Santa Fe', 'Entre Ríos', 'Salta'], 4000),
        'Actividad': np.random.choice(['Soja', 'Maíz', 'Trigo', 'Ganadería', 'Lechería', 'Fruticultura'], 4000),
        'Nivel_Tecnificacion': np.random.choice(['Bajo', 'Medio', 'Alto'], 4000, p=[0.3, 0.4, 0.3]),
        'Uso_Riego': np.random.choice(['Sí', 'No'], 4000),
        'Superficie_Hectareas': np.random.exponential(300, 4000).astype(int),
        'Produccion_Toneladas': np.random.normal(310, 150, 4000),
        'Costo_Produccion': np.random.normal(84120, 60000, 4000),
        'Rentabilidad_Porcentaje': np.random.normal(116, 100, 4000),
        'Indice_Sustentabilidad': np.random.uniform(40, 90, 4000),
        'Cantidad_Empleados': np.random.poisson(6, 4000)
    })
    df = df[df['Superficie_Hectareas'] > 0]
    df = df[df['Rentabilidad_Porcentaje'].between(-90, 500)]

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")
provincias_sel = st.sidebar.multiselect("Provincia", df['Provincia'].unique(), default=df['Provincia'].unique()[:3])
actividad_sel = st.sidebar.multiselect("Actividad", df['Actividad'].unique(), default=df['Actividad'].unique()[:3])

df_filtered = df[df['Provincia'].isin(provincias_sel) & df['Actividad'].isin(actividad_sel)]

# ========== ACTIVIDAD 5: ESTADÍSTICA DESCRIPTIVA ==========
st.header("📊 Actividad 5: Estadística Descriptiva")

with st.expander("Ver medidas estadísticas", expanded=True):
    vars_numericas = ['Superficie_Hectareas', 'Produccion_Toneladas', 'Costo_Produccion', 
                      'Rentabilidad_Porcentaje', 'Indice_Sustentabilidad', 'Cantidad_Empleados']
    
    stats = df[vars_numericas].describe().T
    stats['mediana'] = df[vars_numericas].median()
    stats['moda'] = df[vars_numericas].mode().iloc[0]
    
    st.dataframe(stats[['mean', 'mediana', 'moda', 'std', 'min', 'max']].round(2), 
                 use_container_width=True)

# ========== ACTIVIDAD 6: PERFILES PRODUCTIVOS ==========
st.header("👥 Actividad 6: Perfiles Productivos")

tab1, tab2, tab3, tab4 = st.tabs(["Por Provincia", "Por Actividad", "Por Tecnificación", "Por Superficie"])

with tab1:
    col1, col2 = st.columns(2)
    
    prod_prov = df.groupby('Provincia')['Produccion_Toneladas'].mean().sort_values(ascending=False)
    rent_prov = df.groupby('Provincia')['Rentabilidad_Porcentaje'].mean().sort_values(ascending=False)
    
    with col1:
        fig = px.bar(x=prod_prov.values, y=prod_prov.index, orientation='h',
                     title='Producción promedio por provincia', color=prod_prov.values,
                     color_continuous_scale='Greens')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(x=rent_prov.values, y=rent_prov.index, orientation='h',
                     title='Rentabilidad promedio por provincia', color=rent_prov.values,
                     color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 **Insight:** Santa Fe lidera en rentabilidad, mientras que Salta tiene mayor producción")

with tab2:
    # Gráfico de barras: Rentabilidad promedio por actividad (pedido en Actividad 7)
    rent_act = df.groupby('Actividad')['Rentabilidad_Porcentaje'].mean().sort_values(ascending=False)
    fig = px.bar(x=rent_act.index, y=rent_act.values, title='Rentabilidad promedio por actividad productiva',
                 color=rent_act.values, color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="Actividad", yaxis_title="Rentabilidad (%)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 **Gráfico solicitado en Actividad 7** - Permite identificar qué cultivos son más rentables")

with tab3:
    tech_stats = df.groupby('Nivel_Tecnificacion').agg({
        'Produccion_Toneladas': 'mean',
        'Rentabilidad_Porcentaje': 'mean',
        'Indice_Sustentabilidad': 'mean'
    }).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Producción (ton)', x=tech_stats.index, y=tech_stats['Produccion_Toneladas'], 
                         yaxis='y', marker_color='green'))
    fig.add_trace(go.Bar(name='Rentabilidad (%)', x=tech_stats.index, y=tech_stats['Rentabilidad_Porcentaje'], 
                         yaxis='y2', marker_color='blue'))
    fig.add_trace(go.Scatter(name='Sustentabilidad', x=tech_stats.index, y=tech_stats['Indice_Sustentabilidad'],
                             yaxis='y2', mode='lines+markers', line=dict(color='red', width=3)))
    
    fig.update_layout(title='Impacto del nivel de tecnificación',
                      yaxis=dict(title='Producción (toneladas)', side='left'),
                      yaxis2=dict(title='Porcentaje (%)', side='right', overlaying='y'),
                      legend=dict(x=0.01, y=0.99))
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("🔍 **Observación:** Mayor tecnificación aumenta producción y sustentabilidad, pero NO garantiza mayor rentabilidad")

with tab4:
    # Clasificación por superficie
    df['Rango_Superficie'] = pd.cut(df['Superficie_Hectareas'], 
                                     bins=[0, 100, 250, 500, float('inf')],
                                     labels=['Hasta 100 ha', '101-250 ha', '251-500 ha', 'Más de 500 ha'])
    
    sup_stats = df.groupby('Rango_Superficie', observed=False)[['Produccion_Toneladas', 'Rentabilidad_Porcentaje']].mean()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=sup_stats.index, y=sup_stats['Produccion_Toneladas'], name='Producción', marker_color='green'), secondary_y=False)
    fig.add_trace(go.Scatter(x=sup_stats.index, y=sup_stats['Rentabilidad_Porcentaje'], name='Rentabilidad', 
                             mode='lines+markers', line=dict(color='blue', width=3)), secondary_y=True)
    fig.update_layout(title='Producción y rentabilidad según superficie')
    fig.update_yaxes(title_text="Producción (toneladas)", secondary_y=False)
    fig.update_yaxes(title_text="Rentabilidad (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

# ========== ACTIVIDAD 7: GRÁFICOS ADICIONALES ==========
st.header("🎨 Actividad 7: Visualizaciones")

# Diagramas de dispersión
col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(df, x='Produccion_Toneladas', y='Rentabilidad_Porcentaje', 
                     color='Nivel_Tecnificacion', opacity=0.6,
                     title='Producción vs Rentabilidad',
                     labels={'Produccion_Toneladas': 'Producción (toneladas)', 
                             'Rentabilidad_Porcentaje': 'Rentabilidad (%)'})
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 No hay correlación directa: alta producción no implica alta rentabilidad")

with col2:
    fig = px.scatter(df, x='Nivel_Tecnificacion', y='Rentabilidad_Porcentaje', 
                     color='Uso_Riego', box=True,
                     title='Tecnificación vs Rentabilidad (con boxplot)',
                     labels={'Nivel_Tecnificacion': 'Nivel de tecnificación', 
                             'Rentabilidad_Porcentaje': 'Rentabilidad (%)'})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 Los niveles bajos muestran mayor dispersión y rentabilidades extremas")

# Heatmap de correlación
st.subheader("🔥 Heatmap de correlación entre variables")

corr_matrix = df[['Produccion_Toneladas', 'Costo_Produccion', 'Rentabilidad_Porcentaje', 
                  'Superficie_Hectareas', 'Indice_Sustentabilidad', 'Cantidad_Empleados']].corr()

fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r',
                title='Matriz de correlación')
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Gráfico de líneas: Distribución de costos
st.subheader("📈 Distribución de costos de producción")
fig = px.line(x=df['Costo_Produccion'].sort_values().values, 
              y=np.arange(1, len(df)+1)/len(df)*100,
              title='Curva de distribución de costos de producción',
              labels={'x': 'Costo de producción ($)', 'y': 'Percentil (%)'})
fig.add_vline(x=df['Costo_Produccion'].median(), line_dash="dash", line_color="red",
              annotation_text=f"Mediana: ${df['Costo_Produccion'].median():,.0f}")
st.plotly_chart(fig, use_container_width=True)

# Comparativa uso de riego
st.subheader("💧 Rentabilidad según uso de riego")
riego_stats = df.groupby('Uso_Riego')['Rentabilidad_Porcentaje'].agg(['mean', 'median', 'std'])
fig = go.Figure()
fig.add_trace(go.Bar(name='Media', x=riego_stats.index, y=riego_stats['mean'], marker_color='steelblue'))
fig.add_trace(go.Bar(name='Mediana', x=riego_stats.index, y=riego_stats['median'], marker_color='lightblue'))
fig.update_layout(title='Comparativa de rentabilidad: Con riego vs Sin riego',
                  yaxis_title='Rentabilidad (%)')
st.plotly_chart(fig, use_container_width=True)
st.warning("⚠️ **Hallazgo clave:** Las explotaciones SIN riego muestran mayor rentabilidad promedio")