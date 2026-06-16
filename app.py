import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Intentar importar plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configuración
st.set_page_config(
    page_title="TP Integrador - Grupo 3",
    page_icon="🌾",
    layout="wide"
)

# ========== FUNCIÓN PARA CARGAR DATASET ==========
@st.cache_data
def cargar_dataset():
    """Carga el dataset agropecuario desde la carpeta data/"""
    
    # Buscar en múltiples ubicaciones posibles
    posibles_ubicaciones = [
        Path("data/dataset_agropecuario.csv"),      # data/dataset_agropecuario.csv
        Path("data/agropecuario.csv"),               # nombre alternativo
        Path("dataset_agropecuario.csv"),            # raíz
        Path("../data/dataset_agropecuario.csv"),    # un nivel arriba
    ]
    
    for archivo in posibles_ubicaciones:
        if archivo.exists():
            df = pd.read_csv(archivo)
            return df, f"✅ Dataset cargado: {len(df)} registros desde `{archivo}`"
    
    # Si no encuentra el archivo, muestra las opciones probadas
    return None, f"❌ No se encontró 'dataset_agropecuario.csv' en la carpeta `data/`. Ubicaciones probadas: {[str(p) for p in posibles_ubicaciones]}"

# Cargar dataset
df, mensaje_carga = cargar_dataset()

# Título principal
st.title("🌾 Análisis del Sector Agropecuario Argentino")
st.markdown("### Producción, Costos y Rentabilidad")
st.markdown("**Grupo 3:** Rodolfo Nicolás Aguirre, María Florencia Ardanaz, Juan Manuel Bidegain, Lourdes Reynaldo")
st.markdown("---")

# Mostrar estado de carga
if df is not None:
    st.success(mensaje_carga)
    
    # Mostrar estructura de carpetas actual
    with st.expander("📁 Estructura del proyecto", expanded=False):
        st.code("""
        tp_integrador_g3/
        │
        ├── app.py
        ├── requirements.txt
        │
        ├── data/                           ← ¡TU ARCHIVO ESTÁ AQUÍ!
        │   └── dataset_agropecuario.csv    ← Cargado correctamente
        │
        └── pages/
            ├── 1_Limpieza.py
            ├── 2_AED.py
            ├── 3_Dashboard.py
            └── 4_Analisis.py
        """)
    
    # Vista previa del dataset
    with st.expander("📋 Vista previa del dataset", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
        
        # Mostrar tipos de datos
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Tipos de datos:**")
            st.dataframe(df.dtypes.to_frame().rename(columns={0: 'Tipo'}), use_container_width=True)
        with col2:
            st.write("**Estadísticas rápidas (columnas numéricas):**")
            # Mostrar solo columnas numéricas
            df_numeric = df.select_dtypes(include=[np.number])
            if len(df_numeric.columns) > 0:
                st.dataframe(df_numeric.describe(), use_container_width=True)
            else:
                st.info("No hay columnas numéricas en el dataset")
    
    # Guardar en session_state
    st.session_state['df'] = df
    st.session_state['PLOTLY_AVAILABLE'] = PLOTLY_AVAILABLE
    
else:
    st.error(mensaje_carga)
    
    # Mostrar ayuda más detallada
    st.info("""
    ### 📁 ¿Cómo solucionarlo?
    
    1. **Verificá la estructura de carpetas:**