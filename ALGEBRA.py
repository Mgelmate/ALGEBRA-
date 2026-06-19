import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

# Configuración de la página y estética limpia
st.set_page_config(
    page_title="Optimización de Flota de Drones",
    page_icon="🛸",
    layout="centered"
)

st.title("🛸 Optimizador de Cobertura con Drones")
st.markdown("""
Esta aplicación calcula la combinación óptima de **Drones Livianos** y **Drones Pesados** para maximizar la cobertura total, respetando las restricciones de recursos disponibles.
""")

# --- BARRA LATERAL: ENTRADAS Y PARÁMETROS ---
st.sidebar.header("⚙️ Configuración de Recursos")

st.sidebar.subheader("Límites Disponibles (Restricciones)")
recurso_1 = st.sidebar.slider("Límite del Recurso 1 (ej. Batería/Presupuesto)", min_value=100, max_value=5000, value=1000, step=50)
recurso_2 = st.sidebar.slider("Límite del Recurso 2 (ej. Peso total/Personal)", min_value=100, max_value=5000, value=2400, step=50)

st.sidebar.subheader("Requisitos Mínimos")
min_livianos = st.sidebar.number_input("Cantidad mínima de Drones Livianos (x)", min_value=0, value=5, step=1)
min_pesados = st.sidebar.number_input("Cantidad mínima de Drones Pesados (y)", min_value=0, value=0, step=1)

st.sidebar.subheader("Configuración del Modelo")
tipo_variable = st.sidebar.toggle("Forzar resultados enteros (Drones completos)", value=False)


# --- PROCESAMIENTO DEL MODELO DE OPTIMIZACIÓN ---

# Coeficientes de la función objetivo (negativos para maximizar)
# Cobertura: Livianos = 4, Pesados = 10
c = [-4, -10]

# Matriz de restricciones de consumo
A = [
    [20, 50],   # Consumo del Recurso 1 por cada tipo de drone
    [50, 120]   # Consumo del Recurso 2 por cada tipo de drone
]

# Cotas de las restricciones
bu = [recurso_1, recurso_2]
bl = [-np.inf, -np.inf]

constraints = LinearConstraint(A, bl, bu)

# Cotas de las variables individuales
bounds = Bounds([min_livianos, min_pesados], [np.inf, np.inf])

# Definir la integralidad (0 = continuo, 1 = entero)
int_val = 1 if tipo_variable else 0
integrality = [int_val, int_val]

# Ejecución del optimizador
res = milp(
    c=c,
    constraints=constraints,
    bounds=bounds,
    integrality=integrality
)

# --- VISTA PRINCIPAL: RESULTADOS ---

st.subheader("📊 Resultados de la Optimización")

if res.success:
    st.success(f"¡Solución óptima encontrada de manera exitosa! ({res.message})")
    
    # Grid de métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Cobertura Máxima", 
            value=f"{int(-res.fun) if tipo_variable else round(-res.fun, 2)}"
        )
    with col2:
        st.metric(
            label="Drones Livianos", 
            value=f"{int(res.x[0]) if tipo_variable else round(res.x[0], 2)}"
        )
    with col3:
        st.metric(
            label="Drones Pesados", 
            value=f"{int(res.x[1]) if tipo_variable else round(res.x[1], 2)}"
        )

    # Bloque de desglose del uso de recursos
    with st.expander("🔍 Ver análisis de consumo de recursos"):
        uso_r1 = A[0][0] * res.x[0] + A[0][1] * res.x[1]
        uso_r2 = A[1][0] * res.x[0] + A[1][1] * res.x[1]
        
        st.markdown(f"**Uso del Recurso 1:** {round(uso_r1, 1)} de {recurso_1} ({round((uso_r1/recurso_1)*100, 1)}%)")
        st.progress(min(uso_r1 / recurso_1, 1.0))
        
        st.markdown(f"**Uso del Recurso 2:** {round(uso_r2, 1)} de {recurso_2} ({round((uso_r2/recurso_2)*100, 1)}%)")
        st.progress(min(uso_r2 / recurso_2, 1.0))

else:
    st.error("❌ No se pudo encontrar una solución viable con las restricciones actuales.")
    st.info("Sugerencia: Intenta disminuir la cantidad mínima exigida de drones o aumenta los límites de recursos disponibles.")
