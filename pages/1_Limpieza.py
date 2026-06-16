import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Limpieza de Datos", layout="wide")

# ========== FUNCIÓN PARA CONVERTIR COLUMNAS A NÚMEROS DE FORMA SEGURA ==========
def convertir_a_numerico(df, columna):
    """Intenta convertir una columna a numérico, maneja errores"""
    if columna in df.columns:
        try:
            # Limpiar caracteres especiales
            df[columna] = df[columna].astype(str).str.replace('%', '', regex=False)
            df[columna] = df[columna].astype(str).str.replace('$', '', regex=False)
            df[columna] = df[columna].astype(str).str.replace(',', '.', regex=False)
            df[columna] = df[columna].astype(str).str.strip()
            # Convertir a numérico
            return pd.to_numeric(df[columna], errors='coerce')
        except:
            return df[columna]
    return df[columna] if columna in df.columns else None

# ========== VERIFICAR QUE HAY DATOS ==========
if 'df_raw' not in st.session_state or 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

# Obtener ambos datasets desde session_state
df_raw = st.session_state['df_raw'].copy()        # Original (sucio)
df_limpio = st.session_state['df_limpio'].copy()  # Limpio

# Asegurar que las columnas numéricas sean numéricas en df_raw para el diagnóstico
columnas_a_convertir = ['Rentabilidad_Porcentaje', 'Produccion_Toneladas', 'Costo_Produccion', 
                        'Precio_Venta_Tonelada', 'Ingresos', 'Superficie_Hectareas', 
                        'Edad_Productor', 'Cantidad_Empleados', 'Indice_Sustentabilidad']

for col in columnas_a_convertir:
    if col in df_raw.columns:
        df_raw[col] = convertir_a_numerico(df_raw, col)
    if col in df_limpio.columns:
        df_limpio[col] = convertir_a_numerico(df_limpio, col)

st.title("🧹 Actividades 3 y 4: Diagnóstico y Limpieza de Datos")
st.markdown("---")

# Mostrar comparación inicial
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Registros originales", len(df_raw))
with col2:
    st.metric("Registros después limpieza", len(df_limpio))
with col3:
    st.metric("Registros eliminados", len(df_raw) - len(df_limpio))

st.markdown("---")

# ========== ACTIVIDAD 3: DIAGNÓSTICO ==========
st.header("🔍 Actividad 3 - Diagnóstico de calidad de datos")

with st.expander("📊 Valores faltantes", expanded=True):
    missing_df = pd.DataFrame({
        'Variable': df_raw.columns,
        'Valores faltantes': df_raw.isnull().sum(),
        'Porcentaje': (df_raw.isnull().sum() / len(df_raw) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Valores faltantes'] > 0]
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
        st.info(f"📌 Total de valores faltantes: {df_raw.isnull().sum().sum()}")
        
        if PLOTLY_AVAILABLE and len(missing_df) > 0:
            fig = px.bar(missing_df, x='Variable', y='Valores faltantes',
                         title='Valores faltantes por variable',
                         color='Valores faltantes', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No hay valores faltantes")

with st.expander("⚠️ Inconsistencias en variables categóricas", expanded=True):
    st.markdown("### Problemas detectados en datos originales")
    
    columnas_categoricas = df_raw.select_dtypes(include=['object']).columns
    
    if len(columnas_categoricas) > 0:
        for col in columnas_categoricas:
            if df_raw[col].nunique() < 20:
                valores = df_raw[col].value_counts()
                st.write(f"**{col}:** {len(valores)} categorías únicas")
                
                valores_lower = df_raw[col].astype(str).str.lower().value_counts()
                if len(valores) > len(valores_lower):
                    st.warning(f"⚠️ Posibles inconsistencias en '{col}' (mayúsculas/minúsculas)")
                    st.write("Valores encontrados:")
                    st.write(valores.head(10))
                st.write("---")
    else:
        st.info("No se encontraron columnas categóricas para analizar")

with st.expander("📈 Valores fuera de rango", expanded=True):
    problemas = []
    
    # Superficie negativa
    if 'Superficie_Hectareas' in df_raw.columns:
        sup_neg = (df_raw['Superficie_Hectareas'] < 0).sum()
        if sup_neg > 0:
            problemas.append(f"⚠️ **Superficie_Hectareas:** {sup_neg} valores negativos")
    
    # Costo negativo
    if 'Costo_Produccion' in df_raw.columns:
        costo_neg = (df_raw['Costo_Produccion'] < 0).sum()
        if costo_neg > 0:
            problemas.append(f"⚠️ **Costo_Produccion:** {costo_neg} valores negativos")
    
    # Empleados negativo
    if 'Cantidad_Empleados' in df_raw.columns:
        emp_neg = (df_raw['Cantidad_Empleados'] < 0).sum()
        if emp_neg > 0:
            problemas.append(f"⚠️ **Cantidad_Empleados:** {emp_neg} valores negativos")
    
    # Edad fuera de rango (si es numérica)
    if 'Edad_Productor' in df_raw.columns:
        if pd.api.types.is_numeric_dtype(df_raw['Edad_Productor']):
            edad_fuera = ((df_raw['Edad_Productor'] < 18) | (df_raw['Edad_Productor'] > 100)).sum()
            if edad_fuera > 0:
                problemas.append(f"👤 **Edad_Productor:** {edad_fuera} fuera de rango (18-100 años)")
    
    # Rentabilidad extrema (si es numérica)
    if 'Rentabilidad_Porcentaje' in df_raw.columns:
        if pd.api.types.is_numeric_dtype(df_raw['Rentabilidad_Porcentaje']):
            rent_extrema = (df_raw['Rentabilidad_Porcentaje'] > 500).sum()
            if rent_extrema > 0:
                problemas.append(f"💰 **Rentabilidad >500%:** {rent_extrema} valores atípicos extremos")
    
    # Sustentabilidad fuera de rango
    if 'Indice_Sustentabilidad' in df_raw.columns:
        if pd.api.types.is_numeric_dtype(df_raw['Indice_Sustentabilidad']):
            sust_fuera = ((df_raw['Indice_Sustentabilidad'] < 0) | (df_raw['Indice_Sustentabilidad'] > 100)).sum()
            if sust_fuera > 0:
                problemas.append(f"🌱 **Indice_Sustentabilidad:** {sust_fuera} fuera de rango (0-100)")
    
    if problemas:
        for p in problemas:
            st.markdown(p)
    else:
        st.success("✅ No se detectaron valores fuera de rango")
    
    # Mostrar estadísticas básicas de columnas numéricas
    st.markdown("### 📊 Estadísticas básicas de variables numéricas")
    cols_num = df_raw.select_dtypes(include=[np.number]).columns.tolist()
    if cols_num:
        st.dataframe(df_raw[cols_num].describe(), use_container_width=True)

# ========== ACTIVIDAD 4: LIMPIEZA ==========
st.header("🛠️ Actividad 4 - Limpieza y preparación de datos")
st.markdown("### Comparación: Antes vs Después")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dataset ORIGINAL (primeras filas)")
    st.dataframe(df_raw.head(10), use_container_width=True)
    st.caption(f"Total: {len(df_raw)} registros")

with col2:
    st.subheader("✅ Dataset LIMPIO (primeras filas)")
    st.dataframe(df_limpio.head(10), use_container_width=True)
    st.caption(f"Total: {len(df_limpio)} registros")

# Mostrar las transformaciones aplicadas
st.markdown("### 🔧 Transformaciones aplicadas")

transformaciones = [
    "1. **Conversión de tipos:** Columnas numéricas convertidas correctamente",
    "2. **Imputación de nulos:** Produccion_Toneladas = Ingresos / Precio_Venta_Tonelada",
    "3. **Estandarización:** Categorías unificadas (mayúsculas/minúsculas/tildes)",
    "4. **Corrección de ingresos:** Recalculados cuando no coincidían con Producción × Precio",
    "5. **Eliminación:** Registros con superficie negativa o edad fuera de rango",
    "6. **Outliers:** Marcados los casos con rentabilidad >500%"
]

for t in transformaciones:
    st.info(t)

# Mostrar estadísticas de limpieza
st.markdown("### 📊 Estadísticas de limpieza")

stats_comparacion = pd.DataFrame({
    'Métrica': ['Registros totales', 'Valores nulos', 'Variables numéricas'],
    'Original': [len(df_raw), df_raw.isnull().sum().sum(), len(df_raw.select_dtypes(include=[np.number]).columns)],
    'Limpio': [len(df_limpio), df_limpio.isnull().sum().sum(), len(df_limpio.select_dtypes(include=[np.number]).columns)]
})
st.dataframe(stats_comparacion, use_container_width=True)

# Opción para descargar dataset limpio
st.markdown("---")
csv = df_limpio.to_csv(index=False).encode('utf-8')
st.download_button(
    "💾 Descargar dataset LIMPIO (CSV)",
    csv,
    "dataset_agropecuario_limpio.csv",
    "text/csv",
    type="primary"
)

# Mostrar tipos de datos después de limpieza
with st.expander("🔧 Tipos de datos después de limpieza", expanded=False):
    tipos_df = pd.DataFrame({
        'Columna': df_limpio.columns,
        'Tipo': df_limpio.dtypes.values,
        'Valores nulos': df_limpio.isnull().sum().values
    })
    st.dataframe(tipos_df, use_container_width=True)

st.markdown("---")
st.caption("💡 **Nota:** El dataset limpio es el que se utiliza en las páginas de AED, Dashboard y Análisis Crítico")