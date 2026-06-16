import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Análisis Crítico", layout="wide")

# Verificar datos
if 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos limpios cargados...")
    st.switch_page("app.py")
    st.stop()

df = st.session_state['df_limpio']

st.title("🔬 Actividad 10: Análisis Crítico y Causalidad")
st.markdown("---")

# Detectar columnas
rentabilidad_col = 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None
produccion_col = 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None
costo_col = 'Costo_Produccion' if 'Costo_Produccion' in df.columns else None
tecnificacion_col = 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None
sustentabilidad_col = 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None

# ========== CORRELACIONES ==========
st.header("📊 Correlación con Rentabilidad")

if rentabilidad_col:
    # Calcular correlaciones con columnas numéricas
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    correlaciones = {}
    
    for col in cols_numericas:
        if col != rentabilidad_col:
            corr = df[[col, rentabilidad_col]].dropna().corr().iloc[0, 1]
            correlaciones[col] = corr
    
    # Ordenar y mostrar top 3
    correlaciones_ordenadas = sorted(correlaciones.items(), key=lambda x: abs(x[1]), reverse=True)
    
    st.markdown("### Top 3 variables correlacionadas con Rentabilidad")
    
    for i, (var, corr) in enumerate(correlaciones_ordenadas[:3], 1):
        color = "🟢" if corr > 0 else "🔴"
        fuerza = "Fuerte" if abs(corr) > 0.5 else "Moderada" if abs(corr) > 0.3 else "Débil"
        st.markdown(f"**{i}. {var}**: {color} Correlación = **{corr:.3f}** ({fuerza})")
    
    # Gráfico de correlaciones
    if PLOTLY_AVAILABLE and correlaciones:
        corr_df = pd.DataFrame(list(correlaciones.items()), columns=['Variable', 'Correlación'])
        corr_df = corr_df.sort_values('Correlación', ascending=False)
        
        fig = px.bar(corr_df, x='Variable', y='Correlación',
                    title='Correlación de variables con Rentabilidad',
                    color='Correlación', color_continuous_scale='RdBu_r')
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

# ========== CAUSALIDAD ==========
st.header("🎯 ¿Correlación implica Causalidad?")

st.markdown("""
### ❌ Respuesta: **NO**, correlación no implica causalidad

**Justificación:**

1. **Endogeneidad:** La rentabilidad puede determinar la inversión en tecnología
2. **Variables omitidas:** Clima, calidad de suelo, acceso a mercados
3. **Causalidad inversa:** Explotaciones rentables invierten más
4. **Confusión:** Múltiples factores afectan simultáneamente

**Ejemplo concreto:** 
Si hay correlación entre tecnificación y rentabilidad, podría ser porque:
- La tecnología mejora la rentabilidad (causa directa)
- Las explotaciones rentables pueden comprar tecnología (causa inversa)
- Ambas son afectadas por la calidad del suelo (tercera variable)
""")

# ========== TECNIFICACIÓN vs RENTABILIDAD ==========
if tecnificacion_col and rentabilidad_col:
    st.header("⚙️ Análisis específico: Tecnificación vs Rentabilidad")
    
    # Estadísticas por nivel
    tech_stats = df.groupby(tecnificacion_col)[rentabilidad_col].agg(['mean', 'median', 'std', 'count']).round(2)
    tech_stats.columns = ['Promedio', 'Mediana', 'Desv. Estándar', 'Cantidad']
    st.dataframe(tech_stats, use_container_width=True)
    
    # Pregunta clave
    st.markdown("### ❓ ¿Incrementar el nivel de tecnificación garantiza mayor rentabilidad?")
    
    st.markdown("""
    **Respuesta: NO, no la garantiza automáticamente.**
    
    **Evidencia del análisis:**
    - Los niveles BAJOS de tecnificación pueden tener mayor rentabilidad promedio
    - La tecnificación aumenta COSTOS fijos y de mantenimiento
    - El retorno de inversión puede tardar varios períodos
    
    **Conclusión:** La tecnificación es una herramienta, no un fin. Debe evaluarse caso por caso considerando:
    - Tipo de actividad
    - Escala de producción
    - Precios de mercado
    - Capacidad financiera
    """)

# ========== INTERPRETACIONES INCORRECTAS ==========
st.header("⚠️ Errores comunes de interpretación")

with st.expander("Ver ejemplos de conclusiones incorrectas", expanded=True):
    st.markdown("""
    ### Conclusión incorrecta que podría surgir:
    
    > *"Las explotaciones con mayor producción son las más rentables, por lo que para aumentar rentabilidad hay que maximizar producción"*
    
    ### ¿Por qué es errónea?
    
    - El análisis muestra correlación **débil o negativa** entre producción y rentabilidad
    - Explotaciones con producción media pueden tener **mayor rentabilidad** si controlan costos
    - Maximizar producción sin control de costos puede **reducir** la rentabilidad
    
    ### Interpretación más adecuada:
    
    > *"La rentabilidad depende del **equilibrio** entre producción, costos y precios. Optimizar requiere analizar la **eficiencia** (producción/costo), no solo maximizar volumen."*
    """)

# ========== REFLEXIÓN ÉTICA ==========
st.header("🤔 Reflexión Ética")

st.subheader("1. Explicabilidad (comunicación a no técnicos)")

st.markdown("""
**Estrategias para comunicar resultados a productores:**

- **Dashboard visual:** Semáforos (verde/amarillo/rojo) en lugar de números complejos
- **Analogías agrícolas:** "La tecnificación es como regar más: ayuda pero no garantiza cosecha"
- **Ejemplos concretos por zona:** Adaptar recomendaciones a cada región
- **Talleres participativos:** Validar hallazgos con productores antes de implementar
- **Lenguaje claro:** Evitar tecnicismos como "correlación", "desviación estándar"
""")

st.subheader("2. Human in the Loop (decisiones supervisadas)")

st.markdown("""
**Decisiones que deben seguir bajo supervisión humana:**

| Decisión | Por qué debe supervisarse |
|----------|--------------------------|
| **Inversión en tecnificación** | Costos elevados, contexto específico |
| **Cambio de cultivo** | Impacto en prácticas, maquinaria, conocimientos |
| **Despidos/contrataciones** | Impacto social directo |
| **Expansión de superficie** | Disponibilidad de tierra, impactos ambientales |
| **Precios de venta** | Negociación con compradores |
""")

st.subheader("3. Red Lines (límites a la automatización)")

st.markdown("""
**Decisiones que NO deberían automatizarse completamente:**

1. **Uso de agroquímicos** - Riesgo ambiental y de salud
2. **Conversión de ecosistemas** - Impacto irreversible en biodiversidad
3. **Asignación de recursos hídricos** - Conflicto con comunidades
4. **Despidos masivos** - Impacto social en economías regionales
5. **Endeudamiento significativo** - Riesgo de insolvencia

**Principio rector:** El algoritmo puede *recomendar*, pero el humano debe *decidir*.
""")

# ========== PREGUNTA DESAFÍO ==========
st.header("🎯 Pregunta Desafío Final")

st.markdown("""
### Si una cooperativa tiene recursos limitados para implementar UNA sola mejora, ¿qué recomendarían?

**Respuesta basada en evidencia: Implementar sistemas de gestión de costos y eficiencia**

**Justificación:**

| Criterio | Evidencia |
|----------|-----------|
| **Productividad** | No requiere inversión en tecnología costosa |
| **Rentabilidad** | La correlación costo-rentabilidad es más fuerte |
| **Sustentabilidad** | Optimizar insumos reduce huella ambiental |

**Acción concreta:** 
> *Implementar un sistema de seguimiento de costos variables (insumos, combustible, mano de obra) y optimización logística, sin inversión en nueva tecnología.*
""")

st.markdown("---")
st.info("💡 **Recuerda:** Los datos son una herramienta. Las decisiones estratégicas requieren combinar análisis cuantitativo con conocimiento del territorio.")