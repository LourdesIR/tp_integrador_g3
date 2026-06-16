import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="TP Integrador - Grupo 3",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🌾 Análisis del Sector Agropecuario Argentino")
st.markdown("### Producción, Costos y Rentabilidad")
st.markdown("**Grupo 3:** Rodolfo Nicolás Aguirre, María Florencia Ardanaz, Juan Manuel Bidegain, Lourdes Reynaldo")
st.markdown("---")

# Sidebar para navegación conceptual
st.sidebar.image("https://img.icons8.com/color/96/argentina.png", width=80)
st.sidebar.title("📋 Navegación")
st.sidebar.info("Usa el menú superior para explorar las diferentes actividades")

# Actividad 1: Comprensión de la problemática
with st.expander("📖 Actividad 1 - Importancia del sector agropecuario", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 El sector agropecuario en Argentina
        
        - **Aporte al PBI:** ~15% de los ingresos por exportaciones
        - **Generación de empleo:** Más de 500,000 puestos directos
        - **Principales cultivos:** Soja, maíz, trigo, girasol
        - **Ventaja comparativa:** Suelos fértiles y clima favorable
        """)
    
    with col2:
        st.metric("🌱 Producción anual de granos", "~140 M toneladas", "promedio 2020-2024")
        st.metric("💰 Exportaciones agroindustriales", "USD 35,000 M", "2024")

# Actividad 2: Dataset
with st.expander("📊 Actividad 2 - Comprensión del dataset"):
    st.markdown("""
    ### Características del dataset
    
    | Característica | Valor |
    |---|---|
    | Registros | 5,000 explotaciones |
    | Variables | 14 |
    | Período | Datos anuales |
    | Cobertura geográfica | Nacional |
    """)
    
    # Tabla de variables
    variables_df = pd.DataFrame({
        "Variable": ["ID_Explotacion", "Provincia", "Actividad", "Superficie_Hectareas", 
                     "Edad_Productor", "Nivel_Tecnificacion", "Produccion_Toneladas",
                     "Costo_Produccion", "Precio_Venta_Tonelada", "Ingresos",
                     "Cantidad_Empleados", "Uso_Riego", "Rentabilidad_Porcentaje",
                     "Indice_Sustentabilidad"],
        "Tipo": ["Identificador", "Categórica", "Categórica", "Numérica continua",
                 "Numérica discreta", "Categórica ordinal", "Numérica continua",
                 "Numérica continua", "Numérica continua", "Numérica continua",
                 "Numérica discreta", "Categórica binaria", "Numérica continua",
                 "Numérica continua"],
        "Descripción": ["ID único", "Provincia", "Tipo de producción", "Hectáreas",
                        "Edad del productor", "Bajo/Medio/Alto", "Toneladas producidas",
                        "Costos totales ($)", "Precio por tonelada ($)", "Ingresos totales ($)",
                        "N° de empleados", "Sí/No", "% de rentabilidad", "Índice 0-100"]
    })
    st.dataframe(variables_df, use_container_width=True)