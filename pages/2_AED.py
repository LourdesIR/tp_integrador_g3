import streamlit as st
import pandas as pd
import numpy as np

# Plotly es opcional
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Análisis Exploratorio", layout="wide")

# Verificar datos
if 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos limpios cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

# Y cambiar:
df = st.session_state['df_limpio']  

st.title("📈 Actividades 5-8: Estadística Descriptiva y Visualizaciones")
st.markdown("---")

# ========== ACTIVIDAD 5: ESTADÍSTICA DESCRIPTIVA ==========
st.header("📊 Actividad 5: Estadística Descriptiva")

with st.expander("Ver estadísticas completas", expanded=True):
    # Seleccionar solo columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if columnas_numericas:
        # Calcular estadísticas
        stats = df[columnas_numericas].describe().T
        stats['mediana'] = df[columnas_numericas].median()
        stats['rango'] = stats['max'] - stats['min']
        
        st.dataframe(stats[['mean', 'mediana', 'std', 'min', 'max', 'rango']].round(2), 
                     use_container_width=True)
        
        # Mostrar interpretación
        st.markdown("""
        ### 📝 Interpretación de las medidas:
        
        - **Media vs Mediana:** Si la media es mayor que la mediana, hay valores atípicos altos
        - **Desviación estándar:** Valores altos indican gran variabilidad entre explotaciones
        - **Rango:** Muestra la diferencia entre la explotación más grande y más pequeña
        """)
    else:
        st.warning("No se encontraron columnas numéricas en el dataset")

# ========== ACTIVIDAD 6: PERFILES PRODUCTIVOS ==========
st.header("👥 Actividad 6: Perfiles Productivos")

# Detectar columnas disponibles
columnas_disponibles = {
    'provincia': 'Provincia' if 'Provincia' in df.columns else None,
    'actividad': 'Actividad' if 'Actividad' in df.columns else None,
    'tecnificacion': 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None,
    'riego': 'Uso_Riego' if 'Uso_Riego' in df.columns else None,
    'produccion': 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None,
    'rentabilidad': 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None,
    'sustentabilidad': 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None
}

col1, col2 = st.columns(2)

with col1:
    if columnas_disponibles['provincia'] and columnas_disponibles['produccion']:
        prod_prov = df.groupby(columnas_disponibles['provincia'])[columnas_disponibles['produccion']].mean().sort_values(ascending=False)
        st.markdown("#### 🌾 Producción promedio por provincia")
        st.dataframe(prod_prov.to_frame().round(1), use_container_width=True)
        
        if PLOTLY_AVAILABLE:
            fig = px.bar(x=prod_prov.index, y=prod_prov.values,
                         title='Producción promedio por provincia',
                         color=prod_prov.values, color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(prod_prov)

with col2:
    if columnas_disponibles['actividad'] and columnas_disponibles['rentabilidad']:
        rent_act = df.groupby(columnas_disponibles['actividad'])[columnas_disponibles['rentabilidad']].mean().sort_values(ascending=False)
        st.markdown("#### 💰 Rentabilidad promedio por actividad")
        st.dataframe(rent_act.to_frame().round(1), use_container_width=True)
        
        if PLOTLY_AVAILABLE:
            fig = px.bar(x=rent_act.index, y=rent_act.values,
                         title='Rentabilidad promedio por actividad',
                         color=rent_act.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(rent_act)

# Perfil por tecnificación
if columnas_disponibles['tecnificacion']:
    st.markdown("---")
    st.subheader("⚙️ Impacto del nivel de tecnificación")
    
    tech_group = df.groupby(columnas_disponibles['tecnificacion']).agg({
        col: 'mean' for col in [columnas_disponibles['produccion'], 
                                  columnas_disponibles['rentabilidad'],
                                  columnas_disponibles['sustentabilidad']] 
        if col is not None
    }).round(2)
    
    st.dataframe(tech_group, use_container_width=True)
    
    st.markdown("""
    **Conclusiones:**
    - Mayor tecnificación → Mayor producción
    - Mayor tecnificación → Mayor sustentabilidad
    - Pero **NO** garantiza mayor rentabilidad
    """)

# ========== ACTIVIDAD 7: VISUALIZACIONES ==========
st.header("🎨 Actividad 7: Visualizaciones")

if PLOTLY_AVAILABLE:
    # Gráfico de dispersión
    if columnas_disponibles['produccion'] and columnas_disponibles['rentabilidad']:
        st.subheader("📈 Producción vs Rentabilidad")
        fig = px.scatter(df.sample(min(500, len(df))), 
                        x=columnas_disponibles['produccion'], 
                        y=columnas_disponibles['rentabilidad'],
                        title='Relación entre producción y rentabilidad',
                        opacity=0.6,
                        labels={columnas_disponibles['produccion']: 'Producción (toneladas)',
                                columnas_disponibles['rentabilidad']: 'Rentabilidad (%)'})
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📌 **Insight:** No hay correlación directa - alta producción no garantiza alta rentabilidad")
    
    # Boxplot por tecnificación
    if columnas_disponibles['tecnificacion'] and columnas_disponibles['rentabilidad']:
        st.subheader("📊 Rentabilidad según nivel de tecnificación")
        fig = px.box(df, x=columnas_disponibles['tecnificacion'], 
                    y=columnas_disponibles['rentabilidad'],
                    title='Distribución de rentabilidad por nivel de tecnificación',
                    color=columnas_disponibles['tecnificacion'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap de correlación
    if len(columnas_numericas) > 1:
        st.subheader("🔥 Matriz de correlación")
        corr_matrix = df[columnas_numericas].corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect='auto',
                       color_continuous_scale='RdBu_r',
                       title='Correlación entre variables numéricas')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar top correlaciones con rentabilidad
        if columnas_disponibles['rentabilidad'] and columnas_disponibles['rentabilidad'] in corr_matrix.columns:
            st.subheader("🔍 Correlaciones con Rentabilidad")
            corr_rent = corr_matrix[columnas_disponibles['rentabilidad']].sort_values(ascending=False)
            st.dataframe(corr_rent.to_frame().round(3), use_container_width=True)
else:
    st.info("📊 Para visualizaciones interactivas, instalá plotly: `pip install plotly`")
    # Fallback con matplotlib básico
    if columnas_disponibles['produccion'] and columnas_disponibles['rentabilidad']:
        st.subheader("Gráfico de dispersión (versión simple)")
        chart_data = df[[columnas_disponibles['produccion'], columnas_disponibles['rentabilidad']]].dropna().head(500)
        st.scatter_chart(chart_data)

# ========== ACTIVIDAD 8: INTERPRETACIÓN ==========
st.header("💡 Actividad 8: Interpretación de visualizaciones")

with st.expander("Ver interpretaciones detalladas", expanded=True):
    st.markdown("""
    ### 📊 Rentabilidad promedio por actividad productiva
    
    **¿Qué representa?** Muestra qué tipo de producción (soja, maíz, trigo, ganadería, etc.) genera mayor retorno económico.
    
    **¿Qué información aporta?** Permite identificar qué actividades son más rentables en términos porcentuales.
    
    **Decisiones que respalda:** 
    - Orientar la producción hacia cultivos más rentables
    - Evaluar si conviene diversificar o especializarse
    
    ---
    
    ### 📈 Producción promedio por provincia
    
    **¿Qué representa?** Volumen de producción (toneladas) promedio por explotación en cada provincia.
    
    **¿Qué información aporta?** Identifica las regiones con mayor productividad física.
    
    **Decisiones que respalda:**
    - Dónde invertir en nuevas explotaciones
    - Dónde concentrar recursos logísticos
    
    ---
    
    ### 🔥 Matriz de correlación
    
    **¿Qué representa?** Relaciones lineales entre todas las variables numéricas.
    
    **¿Qué información aporta?** Muestra qué variables están asociadas. Valores cercanos a 1 o -1 indican fuerte relación.
    
    **Decisiones que respalda:**
    - Identificar factores que más influyen en rentabilidad
    - Evitar invertir en variables con baja correlación
    
    ---
    
    ### ⚠️ Conclusión clave
    
    La **tecnificación** aumenta producción y sustentabilidad, pero **NO garantiza mayor rentabilidad**.
    La rentabilidad depende del equilibrio entre ingresos, costos y precios de mercado.
    """)

st.markdown("---")
st.caption("📌 Los análisis completos están disponibles en el Dashboard Ejecutivo")