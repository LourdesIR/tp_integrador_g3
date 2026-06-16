import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Intentar importar plotly (opcional)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Limpieza de Datos", layout="wide")

if 'df_raw' in st.session_state and 'df_limpio' in st.session_state:
    df_raw = st.session_state['df_raw']      # Dataset original (con errores)
    df_limpio = st.session_state['df_limpio']  # Dataset limpio (para análisis)
else:
    st.error("No hay datos cargados")
    st.switch_page("app.py")
    st.stop()

st.title("🧹 Actividades 3 y 4: Diagnóstico y Limpieza de Datos")
st.markdown("---")

# Mostrar información del dataset
st.header("📋 Información del dataset")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Registros totales", len(df))
with col2:
    st.metric("Variables", len(df.columns))
with col3:
    st.metric("Valores nulos", df.isnull().sum().sum())

# ========== ACTIVIDAD 3: DIAGNÓSTICO ==========
st.header("🔍 Actividad 3 - Diagnóstico de calidad de datos")

with st.expander("📊 Valores faltantes por variable", expanded=True):
    missing_df = pd.DataFrame({
        'Variable': df.columns,
        'Valores faltantes': df.isnull().sum(),
        'Porcentaje': (df.isnull().sum() / len(df) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Valores faltantes'] > 0]
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
        
        # Gráfico de barras (solo si plotly está disponible)
        if PLOTLY_AVAILABLE and len(missing_df) > 0:
            fig = px.bar(missing_df, x='Variable', y='Valores faltantes', 
                         title='Distribución de valores faltantes',
                         color='Valores faltantes', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No hay valores faltantes en el dataset")

with st.expander("⚠️ Inconsistencias en variables categóricas", expanded=True):
    st.markdown("### Problemas detectados")
    
    # Revisar columnas categóricas
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() < 20:  # Solo para columnas con pocas categorías
            valores = df[col].value_counts()
            st.write(f"**{col}:** {len(valores)} categorías únicas")
            
            # Detectar posibles inconsistencias (mayúsculas/minúsculas)
            valores_lower = df[col].astype(str).str.lower().value_counts()
            if len(valores) > len(valores_lower):
                st.warning(f"⚠️ Posibles inconsistencias en {col} (ej: 'Si' vs 'SI' vs 'sí')")
                st.write("Valores encontrados:")
                st.write(valores.head(10))
            st.write("---")

with st.expander("📈 Valores fuera de rango", expanded=True):
    problemas = []
    
    # Verificar columnas numéricas
    for col in df.select_dtypes(include=[np.number]).columns:
        negativos = (df[col] < 0).sum()
        if negativos > 0:
            problemas.append(f"⚠️ **{col}:** {negativos} valores negativos")
    
    if 'Edad_Productor' in df.columns:
        edad_fuera = ((df['Edad_Productor'] < 18) | (df['Edad_Productor'] > 100)).sum()
        if edad_fuera > 0:
            problemas.append(f"👤 **Edad_Productor:** {edad_fuera} registros fuera de rango (18-100 años)")
    
    if 'Rentabilidad_Porcentaje' in df.columns:
        rent_extrema = (df['Rentabilidad_Porcentaje'] > 500).sum()
        if rent_extrema > 0:
            problemas.append(f"💰 **Rentabilidad >500%:** {rent_extrema} valores atípicos extremos")
    
    if 'Indice_Sustentabilidad' in df.columns:
        sust_fuera = ((df['Indice_Sustentabilidad'] < 0) | (df['Indice_Sustentabilidad'] > 100)).sum()
        if sust_fuera > 0:
            problemas.append(f"🌱 **Indice_Sustentabilidad:** {sust_fuera} valores fuera de rango (0-100)")
    
    if problemas:
        for p in problemas:
            st.markdown(p)
    else:
        st.success("✅ No se detectaron valores fuera de rango")

# ========== ACTIVIDAD 4: LIMPIEZA ==========
st.header("🛠️ Actividad 4 - Limpieza y preparación de datos")

st.markdown("""
### Estrategias de limpieza aplicadas:

1. **Valores faltantes en Produccion_Toneladas**
   - Imputación mediante fórmula: `Producción = Ingresos / Precio_Venta_Tonelada`
   
2. **Estandarización de categorías**
   - Unificar mayúsculas/minúsculas en variables categóricas
   - Corregir tildes y espacios
   
3. **Corrección de valores fuera de rango**
   - Valores negativos → marcados para revisión
   - Rentabilidad extrema (>500%) → identificados como outliers
   
4. **Consistencia financiera**
   - Verificar relación entre Ingresos, Producción y Precio
""")

if st.button("🧹 Ejecutar limpieza completa", type="primary"):
    df_clean = df.copy()
    cambios_realizados = []
    
    # 1. Corregir valores nulos en Produccion_Toneladas
    if 'Produccion_Toneladas' in df_clean and 'Ingresos' in df_clean and 'Precio_Venta_Tonelada' in df_clean:
        mask_null = df_clean['Produccion_Toneladas'].isna()
        if mask_null.sum() > 0:
            df_clean.loc[mask_null, 'Produccion_Toneladas'] = (
                df_clean.loc[mask_null, 'Ingresos'] / df_clean.loc[mask_null, 'Precio_Venta_Tonelada']
            )
            cambios_realizados.append(f"✅ Corregidos {mask_null.sum()} valores nulos en Produccion_Toneladas")
    
    # 2. Estandarizar columnas categóricas
    for col in df_clean.select_dtypes(include=['object']).columns:
        if df_clean[col].nunique() < 20:
            original = df_clean[col].copy()
            df_clean[col] = df_clean[col].astype(str).str.strip().str.capitalize()
            if not df_clean[col].equals(original):
                cambios_realizados.append(f"✅ Estandarizada columna: {col}")
    
    # 3. Corregir ingresos inconsistentes
    if all(col in df_clean.columns for col in ['Ingresos', 'Produccion_Toneladas', 'Precio_Venta_Tonelada']):
        ingresos_calculados = df_clean['Produccion_Toneladas'] * df_clean['Precio_Venta_Tonelada']
        diff = abs(df_clean['Ingresos'] - ingresos_calculados)
        inconsistentes = (diff > 1) & (diff / df_clean['Ingresos'] > 0.05)  # Diferencia >5%
        if inconsistentes.sum() > 0:
            df_clean.loc[inconsistentes, 'Ingresos'] = ingresos_calculados[inconsistentes]
            cambios_realizados.append(f"✅ Corregidos {inconsistentes.sum()} registros con ingresos inconsistentes")
    
    # 4. Agregar columna de outliers
    if 'Rentabilidad_Porcentaje' in df_clean.columns:
        df_clean['outlier_rentabilidad'] = df_clean['Rentabilidad_Porcentaje'] > 500
        cambios_realizados.append("✅ Agregada columna 'outlier_rentabilidad'")
    
    # Mostrar resultados
    st.success(f"✅ Limpieza completada. {len(cambios_realizados)} transformaciones aplicadas.")
    
    for cambio in cambios_realizados:
        st.info(cambio)
    
    # Mostrar comparación
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Registros antes", len(df))
    with col2:
        st.metric("Registros después", len(df_clean))
    
    # Guardar en session_state
    st.session_state['df_clean'] = df_clean
    
    # Opción para descargar
    csv = df_clean.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Descargar dataset limpio (CSV)",
        csv,
        "dataset_agropecuario_limpio.csv",
        "text/csv",
        type="primary"
    )
    
    # Mostrar preview
    st.subheader("📊 Vista previa del dataset limpio")
    st.dataframe(df_clean.head(10), use_container_width=True)

# Mostrar estadísticas antes de limpiar
st.subheader("📈 Estadísticas actuales (pre-limpieza)")
cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
if cols_numericas:
    st.dataframe(df[cols_numericas].describe(), use_container_width=True)

st.markdown("---")
st.caption("💡 **Nota:** La limpieza preserva todos los registros originales. Los valores problemáticos se corrigen cuando es posible o se marcan como outliers.")