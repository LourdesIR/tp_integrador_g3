import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Limpieza de Datos", layout="wide")
st.title("🧹 Actividades 3 y 4: Diagnóstico y Limpieza de Datos")

# Función para cargar datos (simulados - reemplazar con tu archivo real)
@st.cache_data
def cargar_datos_raw():
    """Carga el dataset original (simulado para demostración)"""
    np.random.seed(42)
    n = 5000
    
    # Generar datos simulados con problemas conocidos
    provincias = np.random.choice(['Buenos Aires', 'Córdoba', 'Santa Fe', 'Entre Ríos', 'Salta'], n)
    actividades = np.random.choice(['Soja', 'Maiz', 'Trigo', 'Ganaderia', 'Lecheria'], n)
    
    # Introducir errores tipográficos (5% de los datos)
    actividades_con_errores = actividades.copy()
    errores_idx = np.random.choice(n, int(n*0.05), replace=False)
    for idx in errores_idx:
        actividades_con_errores[idx] = actividades_con_errores[idx].lower()
    
    df = pd.DataFrame({
        'ID_Explotacion': range(1, n+1),
        'Provincia': provincias,
        'Actividad': actividades_con_errores,
        'Superficie_Hectareas': np.random.exponential(300, n).astype(int),
        'Produccion_Toneladas': np.random.normal(300, 100, n),
        'Costo_Produccion': np.random.normal(85000, 30000, n),
        'Precio_Venta_Tonelada': np.random.normal(520, 50, n),
        'Ingresos': np.random.normal(160000, 60000, n),
        'Rentabilidad_Porcentaje': np.random.normal(120, 40, n),
        'Uso_Riego': np.random.choice(['Si', 'No'], n),
        'Indice_Sustentabilidad': np.random.uniform(40, 90, n)
    })
    
    # Introducir valores nulos (219 en Produccion)
    null_idx = np.random.choice(n, 219, replace=False)
    df.loc[null_idx, 'Produccion_Toneladas'] = np.nan
    
    # Introducir valores fuera de rango
    df.loc[np.random.choice(n, 29), 'Superficie_Hectareas'] = -np.random.randint(1, 100, 29)
    df.loc[np.random.choice(n, 50), 'Edad_Productor'] = np.random.choice([12, 105, 110], 50)
    
    return df

# Cargar datos
df_raw = cargar_datos_raw()

# Mostrar diagnóstico inicial
st.header("📋 Diagnóstico de Calidad de Datos (Actividad 3)")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Registros totales", len(df_raw))
with col2:
    st.metric("Variables", len(df_raw.columns))
with col3:
    st.metric("Valores nulos", df_raw.isnull().sum().sum())

# Tabla de valores faltantes
st.subheader("🔍 Valores faltantes por variable")
missing_df = pd.DataFrame({
    'Variable': df_raw.columns,
    'Valores faltantes': df_raw.isnull().sum(),
    'Porcentaje': (df_raw.isnull().sum() / len(df_raw) * 100).round(2)
})
missing_df = missing_df[missing_df['Valores faltantes'] > 0]
st.dataframe(missing_df, use_container_width=True)

# Gráfico de valores nulos
fig_missing = px.bar(missing_df, x='Variable', y='Valores faltantes', 
                      title='Distribución de valores faltantes',
                      color='Valores faltantes', color_continuous_scale='Reds')
st.plotly_chart(fig_missing, use_container_width=True)

# Mostrar inconsistencias
st.subheader("⚠️ Inconsistencias detectadas")
with st.expander("Ver inconsistencias en variables categóricas"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Actividad - valores únicos:**")
        st.write(df_raw['Actividad'].value_counts().head(10))
    with col_b:
        st.write("**Uso_Riego - valores únicos:**")
        st.write(df_raw['Uso_Riego'].value_counts())

# --- PROCESO DE LIMPIEZA ---
st.header("🛠️ Proceso de Limpieza (Actividad 4)")
st.markdown("""
### Estrategias aplicadas:

1. **Valores faltantes en Produccion_Toneladas (219 registros)**
   - Imputación mediante fórmula: `Produccion = Ingresos / Precio_Venta_Tonelada`
   
2. **Estandarización de categorías**
   - Actividad: unificar 'Soja', 'soja', 'SOJA' → 'Soja'
   - Uso_Riego: unificar 'Si', 'SI', 'sí', 'Sí' → 'Sí'
   
3. **Corrección de valores fuera de rango**
   - Superficie negativa → eliminar registros
   - Edad < 18 o > 100 → marcar como outliers
   
4. **Consistencia financiera**
   - Recalcular Ingresos donde no coinciden con Producción × Precio
""")

# Botón para ejecutar limpieza
if st.button("🧹 Ejecutar limpieza de datos", type="primary"):
    df_clean = df_raw.copy()
    
    # 1. Corregir producción faltante
    mask_null = df_clean['Produccion_Toneladas'].isnull()
    df_clean.loc[mask_null, 'Produccion_Toneladas'] = (
        df_clean.loc[mask_null, 'Ingresos'] / df_clean.loc[mask_null, 'Precio_Venta_Tonelada']
    )
    
    # 2. Estandarizar categorías
    df_clean['Actividad'] = df_clean['Actividad'].str.capitalize()
    df_clean['Uso_Riego'] = df_clean['Uso_Riego'].str.capitalize()
    
    # 3. Eliminar superficies negativas
    df_clean = df_clean[df_clean['Superficie_Hectareas'] > 0]
    
    # 4. Recalcular rentabilidad para asegurar consistencia
    df_clean['Rentabilidad_Recalculada'] = (
        (df_clean['Ingresos'] - df_clean['Costo_Produccion']) / df_clean['Costo_Produccion'] * 100
    )
    
    st.success("✅ Limpieza completada!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registros después de limpieza", len(df_clean), 
                  delta=f"{len(df_clean)-len(df_raw)}", delta_color="off")
    with col2:
        st.metric("Valores nulos restantes", df_clean.isnull().sum().sum(),
                  delta=f"-{df_raw.isnull().sum().sum()}", delta_color="inverse")
    with col3:
        st.metric("Categorías estandarizadas", "2 variables", "Actividad, Uso_Riego")
    
    # Mostrar dataset limpio
    st.subheader("📊 Dataset después de limpieza")
    st.dataframe(df_clean.head(100), use_container_width=True)
    
    # Guardar para usar en otras páginas
    st.session_state['df_clean'] = df_clean
    
    # Botón para descargar
    csv = df_clean.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Descargar dataset limpio", csv, "dataset_limpio.csv", "text/csv")