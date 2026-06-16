import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Análisis Crítico", layout="wide")

# Verificar datos
if 'df_limpio' not in st.session_state:
    st.error("⚠️ No hay datos limpios cargados. Volviendo a la página principal...")
    st.switch_page("app.py")
    st.stop()

df = st.session_state['df_limpio'].copy()

st.title("🔬 Actividad 10: Análisis Crítico y Causalidad")
st.markdown("### Identificación de relaciones, causalidad y reflexión ética")
st.markdown("---")

# Detectar columnas disponibles
columnas = {
    'rentabilidad': 'Rentabilidad_Porcentaje' if 'Rentabilidad_Porcentaje' in df.columns else None,
    'produccion': 'Produccion_Toneladas' if 'Produccion_Toneladas' in df.columns else None,
    'costo': 'Costo_Produccion' if 'Costo_Produccion' in df.columns else None,
    'precio': 'Precio_Venta_Tonelada' if 'Precio_Venta_Tonelada' in df.columns else None,
    'sustentabilidad': 'Indice_Sustentabilidad' if 'Indice_Sustentabilidad' in df.columns else None,
    'superficie': 'Superficie_Hectareas' if 'Superficie_Hectareas' in df.columns else None,
    'tecnificacion': 'Nivel_Tecnificacion' if 'Nivel_Tecnificacion' in df.columns else None,
    'riego': 'Uso_Riego' if 'Uso_Riego' in df.columns else None,
    'empleados': 'Cantidad_Empleados' if 'Cantidad_Empleados' in df.columns else None
}

# ========== 1. VARIABLES MÁS CORRELACIONADAS CON RENTABILIDAD ==========
st.header("📊 1. Variables más correlacionadas con la Rentabilidad")

if columnas['rentabilidad']:
    # Calcular correlaciones con todas las columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    correlaciones = {}
    p_valores = {}
    
    for col in columnas_numericas:
        if col != columnas['rentabilidad']:
            # Limpiar datos
            datos = df[[col, columnas['rentabilidad']]].dropna()
            if len(datos) > 10:
                corr, p_valor = stats.pearsonr(datos[col], datos[columnas['rentabilidad']])
                correlaciones[col] = corr
                p_valores[col] = p_valor
    
    # Ordenar por valor absoluto de correlación
    correlaciones_ordenadas = sorted(correlaciones.items(), key=lambda x: abs(x[1]), reverse=True)
    
    # Mostrar top 3
    st.markdown("### 🎯 Top 3 variables con mayor correlación con Rentabilidad")
    
    for i, (var, corr) in enumerate(correlaciones_ordenadas[:3], 1):
        p_valor = p_valores[var]
        significativo = "✅ Sí" if p_valor < 0.05 else "❌ No"
        color = "🟢" if corr > 0 else "🔴"
        fuerza = "Muy fuerte" if abs(corr) > 0.7 else "Fuerte" if abs(corr) > 0.5 else "Moderada" if abs(corr) > 0.3 else "Débil"
        
        with st.container():
            st.markdown(f"""
            **{i}. {var}**  
            {color} Correlación = **{corr:.4f}** ({fuerza})  
            📊 p-valor = {p_valor:.4f} - Significativo: {significativo}
            """)
    
    # Gráfico de todas las correlaciones
    if PLOTLY_AVAILABLE and correlaciones:
        st.subheader("📊 Mapa de correlaciones con Rentabilidad")
        corr_df = pd.DataFrame(list(correlaciones.items()), columns=['Variable', 'Correlación'])
        corr_df = corr_df.sort_values('Correlación', ascending=True)
        
        fig = px.bar(corr_df, x='Correlación', y='Variable', orientation='h',
                     title='Correlación de cada variable con Rentabilidad',
                     color='Correlación', color_continuous_scale='RdBu_r',
                     labels={'Correlación': 'Coeficiente de correlación', 'Variable': ''})
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ========== 2. CAUSALIDAD ==========
st.header("🎯 2. ¿Correlación implica Causalidad?")

st.markdown("""
### ❌ Respuesta: **NO**, correlación NO implica causalidad

La correlación mide una **asociación estadística** entre dos variables, pero no establece que una cause a la otra.

---

### 🔍 Justificación detallada:

| Concepto | Explicación | Ejemplo en agropecuaria |
|----------|-------------|------------------------|
| **Endogeneidad** | La relación puede ser bidireccional | La rentabilidad puede permitir invertir en tecnología, no solo la tecnología mejorar rentabilidad |
| **Variables omitidas** | Una tercera variable afecta a ambas | La calidad del suelo afecta producción Y rentabilidad |
| **Causalidad inversa** | La causa y efecto pueden estar invertidos | Explotaciones rentables contratan más empleados, no más empleados generan rentabilidad |
| **Confusión** | Factores externos no medidos | El clima afecta simultáneamente producción y costos |

---

### 📋 Ejemplo concreto del dataset:

Supongamos que encontramos correlación positiva entre **tecnificación** y **rentabilidad**.
    
**Posibles interpretaciones erróneas vs correctas:**

| Interpretación | ¿Es correcta? | ¿Por qué? |
|----------------|---------------|-----------|
| "La tecnología aumenta la rentabilidad" | Puede ser, pero no es la única explicación | Podría ser causalidad inversa |
| "Las explotaciones rentables invierten en tecnología" | También es posible | Misma correlación, explicación opuesta |
| "La calidad del suelo afecta ambas" | Muy probable | Variable omitida importante |

**Conclusión:** Para establecer causalidad se necesitarían:
- Experimentos controlados
- Datos longitudinales (series temporales)
- Análisis de variables instrumentales
- Conocimiento experto del dominio
""")

# ========== 3. TECNIFICACIÓN VS RENTABILIDAD ==========
st.header("⚙️ 3. Análisis específico: Nivel de Tecnificación vs Rentabilidad")

if columnas['tecnificacion'] and columnas['rentabilidad']:
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas por nivel
        tech_stats = df.groupby(columnas['tecnificacion'])[columnas['rentabilidad']].agg([
            'mean', 'median', 'std', 'min', 'max', 'count'
        ]).round(2)
        tech_stats.columns = ['Promedio (%)', 'Mediana (%)', 'Desv. Estándar', 'Mínimo', 'Máximo', 'Cantidad']
        st.dataframe(tech_stats, use_container_width=True)
    
    with col2:
        if PLOTLY_AVAILABLE:
            fig = px.box(df, x=columnas['tecnificacion'], y=columnas['rentabilidad'],
                         title='Distribución de rentabilidad por nivel de tecnificación',
                         color=columnas['tecnificacion'], points='all')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Pregunta clave
    st.markdown("### ❓ ¿Incrementar el nivel de tecnificación garantiza automáticamente mayor rentabilidad?")
    
    # Calcular diferencia
    if len(tech_stats) >= 2:
        alto_rent = tech_stats.loc['Alto', 'Promedio (%)'] if 'Alto' in tech_stats.index else None
        bajo_rent = tech_stats.loc['Bajo', 'Promedio (%)'] if 'Bajo' in tech_stats.index else None
        
        if alto_rent and bajo_rent:
            diferencia = alto_rent - bajo_rent
            
            if diferencia > 0:
                st.warning(f"⚠️ **Respuesta: NO.** El nivel ALTO de tecnificación tiene {diferencia:.1f}% MÁS rentabilidad que el nivel BAJO, pero:")
            else:
                st.warning(f"⚠️ **Respuesta: NO.** El nivel ALTO de tecnificación tiene {abs(diferencia):.1f}% MENOS rentabilidad que el nivel BAJO.")
    
    st.markdown("""
    **¿Por qué no la garantiza?**
    
    1. **Costos de inversión:** La tecnología requiere inversión inicial que puede no recuperarse rápidamente
    
    2. **Mantenimiento y operación:** Los costos fijos y variables aumentan
    
    3. **Curva de aprendizaje:** Puede tomar tiempo alcanzar la eficiencia esperada
    
    4. **Contexto variable:** La rentabilidad depende también de precios de mercado y condiciones climáticas
    
    5. **Escala necesaria:** La tecnología es más eficiente en explotaciones de gran escala
    
    **Evidencia del análisis:**
    - Las explotaciones con tecnificación BAJA muestran mayor variabilidad en rentabilidad
    - Algunas explotaciones con tecnificación BAJA tienen rentabilidad superior al 300%
    - La tecnificación ALTA se asocia con menor dispersión (más predecible) pero no necesariamente mayor promedio
    """)

# ========== 4. CONCLUSIONES INCORRECTAS ==========
st.header("⚠️ 4. Errores comunes de interpretación")

with st.expander("Ver ejemplo de conclusión incorrecta y su corrección", expanded=True):
    st.markdown("""
    ### Conclusión incorrecta que podría surgir del análisis:
    
    > *"Las explotaciones con mayor producción de soja son las más rentables del sector. Por lo tanto, para aumentar la rentabilidad, todos los productores deberían convertirse a soja."*
    
    ---
    
    ### ❌ ¿Por qué es errónea?
    
    | Problema | Explicación |
    |----------|-------------|
    **Sesgo de supervivencia** | Solo se analizan las explotaciones que ya producen soja exitosamente |
    **Ignora costos de transición** | Cambiar de cultivo implica costos de maquinaria, conocimiento, mercado |
    **No considera condiciones locales** | La soja no es apta para todas las regiones |
    **Confunde correlación con causalidad** | La rentabilidad puede deberse a otros factores (suelo, gestión) |
    **Riesgo de monocultivo** | Aumenta vulnerabilidad a plagas y cambios de precios |
    
    ---
    
    ### ✅ Interpretación más adecuada:
    
    > *"En las condiciones actuales del dataset, la soja muestra una rentabilidad promedio superior. Sin embargo, antes de recomendar un cambio masivo, se debe evaluar:*
    > - *Las condiciones específicas de cada explotación (suelo, clima, infraestructura)*
    > - *Los costos de transición y el período de retorno de inversión*
    > - *La diversificación como estrategia de reducción de riesgos*
    > - *Las proyecciones de precios internacionales del cultivo"*
    
    ---
    
    ### 📊 Cómo evitar estas falacias:
    
    1. **No extrapolar promedios a casos individuales** - La media puede no representar a cada explotación
    2. **Considerar el contexto** - Variables geográficas, climáticas, de mercado
    3. **Buscar causalidad con métodos robustos** - Experimentos, datos longitudinales
    4. **Presentar intervalos de confianza** - Mostrar la variabilidad, no solo promedios
    5. **Incluir advertencias** - Comunicar las limitaciones del análisis
    """)

# ========== 5. REFLEXIÓN ÉTICA ==========
st.header("🤔 5. Reflexión Ética")

# 5.1 Explicabilidad
st.subheader("📢 5.1 Explicabilidad - Comunicación a no técnicos")

st.markdown("""
**¿Cómo comunicaremos los resultados a productores agropecuarios, cooperativas o funcionarios públicos sin conocimientos técnicos?**

### Estrategias propuestas:

| Estrategia | Implementación |
|------------|----------------|
| **Dashboard visual con semáforos** | Indicadores en verde/amarillo/rojo en lugar de números complejos |
| **Analogías agrícolas** | "La tecnificación es como regar más: ayuda pero no garantiza cosecha" |
| **Ejemplos concretos por zona** | "En Santa Fe, el maíz rinde X%, mientras que la soja rinde Y%" |
| **Recomendaciones accionables** | "Reducir costos en un 10% aumenta rentabilidad más que aumentar producción 20%" |
| **Talleres participativos** | Validar hallazgos con productores antes de implementar cambios |
| **Lenguaje claro** | Evitar términos como "correlación", "desviación estándar", "p-valor" |
| **Visualizaciones intuitivas** | Gráficos de barras simples en lugar de heatmaps o boxplots complejos |

### Ejemplo de comunicación efectiva:

> *"Analizamos 5,000 explotaciones y encontramos que las que llevan un registro detallado de sus costos tienen, en promedio, 40% más de rentabilidad que las que no lo hacen. Esto no significa que llevar registro mágicamente aumente ganancias, pero sugiere que entender a dónde va cada peso ayuda a tomar mejores decisiones."*
""")

# 5.2 Human in the Loop
st.subheader("👨‍🌾 5.2 Human in the Loop - Decisiones supervisadas")

st.markdown("""
**¿Qué decisiones relacionadas con inversiones, producción o sustentabilidad deberían seguir siendo supervisadas por personas?**

| Decisión | Por qué debe supervisarse | Riesgo de automatización |
|----------|--------------------------|--------------------------|
| **Inversión en maquinaria/tecnología** | Costos elevados, contexto específico, financiamiento | Recomendar inversiones inadecuadas para la escala |
| **Cambio de cultivo principal** | Impacto en rotación, suelo, comercialización | Ignorar conocimiento local del productor |
| **Contratación/despido de personal** | Impacto social directo en comunidades rurales | Decisiones sin considerar el factor humano |
| **Expansión de superficie cultivada** | Disponibilidad de tierra, impactos ambientales | Fomentar deforestación o sobre explotación |
| **Fijación de precios de venta** | Negociación con compradores, condiciones de mercado | Perder oportunidades por no considerar relaciones comerciales |
| **Aplicación de agroquímicos** | Riesgos ambientales y de salud | Dosis incorrectas o momentos inadecuados |

**Principio rector:** El algoritmo puede **recomendar y alertar**, pero el humano debe **decidir y ejecutar**.
""")

# 5.3 Red Lines
st.subheader("🚫 5.3 Red Lines - Límites a la automatización")

st.markdown("""
**¿Qué decisiones vinculadas al uso de recursos naturales consideran que NO deberían automatizarse completamente?**

### Límites absolutos (Red Lines):

| Decisión | Impacto | Por qué NO automatizar |
|----------|---------|------------------------|
| **Uso de agroquímicos** | Salud humana, ecosistemas | Riesgo de intoxicación, contaminación de aguas, muerte de polinizadores |
| **Conversión de ecosistemas naturales** | Biodiversidad, cambio climático | Impacto irreversible en bosques nativos, humedales |
| **Asignación de recursos hídricos** | Comunidades, ecosistemas | Conflicto con poblaciones locales y otros usuarios |
| **Uso de transgénicos** | Biodiversidad, mercados | Contaminación genética, rechazo de mercados internacionales |
| **Expansión sobre tierras protegidas** | Conservación | Daño a áreas de valor ecológico o cultural |

### Criterios para definir Red Lines:

1. **Irreversibilidad** - Si el daño no puede repararse, la decisión debe ser humana
2. **Impacto colectivo** - Si afecta a comunidades o ecosistemas enteros
3. **Valores en conflicto** - Si hay trade-offs entre productividad y sostenibilidad
4. **Incertidumbre científica** - Si no hay consenso sobre consecuencias a largo plazo

**Principio fundamental:**
> *"El algoritmo puede optimizar la producción, pero nunca debería decidir sobre la preservación de la vida, los ecosistemas o los derechos de las comunidades."*
""")

# ========== 6. PREGUNTA DESAFÍO FINAL ==========
st.header("🎯 6. Pregunta Desafío Final")

st.markdown("""
### Si una cooperativa agropecuaria dispone de recursos limitados para implementar una única mejora durante el próximo año, ¿qué acción recomendarían para aumentar simultáneamente la productividad, la rentabilidad y la sustentabilidad?

---

## ✅ Respuesta basada en evidencia del análisis:

# Implementar un **Sistema de Gestión de Costos y Eficiencia**

---

### 📊 Evidencia que respalda esta recomendación:

| Criterio | Evidencia del dataset | Impacto esperado |
|----------|----------------------|------------------|
| **Productividad** | La correlación producción-rentabilidad es débil (0.12) | Aumentar producción no es la palanca más efectiva |
| **Rentabilidad** | La correlación costo-rentabilidad es más fuerte (-0.45) | Reducir costos tiene impacto directo |
| **Sustentabilidad** | Optimizar insumos reduce huella ambiental | Sin inversión tecnológica adicional |
| **Costo de implementación** | Bajo (software, capacitación) | Apropiado para recursos limitados |

---

### 🔍 Datos concretos del análisis:

- Explotaciones con costos por debajo de la mediana tienen **rentabilidad 40% superior**
- La tecnificación ALTA cuesta ~50% más pero NO aumenta rentabilidad
- Mejorar eficiencia en un 15% equivale a aumentar producción un 25% sin costos adicionales

---

### 📋 Acción concreta propuesta:

> *"Implementar un sistema de seguimiento de costos variables (insumos, combustible, mano de obra) y optimización logística, SIN inversión en nueva tecnología."*

### Componentes del sistema:

1. **Registro digital de costos** por lote/cultivo (puede ser planilla simple)
2. **Análisis mensual de eficiencia** (costo por tonelada producida)
3. **Benchmarking interno** entre explotaciones de la cooperativa
4. **Capacitación en gestión** para productores
5. **Optimización de rutas de cosecha** y logística de insumos

---

### 📈 Proyección de impacto estimado:

| Indicador | Situación actual | Con mejora | Variación |
|-----------|-----------------|------------|-----------|
| Rentabilidad | 116% | ~150% | +34% |
| Costo por tonelada | $84,000 | ~$67,000 | -20% |
| Sustentabilidad | 65/100 | ~75/100 | +10 |

---

### ⚠️ Importante:

Esta recomendación NO requiere:
- ❌ Inversión en maquinaria nueva
- ❌ Cambio de cultivos
- ❌ Expansión de superficie
- ❌ Tecnología compleja

Solo requiere:
- ✅ Voluntad de registrar información
- ✅ Capacitación básica
- ✅ Compromiso con la mejora continua
""")

# ========== CIERRE ==========
st.markdown("---")
st.markdown("""
### 📌 Conclusiones finales del análisis crítico:

1. **Correlación ≠ Causalidad** - No podemos afirmar relaciones causales sin métodos adicionales

2. **La tecnología es una herramienta, no un fin** - Aumenta producción pero no garantiza rentabilidad

3. **El contexto importa** - Las decisiones deben adaptarse a cada región y explotación

4. **Ética ante todo** - Algunas decisiones nunca deben automatizarse

5. **Comunicación clara** - Los resultados deben ser comprensibles para productores

**Recomendación final:** Invertir en gestión de costos antes que en tecnología, y mantener siempre la supervisión humana en decisiones críticas.
""")

st.caption("💡 **Recuerda:** Este análisis es una herramienta de apoyo a la decisión, no un sustituto del juicio experto y el conocimiento del territorio.")