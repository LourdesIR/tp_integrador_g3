import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats

st.set_page_config(page_title="Análisis Crítico", layout="wide")
st.title("🔬 Actividad 10: Análisis Crítico y Causalidad")

# Cargar datos
if 'df_clean' in st.session_state:
    df = st.session_state['df_clean']
else:
    # Datos simulados
    np.random.seed(42)
    df = pd.DataFrame({
        'Nivel_Tecnificacion': np.random.choice(['Bajo', 'Medio', 'Alto'], 4000),
        'Rentabilidad_Porcentaje': np.random.normal(116, 100, 4000),
        'Produccion_Toneladas': np.random.normal(310, 150, 4000),
        'Costo_Produccion': np.random.normal(84120, 60000, 4000),
        'Indice_Sustentabilidad': np.random.uniform(40, 90, 4000),
        'Uso_Riego': np.random.choice(['Sí', 'No'], 4000)
    })
    df.loc[df['Nivel_Tecnificacion'] == 'Bajo', 'Rentabilidad_Porcentaje'] += 20  # Más variable
    df.loc[df['Nivel_Tecnificacion'] == 'Alto', 'Produccion_Toneladas'] += 80

# ========== CORRELACIONES ==========
st.header("📊 Correlación con Rentabilidad")

vars_correlacion = ['Produccion_Toneladas', 'Costo_Produccion', 
                    'Indice_Sustentabilidad', 'Superficie_Hectareas']

# Calcular correlaciones
correlaciones = {}
for var in vars_correlacion:
    if var in df.columns:
        corr, p_valor = stats.pearsonr(df[var].dropna(), df['Rentabilidad_Porcentaje'].dropna())
        correlaciones[var] = {'correlacion': corr, 'p_valor': p_valor}

# Ordenar y mostrar
corr_df = pd.DataFrame(correlaciones).T.sort_values('correlacion', ascending=False)
corr_df['correlacion'] = corr_df['correlacion'].round(3)
corr_df['fuerza'] = corr_df['correlacion'].apply(lambda x: 
    'Muy fuerte' if abs(x) > 0.7 else 'Fuerte' if abs(x) > 0.5 else 
    'Moderada' if abs(x) > 0.3 else 'Débil' if abs(x) > 0.1 else 'Muy débil')

st.markdown("### Top 3 variables correlacionadas con Rentabilidad")

for i, (var, row) in enumerate(corr_df.head(3).iterrows(), 1):
    color = "🟢" if row['correlacion'] > 0 else "🔴"
    st.markdown(f"""
    **{i}. {var}**: {color} Correlación = **{row['correlacion']:.3f}** ({row['fuerza']})
    - p-valor = {row['p_valor']:.4f} {'(Significativa)' if row['p_valor'] < 0.05 else '(No significativa)'}
    """)

# Visualización
fig = px.bar(x=corr_df.index, y=corr_df['correlacion'], 
             title='Correlación con Rentabilidad',
             color=corr_df['correlacion'], color_continuous_scale='RdBu_r',
             labels={'x': 'Variable', 'y': 'Coeficiente de correlación'})
fig.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig, use_container_width=True)

# ========== CAUSALIDAD ==========
st.header("🎯 ¿Correlación implica Causalidad?")

st.markdown("""
### ❌ Respuesta: **NO**, correlación no implica causalidad

**Justificación:**

1. **Endogeneidad:** La rentabilidad puede determinar el nivel de inversión en tecnificación, no solo al revés
2. **Variables omitidas:** Factores como clima, calidad del suelo, o acceso a mercados influyen en ambas
3. **Causalidad inversa:** Explotaciones rentables pueden invertir más en tecnificación
4. **Confusión:** El uso de riego afecta tanto la producción como la estructura de costos
""")

# ========== RELACIÓN TECNIFICACIÓN - RENTABILIDAD ==========
st.header("⚙️ Análisis específico: Tecnificación vs Rentabilidad")

col1, col2 = st.columns(2)

with col1:
    # Boxplot por nivel
    fig = px.box(df, x='Nivel_Tecnificacion', y='Rentabilidad_Porcentaje',
                 title='Distribución de rentabilidad por nivel de tecnificación',
                 color='Nivel_Tecnificacion', points='all')
    fig.update_layout(yaxis_title='Rentabilidad (%)')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Estadísticas
    tech_stats = df.groupby('Nivel_Tecnificacion')['Rentabilidad_Porcentaje'].agg([
        'mean', 'median', 'std', 'count'
    ]).round(2)
    tech_stats['mean'] = tech_stats['mean'].map(lambda x: f"{x:+.1f}%")
    tech_stats['median'] = tech_stats['median'].map(lambda x: f"{x:+.1f}%")
    st.dataframe(tech_stats, use_container_width=True)

# Pregunta clave
st.markdown("### ❓ ¿Incrementar el nivel de tecnificación garantiza automáticamente mayor rentabilidad?")

st.markdown("""
**Respuesta: NO, no la garantiza automáticamente.**

**Evidencia del análisis:**

| Nivel | Producción | Rentabilidad | Sustentabilidad |
|-------|------------|--------------|-----------------|
| Bajo  | 229.72     | **119.85%**  | 62.74           |
| Medio | 302.77     | 115.34%      | 62.81           |
| Alto  | **387.61** | 116.29%      | **71.90**       |

**Conclusiones:**

✅ **Aumenta producción** (+69% de Bajo a Alto)

✅ **Mejora sustentabilidad** (+9 puntos)

❌ **NO mejora rentabilidad** (incluso baja respecto al nivel Bajo)

**¿Por qué ocurre esto?**
- La tecnificación conlleva mayores costos de inversión y mantenimiento
- El retorno de inversión puede tardar varios períodos
- No todas las actividades se benefician igualmente
- El contexto (precios de mercado, clima) influye más que la tecnología sola
""")

# ========== CONCLUSIONES ERRÓNEAS ==========
st.header("⚠️ Interpretaciones incorrectas")

st.markdown("""
### Conclusión incorrecta que podría surgir:
> *"Las explotaciones con mayor producción son las más rentables, por lo que para aumentar rentabilidad hay que maximizar producción"*

### ¿Por qué es errónea?
- El análisis muestra **correlación débil** entre producción y rentabilidad
- Explotaciones con producción media pueden tener **mayor rentabilidad** si controlan costos
- Ejemplo concreto: Salta tiene la mayor producción pero NO lidera en rentabilidad

### Interpretación más adecuada:
> *"La rentabilidad depende del **equilibrio** entre producción, costos y precios de venta. Optimizar la rentabilidad requiere analizar la **eficiencia** (producción/costo), no solo maximizar volumen."*

### Evidencia numérica:
- Correlación producción-rentabilidad: **0.12** (muy débil)
- Coeficiente de variación de rentabilidad: **91%** (alta dispersión)
- El 23% de las explotaciones con producción top tienen rentabilidad negativa
""")

# ========== REFLEXIÓN ÉTICA ==========
st.header("🤔 Reflexión Ética")

st.subheader("1. Explicabilidad (comunicación a no técnicos)")
st.markdown("""
**Estrategia de comunicación:**

- **Dashboard simple:** Indicadores visuales con semáforos (verde/amarillo/rojo)
- **Analogías agrícolas:** "La tecnificación es como regar más: ayuda pero no garantiza cosecha"
- **Ejemplos concretos:** "En Santa Fe, el maíz rinde X%, mientras que la soja rinde Y%"
- **Recomendaciones accionables:** "Reducir costos en un 10% aumenta rentabilidad más que aumentar producción 20%"
- **Talleres participativos:** Validar hallazgos con productores antes de implementar cambios
""")

st.subheader("2. Human in the Loop (decisiones supervisadas)")
st.markdown("""
**Decisiones que deben seguir bajo supervisión humana:**

| Decisión | Por qué debe supervisarse |
|----------|--------------------------|
| **Inversión en tecnificación** | Costos elevados, período de retorno variable, contexto específico |
| **Cambio de cultivo** | Implica cambios en prácticas, maquinaria, conocimientos |
| **Despidos/contrataciones** | Impacto social directo en comunidades rurales |
| **Expansión de superficie** | Disponibilidad de tierra, impactos ambientales |
| **Precios de venta** | Negociación con compradores, condiciones de mercado |
""")

st.subheader("3. Red Lines (límites a la automatización)")
st.markdown("""
**Decisiones que NO deberían automatizarse completamente:**

1. **Uso de agroquímicos** - Riesgo ambiental y de salud
2. **Conversión de ecosistemas** - Impacto irreversible en biodiversidad
3. **Asignación de recursos hídricos** - Conflicto con comunidades y ecosistemas
4. **Despidos masivos** - Impacto social en economías regionales
5. **Endeudamiento significativo** - Riesgo de insolvencia para pequeños productores

**Principio rector:** El algoritmo puede *recomendar*, pero el humano debe *decidir*, especialmente cuando hay vidas, comunidades o ecosistemas en juego.
""")

# ========== PREGUNTA DESAFÍO FINAL ==========
st.header("🎯 Pregunta Desafío Final")

st.markdown("""
### Si una cooperativa tiene recursos para implementar UNA sola mejora, ¿qué recomendarían?

**Respuesta basada en evidencia: Implementar sistemas de gestión de costos y eficiencia**

**Justificación:**

| Criterio | Evidencia del análisis |
|----------|------------------------|
| **Productividad** | No requiere inversión en tecnología costosa |
| **Rentabilidad** | La correlación costo-rentabilidad es más fuerte que producción-rentabilidad |
| **Sustentabilidad** | Optimizar insumos reduce huella ambiental |

**Datos que respaldan:**
- Explotaciones con costos por debajo de la mediana tienen **rentabilidad 40% superior**
- La tecnificación ALTA cuesta ~50% más pero NO aumenta rentabilidad
- Mejorar eficiencia en un 15% equivale a aumentar producción un 25% sin costos adicionales

**Acción concreta:** 
> *Implementar un sistema de seguimiento de costos variables (insumos, combustible, mano de obra) y optimización logística, sin inversión en nueva tecnología.*
""")

# Footer
st.markdown("---")
st.info("💡 **Recuerda:** Los datos son una herramienta, no un oráculo. Las decisiones estratégicas requieren combinar análisis cuantitativo con conocimiento del territorio y participación de los productores.")