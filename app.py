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
    
    # Buscar en data/dataset_agropecuario.csv
    archivo = Path("data/dataset_agropecuario.csv")
    
    if archivo.exists():
        df = pd.read_csv(archivo)
        return df, f"✅ Dataset cargado: {len(df)} registros desde `{archivo}`"
    
    return None, "❌ No se encontró 'dataset_agropecuario.csv' en la carpeta `data/`"

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
    
    # Estructura del proyecto
    with st.expander("📁 Estructura del proyecto", expanded=False):
        st.code("""
        tp_integrador_g3/
        │
        ├── app.py
        ├── requirements.txt
        │
        ├── data/
        │   └── dataset_agropecuario.csv
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Tipos de datos:**")
            st.dataframe(df.dtypes.to_frame().rename(columns={0: 'Tipo'}), use_container_width=True)
        with col2:
            st.write("**Estadísticas rápidas:**")
            df_numeric = df.select_dtypes(include=[np.number])
            if len(df_numeric.columns) > 0:
                st.dataframe(df_numeric.describe(), use_container_width=True)
    
    # Guardar en session_state
    st.session_state['df'] = df
    st.session_state['PLOTLY_AVAILABLE'] = PLOTLY_AVAILABLE
    
else:
    st.error(mensaje_carga)
    st.info("""
    **Solución:**
    1. Creá la carpeta `data/` en el mismo directorio que `app.py`
    2. Colocá el archivo `dataset_agropecuario.csv` dentro de `data/`
    3. Verificá que el nombre sea exactamente `dataset_agropecuario.csv`
    """)
    st.stop()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/argentina.png", width=80)
st.sidebar.title("📋 Navegación")
st.sidebar.info(f"📊 Dataset: {len(df):,} registros")

# Métricas en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Resumen rápido")

if 'Rentabilidad_Porcentaje' in df.columns:
    st.sidebar.metric("Rentabilidad promedio", f"{df['Rentabilidad_Porcentaje'].mean():.1f}%")
if 'Produccion_Toneladas' in df.columns:
    st.sidebar.metric("Producción promedio", f"{df['Produccion_Toneladas'].mean():.0f} ton")

# Actividad 1
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
        if 'Produccion_Toneladas' in df.columns:
            prod_total = df['Produccion_Toneladas'].sum() / 1_000_000
            st.metric("📊 Producción total en dataset", f"{prod_total:.1f} M toneladas")
        if 'Provincia' in df.columns:
            st.metric("🗺️ Provincias representadas", df['Provincia'].nunique())

# Actividad 2
with st.expander("📊 Actividad 2 - Comprensión del dataset", expanded=False):
    st.markdown("### Características del dataset")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registros", f"{len(df):,}")
    with col2:
        st.metric("Variables", len(df.columns))
    with col3:
        st.metric("Valores nulos", df.isnull().sum().sum())
    
    st.markdown("### Variables del dataset")
    var_info = pd.DataFrame({
        'Variable': df.columns,
        'Tipo': df.dtypes.values,
        'Valores nulos': df.isnull().sum().values,
        '% Nulos': (df.isnull().sum() / len(df) * 100).round(2).values
    })
    st.dataframe(var_info, use_container_width=True)

# Actividad 3 - Diagnóstico
with st.expander("🔍 Actividad 3 - Diagnóstico de calidad de datos", expanded=False):
    st.markdown("### Problemas detectados")
    
    problemas = []
    
    total_nulos = df.isnull().sum().sum()
    if total_nulos > 0:
        problemas.append(f"📌 **Valores faltantes:** {total_nulos} en total")
    
    for col in df.select_dtypes(include=[np.number]).columns:
        negativos = (df[col] < 0).sum()
        if negativos > 0:
            problemas.append(f"⚠️ **{col}:** {negativos} valores negativos")
    
    if 'Edad_Productor' in df.columns:
        edad_fuera = ((df['Edad_Productor'] < 18) | (df['Edad_Productor'] > 100)).sum()
        if edad_fuera > 0:
            problemas.append(f"👤 **Edad_Productor:** {edad_fuera} fuera de rango")
    
    if 'Rentabilidad_Porcentaje' in df.columns:
        rent_extrema = (df['Rentabilidad_Porcentaje'] > 500).sum()
        if rent_extrema > 0:
            problemas.append(f"💰 **Rentabilidad >500%:** {rent_extrema} valores atípicos")
    
    if problemas:
        for p in problemas:
            st.markdown(p)
    else:
        st.success("✅ No se detectaron problemas")

# Actividad 4 - Limpieza
with st.expander("🧹 Actividad 4 - Limpieza y preparación", expanded=False):
    st.markdown("### Plan de limpieza")
    
    st.markdown("""
    | Problema | Solución |
    |----------|----------|
    | Valores nulos en Produccion | Imputación: Ingresos / Precio_Venta |
    | Inconsistencias en categorías | Estandarización a formato uniforme |
    | Valores negativos | Eliminación o recálculo |
    | Rentabilidad extrema | Marcado como outlier |
    """)
    
    if st.button("🔄 Ejecutar limpieza", type="primary"):
        df_clean = df.copy()
        
        if 'Produccion_Toneladas' in df_clean and 'Ingresos' in df_clean and 'Precio_Venta_Tonelada' in df_clean:
            mask_nan = df_clean['Produccion_Toneladas'].isna()
            df_clean.loc[mask_nan, 'Produccion_Toneladas'] = (
                df_clean.loc[mask_nan, 'Ingresos'] / df_clean.loc[mask_nan, 'Precio_Venta_Tonelada']
            )
            st.success(f"✅ Corregidos {mask_nan.sum()} valores nulos")
        
        if 'Actividad' in df_clean:
            df_clean['Actividad'] = df_clean['Actividad'].str.capitalize()
            st.success("✅ Estandarizada columna Actividad")
        
        if 'Uso_Riego' in df_clean:
            df_clean['Uso_Riego'] = df_clean['Uso_Riego'].str.capitalize()
            st.success("✅ Estandarizada columna Uso_Riego")
        
        st.session_state['df_clean'] = df_clean
        
        csv = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Descargar dataset limpio", csv, "dataset_limpio.csv", "text/csv")

# Actividad 5-8: Visualizaciones (si está disponible plotly)
if PLOTLY_AVAILABLE and df is not None:
    with st.expander("📈 Actividades 5-8: Visualizaciones", expanded=False):
        st.markdown("### Gráficos del análisis exploratorio")
        
        # Gráfico 1: Rentabilidad por actividad
        if 'Rentabilidad_Porcentaje' in df.columns and 'Actividad' in df.columns:
            rent_act = df.groupby('Actividad')['Rentabilidad_Porcentaje'].mean().sort_values(ascending=False)
            fig1 = px.bar(x=rent_act.index, y=rent_act.values, 
                         title='Rentabilidad promedio por actividad',
                         color=rent_act.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Producción por provincia
        if 'Produccion_Toneladas' in df.columns and 'Provincia' in df.columns:
            prod_prov = df.groupby('Provincia')['Produccion_Toneladas'].mean().sort_values(ascending=False)
            fig2 = px.bar(x=prod_prov.index, y=prod_prov.values,
                         title='Producción promedio por provincia',
                         color=prod_prov.values, color_continuous_scale='Greens')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Dispersión
        if 'Produccion_Toneladas' in df.columns and 'Rentabilidad_Porcentaje' in df.columns:
            fig3 = px.scatter(df.sample(min(1000, len(df))), 
                             x='Produccion_Toneladas', y='Rentabilidad_Porcentaje',
                             title='Producción vs Rentabilidad', opacity=0.6)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Heatmap
        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(cols_num) > 1:
            corr_matrix = df[cols_num].corr()
            fig4 = px.imshow(corr_matrix, text_auto=True, aspect='auto',
                            color_continuous_scale='RdBu_r',
                            title='Matriz de correlación')
            fig4.update_layout(height=500)
            st.plotly_chart(fig4, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
### 📱 Navegación completa

Usá el **menú ☰ arriba a la izquierda** para acceder a:
- **1_Limpieza** → Actividades 3 y 4
- **2_AED** → Actividades 5-8  
- **3_Dashboard** → Actividad 9
- **4_Analisis** → Actividad 10
""")