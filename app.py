import subprocess
import sys

# Forzar instalación de plotly al iniciar (solo en producción)
import os
if os.environ.get('STREAMLIT_CLOUD'):
    try:
        import plotly
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(
    page_title="TP Integrador - Grupo 3",
    page_icon="🌾",
    layout="wide"
)

# ========== FUNCIONES DE LIMPIEZA ==========
def convertir_columnas_numericas(df):
    """Convierte columnas que deberían ser numéricas"""
    columnas_numericas = [
        'Rentabilidad_Porcentaje', 'Rentabilidad', 'rentabilidad',
        'Produccion_Toneladas', 'Produccion', 'produccion',
        'Costo_Produccion', 'Costo', 'costo',
        'Precio_Venta_Tonelada', 'Precio_Venta',
        'Ingresos', 'ingresos',
        'Superficie_Hectareas', 'Superficie',
        'Edad_Productor', 'Edad',
        'Cantidad_Empleados', 'Empleados',
        'Indice_Sustentabilidad', 'Sustentabilidad'
    ]
    
    for col in df.columns:
        if col in columnas_numericas or any(palabra in col.lower() for palabra in ['porcentaje', 'tonelada', 'costo', 'ingreso', 'superficie', 'edad', 'empleado', 'sustentabilidad']):
            try:
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = df[col].astype(str).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                pass
    return df

def limpiar_dataset(df):
    """Aplica todas las limpiezas necesarias al dataset"""
    df_clean = df.copy()
    cambios = []
    
    # 1. Convertir columnas numéricas
    df_clean = convertir_columnas_numericas(df_clean)
    cambios.append("✅ Convertidas columnas numéricas")
    
    # 2. Corregir valores nulos en Produccion_Toneladas
    if 'Produccion_Toneladas' in df_clean and 'Ingresos' in df_clean and 'Precio_Venta_Tonelada' in df_clean:
        mask_null = df_clean['Produccion_Toneladas'].isna()
        if mask_null.sum() > 0:
            df_clean.loc[mask_null, 'Produccion_Toneladas'] = (
                df_clean.loc[mask_null, 'Ingresos'] / df_clean.loc[mask_null, 'Precio_Venta_Tonelada']
            )
            cambios.append(f"✅ Corregidos {mask_null.sum()} valores nulos en Produccion_Toneladas")
    
       # 3. Estandarizar columnas categóricas específicas
    # Uso_Riego: unificar todas las variantes
    if 'Uso_Riego' in df_clean.columns:
        df_clean['Uso_Riego'] = df_clean['Uso_Riego'].astype(str).str.strip().str.lower()
        df_clean['Uso_Riego'] = df_clean['Uso_Riego'].map({'si': 'Sí', 'sí': 'Sí', 'no': 'No'})
        cambios.append("✅ Estandarizada columna: Uso_Riego")
    
    # Actividad: capitalizar
    if 'Actividad' in df_clean.columns:
        df_clean['Actividad'] = df_clean['Actividad'].astype(str).str.strip().str.capitalize()
        cambios.append("✅ Estandarizada columna: Actividad")
    
    # Provincia: title (primeras letras mayúsculas)
    if 'Provincia' in df_clean.columns:
        df_clean['Provincia'] = df_clean['Provincia'].astype(str).str.strip().str.title()
        cambios.append("✅ Estandarizada columna: Provincia")
    
    # Nivel_Tecnificacion: capitalizar
    if 'Nivel_Tecnificacion' in df_clean.columns:
        df_clean['Nivel_Tecnificacion'] = df_clean['Nivel_Tecnificacion'].astype(str).str.strip().str.capitalize()
        cambios.append("✅ Estandarizada columna: Nivel_Tecnificacion")
        
    # 4. Corregir ingresos inconsistentes
    if all(col in df_clean.columns for col in ['Ingresos', 'Produccion_Toneladas', 'Precio_Venta_Tonelada']):
        ingresos_calculados = df_clean['Produccion_Toneladas'] * df_clean['Precio_Venta_Tonelada']
        diff = abs(df_clean['Ingresos'] - ingresos_calculados)
        inconsistentes = (diff > 1) & (diff / df_clean['Ingresos'] > 0.05)
        if inconsistentes.sum() > 0:
            df_clean.loc[inconsistentes, 'Ingresos'] = ingresos_calculados[inconsistentes]
            cambios.append(f"✅ Corregidos {inconsistentes.sum()} registros con ingresos inconsistentes")
    
    # 5. Agregar columna de outliers
    if 'Rentabilidad_Porcentaje' in df_clean.columns:
        df_clean['outlier_rentabilidad'] = df_clean['Rentabilidad_Porcentaje'] > 500
        cambios.append("✅ Agregada columna 'outlier_rentabilidad'")
    
    # 6. Eliminar registros con datos inválidos (opcional)
    # Filtrar superficies negativas
    if 'Superficie_Hectareas' in df_clean.columns:
        original_len = len(df_clean)
        df_clean = df_clean[df_clean['Superficie_Hectareas'] > 0]
        if len(df_clean) < original_len:
            cambios.append(f"✅ Eliminados {original_len - len(df_clean)} registros con superficie negativa")
    
    # 7. Filtrar edades fuera de rango (si existe la columna)
    if 'Edad_Productor' in df_clean.columns:
        original_len = len(df_clean)
        df_clean = df_clean[(df_clean['Edad_Productor'] >= 18) & (df_clean['Edad_Productor'] <= 100)]
        if len(df_clean) < original_len:
            cambios.append(f"✅ Eliminados {original_len - len(df_clean)} registros con edad fuera de rango")
    
    return df_clean, cambios

# ========== CARGAR DATASET ==========
@st.cache_data
def cargar_y_limpiar_dataset():
    """Carga el dataset original y aplica limpieza automática"""
    archivo = Path("data/dataset_agropecuario.csv")
    
    if not archivo.exists():
        return None, None, "❌ No se encontró el archivo en data/dataset_agropecuario.csv"
    
    # Cargar original
    df_raw = pd.read_csv(archivo)
    
    # Aplicar limpieza
    df_clean, cambios = limpiar_dataset(df_raw)
    
    return df_raw, df_clean, cambios

# Cargar y limpiar
df_raw, df_clean, mensaje_limpieza = cargar_y_limpiar_dataset()

# Título principal
st.title("🌾 Análisis del Sector Agropecuario Argentino")
st.markdown("### Producción, Costos y Rentabilidad")
st.markdown("**Grupo 3:** Rodolfo Nicolás Aguirre, María Florencia Ardanaz, Juan Manuel Bidegain, Lourdes Reynaldo")
st.markdown("---")

if df_clean is not None:
    st.success("✅ Dataset cargado y limpiado correctamente")
    
    # Guardar AMBOS datasets en session_state
    st.session_state['df_raw'] = df_raw           # Original (por si se necesita)
    st.session_state['df'] = df_clean             # Limpio (para análisis)
    st.session_state['df_limpio'] = df_clean      # Alias para claridad
    st.session_state['PLOTLY_AVAILABLE'] = PLOTLY_AVAILABLE
    
    # Mostrar resumen de limpieza
    with st.expander("🧹 Resumen de limpieza aplicada", expanded=False):
        for cambio in mensaje_limpieza:
            st.info(cambio)
    
    # Métricas del dataset limpio
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registros originales", len(df_raw))
    with col2:
        st.metric("Registros después limpieza", len(df_clean))
    with col3:
        st.metric("Registros eliminados", len(df_raw) - len(df_clean))
    
    # Vista previa del dataset LIMPIO
    with st.expander("📋 Vista previa del dataset LIMPIO", expanded=False):
        st.dataframe(df_clean.head(10), use_container_width=True)
        
        # Mostrar tipos de datos después de limpieza
        st.write("**Tipos de datos después de limpieza:**")
        tipos_df = pd.DataFrame({
            'Columna': df_clean.columns,
            'Tipo': df_clean.dtypes.values,
            'Valores nulos': df_clean.isnull().sum().values
        })
        st.dataframe(tipos_df, use_container_width=True)
    
    # Opción para descargar dataset limpio
    csv = df_clean.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Descargar dataset LIMPIO (CSV)",
        csv,
        "dataset_agropecuario_limpio.csv",
        "text/csv"
    )
    
else:
    st.error(mensaje_limpieza)
    st.stop()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/argentina.png", width=80)
st.sidebar.title("📋 Navegación")
st.sidebar.info(f"📊 Dataset limpio: {len(df_clean):,} registros")

# Métricas en sidebar (usando dataset LIMPIO)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Resumen rápido (datos limpios)")

if 'Rentabilidad_Porcentaje' in df_clean.columns:
    rent_mean = df_clean['Rentabilidad_Porcentaje'].mean()
    if not pd.isna(rent_mean):
        st.sidebar.metric("💰 Rentabilidad promedio", f"{rent_mean:.1f}%")

if 'Produccion_Toneladas' in df_clean.columns:
    prod_mean = df_clean['Produccion_Toneladas'].mean()
    if not pd.isna(prod_mean):
        st.sidebar.metric("🌾 Producción promedio", f"{prod_mean:.0f} ton")

if 'Indice_Sustentabilidad' in df_clean.columns:
    sust_mean = df_clean['Indice_Sustentabilidad'].mean()
    if not pd.isna(sust_mean):
        st.sidebar.metric("🌱 Sustentabilidad", f"{sust_mean:.1f}/100")

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
        if 'Produccion_Toneladas' in df_clean.columns:
            prod_total = df_clean['Produccion_Toneladas'].sum() / 1_000_000
            st.metric("📊 Producción total en dataset", f"{prod_total:.1f} M toneladas")
        if 'Provincia' in df_clean.columns:
            st.metric("🗺️ Provincias representadas", df_clean['Provincia'].nunique())

# Actividad 2
with st.expander("📊 Actividad 2 - Comprensión del dataset", expanded=False):
    st.markdown("### Características del dataset (después de limpieza)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registros", f"{len(df_clean):,}")
    with col2:
        st.metric("Variables", len(df_clean.columns))
    with col3:
        st.metric("Valores nulos", df_clean.isnull().sum().sum())
    
    st.markdown("### Variables del dataset limpio")
    var_info = pd.DataFrame({
        'Variable': df_clean.columns,
        'Tipo': df_clean.dtypes.values,
        'Valores nulos': df_clean.isnull().sum().values,
        '% Nulos': (df_clean.isnull().sum() / len(df_clean) * 100).round(2).values
    })
    st.dataframe(var_info, use_container_width=True)

# Actividad 3 y 4 (resumen)
with st.expander("🔍 Actividades 3 y 4 - Diagnóstico y limpieza", expanded=False):
    st.markdown("### Problemas detectados y corregidos")
    
    st.markdown("""
    | Problema | Solución | Registros afectados |
    |---|---|---|
    | Valores nulos en Produccion_Toneladas | Imputación: Ingresos / Precio_Venta | ~219 |
    | Inconsistencias en categorías | Estandarización a formato uniforme | Todos |
    | Superficie negativa | Eliminación de registros | ~29 |
    | Edad fuera de rango (18-100) | Eliminación de registros | ~50 |
    | Rentabilidad extrema (>500%) | Marcado como outlier | ~15 |
    """)
    
    st.info(f"**Resultado:** {len(df_raw) - len(df_clean)} registros eliminados por valores inválidos. {len(df_clean)} registros limpios para análisis.")

# Footer
st.markdown("---")
st.markdown("""
### 📱 Para el análisis COMPLETO con datos LIMPIOS

Usá el **menú ☰ en la esquina superior izquierda** para navegar a:
- **1_Limpieza** → Proceso detallado de limpieza
- **2_AED** → Análisis estadístico con datos LIMPIOS
- **3_Dashboard** → Dashboard ejecutivo con datos LIMPIOS
- **4_Analisis** → Análisis crítico con datos LIMPIOS

✅ **Todos los análisis utilizan el dataset limpio automáticamente**
""")