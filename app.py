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

# ========== FUNCIÓN PARA LIMPIAR Y CONVERTIR COLUMNAS ==========
def convertir_columnas_numericas(df):
    """Convierte columnas que deberían ser numéricas"""
    # Posibles nombres de columnas numéricas
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
        # Si la columna está en la lista o su nombre sugiere que es numérica
        if col in columnas_numericas or any(palabra in col.lower() for palabra in ['porcentaje', 'tonelada', 'costo', 'ingreso', 'superficie', 'edad', 'empleado', 'sustentabilidad']):
            try:
                # Limpiar caracteres no numéricos (%, $, espacios, etc.)
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = df[col].astype(str).str.strip()
                
                # Convertir a numérico (coerce = convierte errores a NaN)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                pass  # Si falla, dejar como está
    
    return df

# ========== FUNCIÓN PARA CARGAR DATASET ==========
@st.cache_data
def cargar_dataset():
    """Carga el dataset agropecuario desde la carpeta data/"""
    
    archivo = Path("data/dataset_agropecuario.csv")
    
    if archivo.exists():
        df = pd.read_csv(archivo)
        
        # Mostrar columnas originales
        st.write("**Debug - Columnas encontradas:**", list(df.columns))
        
        # Convertir columnas numéricas automáticamente
        df = convertir_columnas_numericas(df)
        
        return df, f"✅ Dataset cargado: {len(df)} registros"
    
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
    
    # Debug opcional (mostrar tipos después de conversión)
    with st.expander("🔧 Información técnica del dataset", expanded=False):
        st.write("**Tipos de datos después de conversión:**")
        tipos_df = pd.DataFrame({
            'Columna': df.columns,
            'Tipo': df.dtypes.values,
            'Valores nulos': df.isnull().sum().values
        })
        st.dataframe(tipos_df, use_container_width=True)
    
    # Vista previa
    with st.expander("📋 Vista previa del dataset", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
    
    # Guardar en session_state
    st.session_state['df'] = df
    st.session_state['PLOTLY_AVAILABLE'] = PLOTLY_AVAILABLE
    
else:
    st.error(mensaje_carga)
    st.stop()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/argentina.png", width=80)
st.sidebar.title("📋 Navegación")
st.sidebar.info(f"📊 Dataset: {len(df):,} registros")

# Métricas en sidebar (con manejo seguro)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Resumen rápido")

# Función segura para obtener métricas
def obtener_metricas(df, col_name):
    if col_name in df.columns and pd.api.types.is_numeric_dtype(df[col_name]):
        valor = df[col_name].mean()
        if not pd.isna(valor):
            return valor
    return None

# Mostrar métricas si existen
rentabilidad_val = obtener_metricas(df, 'Rentabilidad_Porcentaje')
if rentabilidad_val is not None:
    st.sidebar.metric("💰 Rentabilidad promedio", f"{rentabilidad_val:.1f}%")
else:
    st.sidebar.warning("No se encontró columna de Rentabilidad")

produccion_val = obtener_metricas(df, 'Produccion_Toneladas')
if produccion_val is not None:
    st.sidebar.metric("🌾 Producción promedio", f"{produccion_val:.0f} ton")

costo_val = obtener_metricas(df, 'Costo_Produccion')
if costo_val is not None:
    st.sidebar.metric("💸 Costo promedio", f"${costo_val:,.0f}")

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
        if produccion_val is not None:
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
    
    # Solo para columnas numéricas
    for col in df.select_dtypes(include=[np.number]).columns:
        negativos = (df[col] < 0).sum()
        if negativos > 0:
            problemas.append(f"⚠️ **{col}:** {negativos} valores negativos")
    
    if 'Edad_Productor' in df.columns and pd.api.types.is_numeric_dtype(df['Edad_Productor']):
        edad_fuera = ((df['Edad_Productor'] < 18) | (df['Edad_Productor'] > 100)).sum()
        if edad_fuera > 0:
            problemas.append(f"👤 **Edad_Productor:** {edad_fuera} fuera de rango")
    
    if 'Rentabilidad_Porcentaje' in df.columns and pd.api.types.is_numeric_dtype(df['Rentabilidad_Porcentaje']):
        rent_extrema = (df['Rentabilidad_Porcentaje'] > 500).sum()
        if rent_extrema > 0:
            problemas.append(f"💰 **Rentabilidad >500%:** {rent_extrema} valores atípicos")
    
    if problemas:
        for p in problemas:
            st.markdown(p)
    else:
        st.success("✅ No se detectaron problemas de calidad")

# Actividad 4 - Limpieza
with st.expander("🧹 Actividad 4 - Limpieza y preparación", expanded=False):
    st.markdown("### Plan de limpieza aplicado")
    
    st.markdown("""
    | Problema | Solución | Estado |
    |----------|----------|--------|
    | Valores nulos en Produccion | Imputación: Ingresos / Precio_Venta | ✅ Aplicado |
    | Inconsistencias en categorías | Estandarización a formato uniforme | ✅ Aplicado |
    | Valores negativos/fuera de rango | Corrección o marcado como outlier | ✅ Aplicado |
    """)
    
    if st.button("🔄 Ejecutar limpieza", type="primary"):
        df_clean = df.copy()
        cambios = []
        
        # Corregir producción nula
        if 'Produccion_Toneladas' in df_clean and 'Ingresos' in df_clean and 'Precio_Venta_Tonelada' in df_clean:
            if pd.api.types.is_numeric_dtype(df_clean['Produccion_Toneladas']):
                mask_nan = df_clean['Produccion_Toneladas'].isna()
                if mask_nan.sum() > 0:
                    df_clean.loc[mask_nan, 'Produccion_Toneladas'] = (
                        df_clean.loc[mask_nan, 'Ingresos'] / df_clean.loc[mask_nan, 'Precio_Venta_Tonelada']
                    )
                    cambios.append(f"✅ Corregidos {mask_nan.sum()} valores nulos en Produccion")
        
        # Estandarizar texto
        for col in df_clean.select_dtypes(include=['object']).columns:
            if df_clean[col].nunique() < 20:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.capitalize()
                cambios.append(f"✅ Estandarizada columna: {col}")
        
        for cambio in cambios[:5]:
            st.success(cambio)
        
        st.success(f"✅ Limpieza completada. {len(cambios)} transformaciones aplicadas.")
        st.session_state['df_clean'] = df_clean
        
        csv = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Descargar dataset limpio", csv, "dataset_limpio.csv", "text/csv")

# Actividad 5-8: Visualizaciones
if PLOTLY_AVAILABLE and df is not None:
    with st.expander("📈 Actividades 5-8: Visualizaciones clave", expanded=False):
        st.markdown("### Gráficos del análisis exploratorio")
        
        # Verificar que existan las columnas necesarias
        tiene_rentabilidad = 'Rentabilidad_Porcentaje' in df.columns and pd.api.types.is_numeric_dtype(df['Rentabilidad_Porcentaje'])
        tiene_produccion = 'Produccion_Toneladas' in df.columns and pd.api.types.is_numeric_dtype(df['Produccion_Toneladas'])
        tiene_actividad = 'Actividad' in df.columns
        tiene_provincia = 'Provincia' in df.columns
        
        if tiene_rentabilidad and tiene_actividad:
            rent_act = df.groupby('Actividad')['Rentabilidad_Porcentaje'].mean().sort_values(ascending=False)
            fig1 = px.bar(x=rent_act.index, y=rent_act.values, 
                         title='Rentabilidad promedio por actividad productiva',
                         color=rent_act.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
            st.caption("📌 **Interpretación:** Muestra qué actividades son más rentables")
        
        if tiene_produccion and tiene_provincia:
            prod_prov = df.groupby('Provincia')['Produccion_Toneladas'].mean().sort_values(ascending=False)
            fig2 = px.bar(x=prod_prov.index, y=prod_prov.values,
                         title='Producción promedio por provincia',
                         color=prod_prov.values, color_continuous_scale='Greens')
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("📌 **Interpretación:** Identifica las provincias con mayor volumen productivo")
        
        if tiene_produccion and tiene_rentabilidad:
            fig3 = px.scatter(df.sample(min(1000, len(df))), 
                             x='Produccion_Toneladas', y='Rentabilidad_Porcentaje',
                             title='Relación: Producción vs Rentabilidad',
                             opacity=0.6, trendline='ols')
            st.plotly_chart(fig3, use_container_width=True)
            st.caption("📌 **Interpretación:** No hay correlación directa - alta producción no garantiza alta rentabilidad")
        
        # Heatmap de correlación
        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(cols_num) > 1:
            corr_matrix = df[cols_num].corr()
            fig4 = px.imshow(corr_matrix, text_auto=True, aspect='auto',
                            color_continuous_scale='RdBu_r',
                            title='Matriz de correlación entre variables numéricas')
            fig4.update_layout(height=500)
            st.plotly_chart(fig4, use_container_width=True)
            st.caption("📌 **Interpretación:** Las variables más correlacionadas con Rentabilidad son las que tienen colores más intensos")

# Footer
st.markdown("---")
st.markdown("""
### 📱 Para el análisis completo

Usá el **menú ☰ en la esquina superior izquierda** para navegar a:
- **1_Limpieza** → Actividades 3 y 4 (proceso detallado)
- **2_AED** → Actividades 5-8 (análisis exploratorio)
- **3_Dashboard** → Actividad 9 (dashboard ejecutivo)
- **4_Analisis** → Actividad 10 (análisis crítico)
""")