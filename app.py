"""
App Analizadora de Datasets con Streamlit
Proyecto Final Integrador – Especialización Python for Analytics
Autor: Chris Anthony Perea Pacaya
Año: 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ─────────────────────────────────────────────
# Configuración general de la app
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DataViz Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# FUNCIONES UTILITARIAS
# ─────────────────────────────────────────────

@st.cache_data
def cargar_csv(file) -> pd.DataFrame:
    """Carga un CSV desde file_uploader con detección automática de separador."""
    try:
        df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(file, encoding="latin-1", on_bad_lines="skip")
    return df


@st.cache_data
def cargar_csv_path(path: str) -> pd.DataFrame:
    """Carga un CSV desde ruta local."""
    try:
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")
    return df


def estandarizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina espacios y caracteres especiales de los nombres de columnas."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.replace(r"[/\\\s]+", "_", regex=True)
        .str.replace(r"[^A-Za-z0-9_]", "", regex=True)
    )
    return df


def detectar_fechas(df: pd.DataFrame) -> list:
    """Detecta columnas que puedan convertirse a datetime."""
    candidatas = []
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().head(50)
        convertidas = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
        if convertidas.notna().mean() > 0.7:
            candidatas.append(col)
    return candidatas


def convertir_fechas(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Convierte columnas detectadas como fecha."""
    df = df.copy()
    for col in cols:
        df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
    return df


def clasificar_variables(df: pd.DataFrame):
    """Retorna listas de columnas numéricas, categóricas, binarias y de fecha."""
    numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    fechas = df.select_dtypes(include=["datetime64"]).columns.tolist()
    binarias = [c for c in numericas if df[c].nunique() == 2]
    numericas_puras = [c for c in numericas if c not in binarias]
    categoricas = df.select_dtypes(include="object").columns.tolist()
    return numericas_puras, categoricas, binarias, fechas


def resumen_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna tabla de nulos por columna."""
    nulos = df.isnull().sum()
    pct = (nulos / len(df) * 100).round(2)
    return pd.DataFrame({"Columna": df.columns, "Nulos": nulos.values, "% Nulos": pct.values})


def detectar_outliers_iqr(df: pd.DataFrame, col: str) -> pd.Series:
    """Retorna máscara booleana de outliers con regla IQR."""
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    return (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)


# ─────────────────────────────────────────────
# SIDEBAR — menú y carga global
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bar-chart.png", width=60)
    st.title("DataViz Analyzer")
    st.markdown("---")

    seccion = st.selectbox(
        "📌 Navegar a",
        ["🏠 Home", "📂 Carga y Perfil", "⚙️ Procesamiento", "📊 Análisis Visual"],
    )

    st.markdown("---")
    st.markdown("### 📁 Fuente de datos")

    fuente = st.radio("Seleccionar fuente:", ["Cargar archivo CSV", "Usar dataset del proyecto"])

    df_raw = None

    if fuente == "Cargar archivo CSV":
        uploaded = st.file_uploader("Sube tu archivo .csv", type=["csv"])
        if uploaded:
            df_raw = cargar_csv(uploaded)
            st.session_state["df_raw"] = df_raw
            st.session_state["nombre_dataset"] = uploaded.name
            st.success(f"✅ {uploaded.name} cargado")
    else:
        opciones_ds = {
            "AI Impact on Jobs 2030": "data/AI_Impact_on_Jobs_2030.csv",
            "Superstore Sales": "data/sample_-_superstore.csv",
            "E-commerce Order Risk": "data/synthetic_ecommerce_order_risk_dataset.csv",
            "Teen Mental Health": "data/Teen_Mental_Health_Dataset.csv",
        }
        ds_elegido = st.selectbox("Dataset del proyecto:", list(opciones_ds.keys()))
        if st.button("📥 Cargar dataset"):
            ruta = opciones_ds[ds_elegido]
            df_raw = cargar_csv_path(ruta)
            st.session_state["df_raw"] = df_raw
            st.session_state["nombre_dataset"] = ds_elegido
            st.success(f"✅ {ds_elegido} cargado")

    # Recuperar de session_state si ya fue cargado
    if df_raw is None and "df_raw" in st.session_state:
        df_raw = st.session_state["df_raw"]

    if df_raw is not None:
        st.markdown("---")
        st.markdown(f"**Dataset activo:** `{st.session_state.get('nombre_dataset','—')}`")
        st.markdown(f"**Filas:** {df_raw.shape[0]:,} | **Columnas:** {df_raw.shape[1]}")

    st.markdown("---")
    st.caption("Especialización Python for Analytics\n\nProyecto Final Integrador · 2025")


# ═══════════════════════════════════════════════════════════
# SECCIÓN 1 — HOME
# ═══════════════════════════════════════════════════════════
if seccion == "🏠 Home":
    st.title("📊 App Analizadora de Datasets")
    st.markdown("#### Proyecto Final Integrador — Exploración y Visualización de Datos con Python")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🎯 Objetivo del proyecto
        Construir una aplicación interactiva en **Streamlit** capaz de procesar cualquiera de los
        cuatro datasets propuestos, mostrando secciones de presentación, carga/procesamiento de datos
        y análisis visual mediante gráficos interactivos.

        La herramienta está diseñada como un **producto real de análisis exploratorio de datos (EDA)**,
        adaptándose automáticamente a la estructura de cada dataset cargado.
        """)

        st.markdown("""
        ### 👤 Autor
        | | |
        |---|---|
        | **Nombre** | Chris Anthony Perea Pacaya |
        | **Curso** | Exploración y Visualización de Datos con Python |
        | **Institución** | DMC Institute — Diploma Business Analyst |
        | **Año** | 2025 |
        """)

    with col2:
        st.markdown("### 🛠️ Tecnologías")
        tecnologias = {
            "Python": "🐍", "Pandas": "🐼", "NumPy": "🔢",
            "Streamlit": "⚡", "Plotly": "📈", "Matplotlib": "🎨",
            "Seaborn": "🌊", "GitHub": "🐙"
        }
        for tech, icon in tecnologias.items():
            st.markdown(f"{icon} **{tech}**")

    st.markdown("---")
    st.markdown("### 📦 Datasets disponibles")

    datasets_info = [
        {
            "nombre": "🤖 AI Impact on Jobs 2030",
            "filas": "3,000", "columnas": "20",
            "descripcion": "Mercado laboral e impacto de la IA en empleos, salarios, habilidades y demanda futura.",
            "preguntas": "Riesgo de reemplazo, demanda futura, salarios, nivel de automatización.",
            "color": "#1f77b4"
        },
        {
            "nombre": "🛒 Superstore Sales",
            "filas": "10,194", "columnas": "21",
            "descripcion": "Ventas de una tienda: pedidos, clientes, regiones, categorías y utilidad.",
            "preguntas": "Rentabilidad, descuentos, productos top, evolución temporal de ventas.",
            "color": "#2ca02c"
        },
        {
            "nombre": "🌐 E-commerce Order Risk",
            "filas": "12,000", "columnas": "23",
            "descripcion": "Pedidos de e-commerce con variables de fraude, devolución, entrega y riesgo operativo.",
            "preguntas": "Factores de riesgo, fraude, método de pago, entregas tardías.",
            "color": "#ff7f0e"
        },
        {
            "nombre": "🧠 Teen Mental Health",
            "filas": "1,200", "columnas": "13",
            "descripcion": "Hábitos digitales, sueño, actividad física e indicadores de bienestar en adolescentes.",
            "preguntas": "Uso de redes, sueño, estrés, ansiedad, interacción social.",
            "color": "#9467bd"
        },
    ]

    cols = st.columns(2)
    for i, ds in enumerate(datasets_info):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="border-left: 4px solid {ds['color']}; padding: 12px 16px;
                        background-color: #f8f9fa; border-radius: 4px; margin-bottom: 12px;">
                <b>{ds['nombre']}</b><br>
                <small>📏 {ds['filas']} filas · {ds['columnas']} columnas</small><br><br>
                {ds['descripcion']}<br><br>
                <small>🔍 <i>{ds['preguntas']}</i></small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.info(
        "⚠️ **Nota de uso responsable:** Los resultados de esta aplicación son exploratorios "
        "y no reemplazan validación técnica o profesional especializada. "
        "Los análisis del dataset de salud mental no deben interpretarse como diagnóstico clínico."
    )


# ═══════════════════════════════════════════════════════════
# SECCIÓN 2 — CARGA Y PERFIL
# ═══════════════════════════════════════════════════════════
elif seccion == "📂 Carga y Perfil":
    st.title("📂 Carga y Perfil del Dataset")
    st.markdown("---")

    if df_raw is None:
        st.warning("⚠️ No hay dataset cargado. Usa el panel izquierdo para cargar un archivo o seleccionar un dataset.")
        st.stop()

    # Estandarizar columnas
    df = estandarizar_columnas(df_raw)
    cols_fecha = detectar_fechas(df)
    df = convertir_fechas(df, cols_fecha)
    num_cols, cat_cols, bin_cols, fecha_cols = clasificar_variables(df)

    # ── Métricas rápidas ──
    st.markdown("### 📐 Métricas rápidas")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Filas", f"{df.shape[0]:,}")
    m2.metric("Columnas", f"{df.shape[1]}")
    m3.metric("Numéricas", len(num_cols))
    m4.metric("Categóricas", len(cat_cols))
    m5.metric("Nulos", f"{df.isnull().sum().sum():,}")
    m6.metric("Duplicados", f"{df.duplicated().sum():,}")

    st.markdown("---")

    # ── Vista previa ──
    st.markdown("### 👀 Vista previa de los datos")
    n_filas = st.slider("Número de filas a mostrar:", 5, 50, 10)
    st.dataframe(df.head(n_filas), use_container_width=True)

    st.markdown("---")

    # ── Tipos de datos ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏷️ Tipos de variables")
        tipos_df = pd.DataFrame({
            "Columna": df.columns,
            "Tipo pandas": df.dtypes.astype(str).values,
            "Clasificación": [
                "📅 Fecha" if c in fecha_cols
                else "🔢 Numérica" if c in num_cols
                else "🔘 Binaria" if c in bin_cols
                else "🔤 Categórica"
                for c in df.columns
            ]
        })
        st.dataframe(tipos_df, use_container_width=True, height=350)

    with col_b:
        st.markdown("### 📊 Distribución de tipos")
        tipo_counts = {
            "Numéricas": len(num_cols),
            "Categóricas": len(cat_cols),
            "Binarias": len(bin_cols),
            "Fechas": len(fecha_cols)
        }
        fig_tipos = px.pie(
            values=list(tipo_counts.values()),
            names=list(tipo_counts.keys()),
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig_tipos.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_tipos, use_container_width=True)

    st.markdown("---")

    # ── Estadística descriptiva ──
    st.markdown("### 📈 Estadística descriptiva")
    if st.checkbox("Mostrar estadística descriptiva completa"):
        if num_cols:
            st.dataframe(df[num_cols].describe().round(3), use_container_width=True)
        else:
            st.info("No hay variables numéricas puras en este dataset.")

    # ── Selector de columnas ──
    st.markdown("---")
    st.markdown("### 🎛️ Explorar columnas seleccionadas")
    cols_elegidas = st.multiselect(
        "Selecciona columnas para revisar:",
        options=df.columns.tolist(),
        default=df.columns[:5].tolist()
    )
    if cols_elegidas:
        st.dataframe(df[cols_elegidas].head(20), use_container_width=True)

    # Guardar df procesado en session_state
    st.session_state["df_procesado"] = df
    st.session_state["num_cols"] = num_cols
    st.session_state["cat_cols"] = cat_cols
    st.session_state["bin_cols"] = bin_cols
    st.session_state["fecha_cols"] = fecha_cols


# ═══════════════════════════════════════════════════════════
# SECCIÓN 3 — PROCESAMIENTO
# ═══════════════════════════════════════════════════════════
elif seccion == "⚙️ Procesamiento":
    st.title("⚙️ Procesamiento de Datos")
    st.markdown("---")

    if df_raw is None:
        st.warning("⚠️ No hay dataset cargado. Usa el panel izquierdo.")
        st.stop()

    # Recuperar o reprocesar
    if "df_procesado" in st.session_state:
        df = st.session_state["df_procesado"]
        num_cols = st.session_state["num_cols"]
        cat_cols = st.session_state["cat_cols"]
        bin_cols = st.session_state["bin_cols"]
        fecha_cols = st.session_state["fecha_cols"]
    else:
        df = estandarizar_columnas(df_raw)
        cols_fecha = detectar_fechas(df)
        df = convertir_fechas(df, cols_fecha)
        num_cols, cat_cols, bin_cols, fecha_cols = clasificar_variables(df)
        st.session_state["df_procesado"] = df
        st.session_state["num_cols"] = num_cols
        st.session_state["cat_cols"] = cat_cols
        st.session_state["bin_cols"] = bin_cols
        st.session_state["fecha_cols"] = fecha_cols

    # ── Valores nulos ──
    st.markdown("### 🔍 Análisis de valores nulos")
    df_nulos = resumen_nulos(df)
    df_nulos_filtrado = df_nulos[df_nulos["Nulos"] > 0]

    col1, col2 = st.columns(2)
    with col1:
        if df_nulos_filtrado.empty:
            st.success("✅ No hay valores nulos en el dataset.")
        else:
            st.dataframe(df_nulos_filtrado, use_container_width=True)

    with col2:
        if not df_nulos_filtrado.empty:
            fig_nulos = px.bar(
                df_nulos_filtrado,
                x="Columna", y="% Nulos",
                title="% de Nulos por Columna",
                color="% Nulos",
                color_continuous_scale="Reds"
            )
            fig_nulos.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_nulos, use_container_width=True)
        else:
            # Heatmap de nulos con seaborn
            fig_h, ax = plt.subplots(figsize=(6, 3))
            sns.heatmap(df.isnull(), cbar=False, ax=ax, cmap="YlOrRd")
            ax.set_title("Mapa de nulos")
            st.pyplot(fig_h)
            plt.close()

    st.markdown("---")

    # ── Duplicados ──
    st.markdown("### 🔁 Duplicados")
    n_dup = df.duplicated().sum()
    if n_dup == 0:
        st.success("✅ No se encontraron filas duplicadas.")
    else:
        st.warning(f"⚠️ Se detectaron **{n_dup}** filas duplicadas ({n_dup/len(df)*100:.2f}% del total).")
        if st.checkbox("Mostrar filas duplicadas"):
            st.dataframe(df[df.duplicated(keep=False)].head(20), use_container_width=True)

    st.markdown("---")

    # ── Outliers ──
    st.markdown("### 📦 Detección de Outliers (regla IQR)")
    if not num_cols:
        st.info("No hay variables numéricas para analizar outliers.")
    else:
        col_outlier = st.selectbox("Selecciona variable numérica:", num_cols)
        mask_outlier = detectar_outliers_iqr(df, col_outlier)
        n_out = mask_outlier.sum()

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Outliers detectados", f"{n_out:,}")
            st.metric("% del total", f"{n_out/len(df)*100:.2f}%")
            Q1 = df[col_outlier].quantile(0.25)
            Q3 = df[col_outlier].quantile(0.75)
            IQR = Q3 - Q1
            st.markdown(f"""
            - **Q1:** {Q1:.3f}
            - **Q3:** {Q3:.3f}
            - **IQR:** {IQR:.3f}
            - **Límite inferior:** {Q1 - 1.5*IQR:.3f}
            - **Límite superior:** {Q3 + 1.5*IQR:.3f}
            """)

        with col_b:
            fig_box = px.box(
                df, y=col_outlier,
                title=f"Boxplot: {col_outlier}",
                points="outliers",
                color_discrete_sequence=["#636EFA"]
            )
            st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # ── Filtros dinámicos ──
    st.markdown("### 🎛️ Filtros dinámicos")
    df_filtrado = df.copy()

    if cat_cols:
        col_cat_filtro = st.selectbox("Filtrar por variable categórica:", ["(ninguna)"] + cat_cols)
        if col_cat_filtro != "(ninguna)":
            opciones_cat = df[col_cat_filtro].dropna().unique().tolist()
            seleccion_cat = st.multiselect(
                f"Valores de {col_cat_filtro}:",
                options=opciones_cat,
                default=opciones_cat[:3] if len(opciones_cat) >= 3 else opciones_cat
            )
            if seleccion_cat:
                df_filtrado = df_filtrado[df_filtrado[col_cat_filtro].isin(seleccion_cat)]

    if num_cols:
        col_num_filtro = st.selectbox("Filtrar por rango numérico:", ["(ninguna)"] + num_cols)
        if col_num_filtro != "(ninguna)":
            min_v = float(df[col_num_filtro].min())
            max_v = float(df[col_num_filtro].max())
            rango = st.slider(
                f"Rango de {col_num_filtro}:",
                min_value=min_v, max_value=max_v,
                value=(min_v, max_v)
            )
            df_filtrado = df_filtrado[
                df_filtrado[col_num_filtro].between(rango[0], rango[1])
            ]

    st.info(f"📋 Registros tras filtros: **{len(df_filtrado):,}** de {len(df):,}")
    if st.checkbox("Ver datos filtrados"):
        st.dataframe(df_filtrado.head(30), use_container_width=True)

    # Guardar dataset filtrado
    st.session_state["df_filtrado"] = df_filtrado


# ═══════════════════════════════════════════════════════════
# SECCIÓN 4 — ANÁLISIS VISUAL
# ═══════════════════════════════════════════════════════════
elif seccion == "📊 Análisis Visual":
    st.title("📊 Análisis Visual")
    st.markdown("---")

    if df_raw is None:
        st.warning("⚠️ No hay dataset cargado. Usa el panel izquierdo.")
        st.stop()

    # Recuperar datos
    if "df_procesado" in st.session_state:
        df = st.session_state["df_procesado"]
        num_cols = st.session_state["num_cols"]
        cat_cols = st.session_state["cat_cols"]
        bin_cols = st.session_state["bin_cols"]
        fecha_cols = st.session_state["fecha_cols"]
    else:
        df = estandarizar_columnas(df_raw)
        cols_fecha = detectar_fechas(df)
        df = convertir_fechas(df, cols_fecha)
        num_cols, cat_cols, bin_cols, fecha_cols = clasificar_variables(df)
        st.session_state["df_procesado"] = df
        st.session_state["num_cols"] = num_cols
        st.session_state["cat_cols"] = cat_cols
        st.session_state["bin_cols"] = bin_cols
        st.session_state["fecha_cols"] = fecha_cols

    # Usar filtrado si existe
    df_vis = st.session_state.get("df_filtrado", df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Resumen",
        "📊 Univariado",
        "🔗 Bivariado",
        "🕸️ Multivariado",
        "📅 Temporal",
        "💡 Insights"
    ])

    # ── TAB 1: RESUMEN ──────────────────────────────────────
    with tab1:
        st.subheader("📋 Resumen del Dataset")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Filas", f"{df_vis.shape[0]:,}")
        c2.metric("Columnas", f"{df_vis.shape[1]}")
        c3.metric("Nulos totales", f"{df_vis.isnull().sum().sum():,}")
        c4.metric("Duplicados", f"{df_vis.duplicated().sum():,}")

        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Tipos de datos**")
            tipos_df = pd.DataFrame({
                "Columna": df_vis.columns,
                "Tipo": df_vis.dtypes.astype(str).values
            })
            st.dataframe(tipos_df, use_container_width=True, height=300)

        with col_b:
            if num_cols:
                st.markdown("**Estadística descriptiva**")
                st.dataframe(df_vis[num_cols].describe().round(3), use_container_width=True, height=300)

        st.markdown("---")
        st.markdown("**Nulos por columna**")
        df_nulos = resumen_nulos(df_vis)
        df_nulos_plot = df_nulos[df_nulos["Nulos"] > 0]
        if df_nulos_plot.empty:
            st.success("✅ No hay valores nulos.")
        else:
            fig_n = px.bar(df_nulos_plot, x="Columna", y="% Nulos",
                           color="% Nulos", color_continuous_scale="Oranges",
                           title="Porcentaje de nulos por columna")
            st.plotly_chart(fig_n, use_container_width=True)

        if st.checkbox("📄 Mostrar datos crudos"):
            st.dataframe(df_vis.head(50), use_container_width=True)

    # ── TAB 2: UNIVARIADO ────────────────────────────────────
    with tab2:
        st.subheader("📊 Análisis Univariado")

        sub_tab_num, sub_tab_cat = st.tabs(["Numéricas", "Categóricas"])

        with sub_tab_num:
            if not num_cols:
                st.info("No hay variables numéricas en este dataset.")
            else:
                var_num = st.selectbox("Variable numérica:", num_cols, key="univ_num")
                col1, col2 = st.columns(2)

                with col1:
                    # Histograma con Plotly
                    fig_hist = px.histogram(
                        df_vis, x=var_num, nbins=30,
                        title=f"Distribución de {var_num}",
                        color_discrete_sequence=["#636EFA"],
                        marginal="box"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                    st.caption("El histograma muestra la distribución de frecuencias de la variable seleccionada. La caja superpuesta indica la mediana y percentiles.")

                with col2:
                    # Boxplot con Seaborn/Matplotlib
                    fig_s, ax = plt.subplots(figsize=(5, 4))
                    sns.boxplot(y=df_vis[var_num].dropna(), ax=ax,
                                color="#48cae4", flierprops=dict(marker='o', color='red', alpha=0.5))
                    ax.set_title(f"Boxplot: {var_num}", fontsize=12)
                    ax.set_ylabel(var_num)
                    st.pyplot(fig_s)
                    plt.close()
                    st.caption("El boxplot (Seaborn) permite identificar la mediana, rango intercuartílico y valores atípicos.")

        with sub_tab_cat:
            if not cat_cols:
                st.info("No hay variables categóricas en este dataset.")
            else:
                var_cat = st.selectbox("Variable categórica:", cat_cols, key="univ_cat")
                top_n = st.slider("Top N categorías:", 5, 30, 10, key="top_n_cat")

                conteo = df_vis[var_cat].value_counts().head(top_n).reset_index()
                conteo.columns = [var_cat, "Conteo"]
                conteo["Proporción (%)"] = (conteo["Conteo"] / len(df_vis) * 100).round(2)

                col1, col2 = st.columns(2)
                with col1:
                    fig_bar = px.bar(
                        conteo, x=var_cat, y="Conteo",
                        title=f"Conteo por {var_cat} (Top {top_n})",
                        color="Conteo", color_continuous_scale="Blues",
                        text="Conteo"
                    )
                    fig_bar.update_layout(xaxis_tickangle=-40)
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.caption(f"Las {top_n} categorías más frecuentes en {var_cat}.")

                with col2:
                    fig_pie = px.pie(
                        conteo, names=var_cat, values="Proporción (%)",
                        title=f"Proporción por {var_cat}",
                        hole=0.3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.caption("Distribución porcentual entre las categorías.")

    # ── TAB 3: BIVARIADO ──────────────────────────────────────
    with tab3:
        st.subheader("🔗 Análisis Bivariado")

        tipo_biv = st.selectbox(
            "Tipo de análisis:",
            ["Numérica vs Numérica (Scatter)", "Numérica vs Categórica (Boxplot)", "Categórica vs Categórica (Barras agrupadas)"],
            key="tipo_biv"
        )

        if tipo_biv == "Numérica vs Numérica (Scatter)":
            if len(num_cols) < 2:
                st.info("Se necesitan al menos 2 variables numéricas.")
            else:
                c1, c2, c3 = st.columns(3)
                var_x = c1.selectbox("Eje X:", num_cols, key="biv_x")
                var_y = c2.selectbox("Eje Y:", num_cols, index=min(1, len(num_cols)-1), key="biv_y")
                color_var = c3.selectbox("Color (opcional):", ["(ninguna)"] + cat_cols, key="biv_color")

                color_arg = None if color_var == "(ninguna)" else color_var
                fig_sc = px.scatter(
                    df_vis, x=var_x, y=var_y, color=color_arg,
                    title=f"{var_x} vs {var_y}",
                    opacity=0.6, trendline="ols" if color_arg is None else None
                )
                st.plotly_chart(fig_sc, use_container_width=True)
                st.caption(f"Relación entre {var_x} y {var_y}. La línea de tendencia indica la dirección de la correlación.")

        elif tipo_biv == "Numérica vs Categórica (Boxplot)":
            if not num_cols or not cat_cols:
                st.info("Se necesita al menos una variable numérica y una categórica.")
            else:
                c1, c2 = st.columns(2)
                var_num_b = c1.selectbox("Variable numérica:", num_cols, key="biv_num")
                var_cat_b = c2.selectbox("Variable categórica:", cat_cols, key="biv_cat")
                top_cats = st.slider("Top N categorías:", 3, 20, 8, key="biv_top")

                cats_top = df_vis[var_cat_b].value_counts().head(top_cats).index.tolist()
                df_biv = df_vis[df_vis[var_cat_b].isin(cats_top)]

                fig_biv = px.box(
                    df_biv, x=var_cat_b, y=var_num_b,
                    title=f"{var_num_b} por {var_cat_b}",
                    color=var_cat_b,
                    points="outliers"
                )
                fig_biv.update_layout(showlegend=False, xaxis_tickangle=-40)
                st.plotly_chart(fig_biv, use_container_width=True)
                st.caption(f"Comparación de {var_num_b} entre las categorías de {var_cat_b}.")

        else:
            if len(cat_cols) < 2:
                st.info("Se necesitan al menos 2 variables categóricas.")
            else:
                c1, c2 = st.columns(2)
                var_c1 = c1.selectbox("Variable categórica 1:", cat_cols, key="biv_c1")
                var_c2 = c2.selectbox("Variable categórica 2:", cat_cols, index=min(1, len(cat_cols)-1), key="biv_c2")
                top_c = st.slider("Top N (var 1):", 3, 15, 5, key="biv_top_c")

                cats_top = df_vis[var_c1].value_counts().head(top_c).index.tolist()
                df_cc = df_vis[df_vis[var_c1].isin(cats_top)]
                tabla = df_cc.groupby([var_c1, var_c2]).size().reset_index(name="Conteo")

                fig_bar_g = px.bar(
                    tabla, x=var_c1, y="Conteo", color=var_c2,
                    title=f"{var_c1} vs {var_c2}",
                    barmode="group"
                )
                fig_bar_g.update_layout(xaxis_tickangle=-40)
                st.plotly_chart(fig_bar_g, use_container_width=True)
                st.caption(f"Distribución de {var_c2} dentro de cada categoría de {var_c1}.")

    # ── TAB 4: MULTIVARIADO ───────────────────────────────────
    with tab4:
        st.subheader("🕸️ Análisis Multivariado")

        sub1, sub2, sub3 = st.tabs(["Correlación / Heatmap", "Barras apiladas", "Segmentación 3 variables"])

        with sub1:
            if len(num_cols) < 2:
                st.info("Se necesitan al menos 2 variables numéricas para calcular correlación.")
            else:
                cols_corr = st.multiselect(
                    "Variables para correlación:",
                    options=num_cols,
                    default=num_cols[:min(8, len(num_cols))]
                )
                if len(cols_corr) >= 2:
                    corr_matrix = df_vis[cols_corr].corr().round(3)

                    # Plotly heatmap interactivo
                    fig_heat = px.imshow(
                        corr_matrix,
                        text_auto=True,
                        color_continuous_scale="RdBu_r",
                        title="Mapa de correlación (Pearson)",
                        aspect="auto",
                        zmin=-1, zmax=1
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)

                    # Seaborn heatmap complementario
                    if st.checkbox("Ver heatmap Seaborn"):
                        fig_s2, ax2 = plt.subplots(figsize=(8, 6))
                        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm",
                                    center=0, ax=ax2, linewidths=0.5)
                        ax2.set_title("Correlación (Seaborn)", fontsize=12)
                        plt.tight_layout()
                        st.pyplot(fig_s2)
                        plt.close()
                    st.caption("Valores cercanos a 1 o -1 indican alta correlación positiva o negativa respectivamente. Valores cercanos a 0 sugieren independencia.")

        with sub2:
            if not cat_cols or not num_cols:
                st.info("Se necesita al menos una variable categórica y una numérica.")
            else:
                c1, c2, c3 = st.columns(3)
                cat_apil = c1.selectbox("Categoría (eje X):", cat_cols, key="apil_x")
                cat_color = c2.selectbox("Categoría (color):", cat_cols, index=min(1, len(cat_cols)-1), key="apil_color")
                num_apil = c3.selectbox("Variable numérica (valor):", num_cols, key="apil_val")
                top_apil = st.slider("Top N (eje X):", 3, 15, 6, key="apil_top")

                cats_top_a = df_vis[cat_apil].value_counts().head(top_apil).index.tolist()
                df_apil = df_vis[df_vis[cat_apil].isin(cats_top_a)]
                tabla_apil = df_apil.groupby([cat_apil, cat_color])[num_apil].mean().reset_index()

                fig_apil = px.bar(
                    tabla_apil, x=cat_apil, y=num_apil, color=cat_color,
                    title=f"Media de {num_apil} por {cat_apil} y {cat_color}",
                    barmode="stack"
                )
                fig_apil.update_layout(xaxis_tickangle=-40)
                st.plotly_chart(fig_apil, use_container_width=True)
                st.caption(f"Barras apiladas que muestran la media de {num_apil} desglosada por {cat_color}.")

        with sub3:
            if len(num_cols) < 2 or not cat_cols:
                st.info("Se necesitan al menos 2 numéricas y 1 categórica.")
            else:
                c1, c2, c3, c4 = st.columns(4)
                v_x = c1.selectbox("Eje X:", num_cols, key="seg_x")
                v_y = c2.selectbox("Eje Y:", num_cols, index=min(1, len(num_cols)-1), key="seg_y")
                v_c = c3.selectbox("Color:", cat_cols, key="seg_c")
                v_s = c4.selectbox("Tamaño (opcional):", ["(ninguna)"] + num_cols, key="seg_s")

                size_arg = None if v_s == "(ninguna)" else v_s
                # Limpiar nulos en columnas usadas
                cols_usar = [v_x, v_y, v_c] + ([v_s] if size_arg else [])
                df_seg = df_vis[cols_usar].dropna()

                fig_seg = px.scatter(
                    df_seg, x=v_x, y=v_y, color=v_c, size=size_arg,
                    title=f"Segmentación: {v_x} vs {v_y} por {v_c}",
                    opacity=0.7
                )
                st.plotly_chart(fig_seg, use_container_width=True)
                st.caption(f"Visualización multivariada: {v_x}, {v_y} y {v_c} analizados simultáneamente.")

    # ── TAB 5: TEMPORAL ───────────────────────────────────────
    with tab5:
        st.subheader("📅 Análisis Temporal")

        if not fecha_cols:
            st.info(
                "ℹ️ No se detectaron columnas de fecha en este dataset. "
                "El análisis temporal no aplica para la fuente actual."
            )
        else:
            col_fecha = st.selectbox("Columna de fecha:", fecha_cols, key="temp_fecha")
            frecuencia = st.selectbox(
                "Agrupar por:",
                ["Día", "Semana", "Mes", "Trimestre", "Año"],
                index=2, key="temp_frec"
            )
            freq_map = {"Día": "D", "Semana": "W", "Mes": "ME", "Trimestre": "QE", "Año": "YE"}
            freq = freq_map[frecuencia]

            df_temp = df_vis.dropna(subset=[col_fecha]).copy()
            df_temp = df_temp.set_index(col_fecha).sort_index()

            if num_cols:
                var_temp = st.selectbox("Variable numérica a analizar:", num_cols, key="temp_num")
                agg_func = st.selectbox("Agregación:", ["Suma", "Media", "Conteo"], key="temp_agg")

                if agg_func == "Suma":
                    serie = df_temp[var_temp].resample(freq).sum()
                elif agg_func == "Media":
                    serie = df_temp[var_temp].resample(freq).mean()
                else:
                    serie = df_temp[var_temp].resample(freq).count()

                serie = serie.reset_index()
                serie.columns = [col_fecha, var_temp]
                serie = serie.dropna()

                fig_line = px.line(
                    serie, x=col_fecha, y=var_temp,
                    title=f"{agg_func} de {var_temp} por {frecuencia}",
                    markers=True,
                    color_discrete_sequence=["#EF553B"]
                )
                fig_line.update_layout(xaxis_title="Fecha", yaxis_title=f"{agg_func} de {var_temp}")
                st.plotly_chart(fig_line, use_container_width=True)
                st.caption(f"Evolución temporal de {var_temp} agregada por {frecuencia.lower()}.")

                # Barras por período
                fig_bar_t = px.bar(
                    serie, x=col_fecha, y=var_temp,
                    title=f"Barras: {agg_func} de {var_temp} por {frecuencia}",
                    color=var_temp, color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_bar_t, use_container_width=True)
                st.caption("Vista en barras para identificar períodos de mayor actividad.")

            else:
                # Solo conteo de registros por período
                conteo_temp = df_temp.resample(freq).size().reset_index()
                conteo_temp.columns = [col_fecha, "Registros"]

                fig_ct = px.line(
                    conteo_temp, x=col_fecha, y="Registros",
                    title=f"Número de registros por {frecuencia}",
                    markers=True
                )
                st.plotly_chart(fig_ct, use_container_width=True)

    # ── TAB 6: INSIGHTS ───────────────────────────────────────
    with tab6:
        st.subheader("💡 Insights y Hallazgos Clave")

        nombre_ds = st.session_state.get("nombre_dataset", "Dataset cargado")
        st.markdown(f"**Dataset analizado:** `{nombre_ds}`")
        st.markdown("---")

        # Insights automáticos generales
        insights = []

        # 1. Nulos
        total_nulos = df_vis.isnull().sum().sum()
        pct_nulos = total_nulos / (df_vis.shape[0] * df_vis.shape[1]) * 100
        if pct_nulos == 0:
            insights.append(("✅", "Completitud de datos", "El dataset no tiene valores nulos. Alta calidad de datos."))
        elif pct_nulos < 5:
            insights.append(("🟡", "Calidad aceptable", f"Solo el {pct_nulos:.2f}% de los valores son nulos. Impacto mínimo en el análisis."))
        else:
            insights.append(("🔴", "Advertencia de calidad", f"El {pct_nulos:.2f}% de los valores son nulos. Considerar estrategia de imputación."))

        # 2. Duplicados
        n_dup_v = df_vis.duplicated().sum()
        if n_dup_v > 0:
            insights.append(("⚠️", "Duplicados detectados", f"Se encontraron {n_dup_v:,} filas duplicadas. Revisar si corresponden a errores de carga."))
        else:
            insights.append(("✅", "Sin duplicados", "No se detectaron filas duplicadas en el dataset."))

        # 3. Variables numéricas — asimetría
        if num_cols:
            for col in num_cols[:3]:
                skew = df_vis[col].skew()
                if abs(skew) > 1:
                    dir_skew = "positiva (cola derecha)" if skew > 0 else "negativa (cola izquierda)"
                    insights.append(("📊", f"Asimetría en {col}", f"La variable presenta asimetría {dir_skew} (skewness={skew:.2f}). Considerar transformación logarítmica si se usará en modelos."))

        # 4. Outliers
        if num_cols:
            col_mayor_out = max(num_cols, key=lambda c: detectar_outliers_iqr(df_vis, c).sum())
            n_out_max = detectar_outliers_iqr(df_vis, col_mayor_out).sum()
            pct_out = n_out_max / len(df_vis) * 100
            insights.append(("📦", f"Outliers en {col_mayor_out}", f"Variable con mayor concentración de outliers: {pct_out:.2f}% ({n_out_max:,} registros). Verificar si son errores o valores extremos reales."))

        # 5. Variable categórica dominante
        if cat_cols:
            for cc in cat_cols[:2]:
                top_val = df_vis[cc].value_counts().index[0]
                top_pct = df_vis[cc].value_counts().iloc[0] / len(df_vis) * 100
                if top_pct > 50:
                    insights.append(("🔍", f"Dominancia en {cc}", f"La categoría '{top_val}' representa el {top_pct:.1f}% del total. Posible desbalance de clases."))

        # 6. Correlación alta
        if len(num_cols) >= 2:
            corr_m = df_vis[num_cols].corr().abs()
            np.fill_diagonal(corr_m.values, 0)
            max_corr = corr_m.max().max()
            if max_corr > 0.7:
                idx = corr_m.stack().idxmax()
                insights.append(("🔗", "Alta correlación detectada", f"Las variables '{idx[0]}' y '{idx[1]}' tienen correlación de {max_corr:.3f}. Pueden contener información redundante."))

        # Mostrar insights
        for emoji, titulo, texto in insights:
            with st.expander(f"{emoji} {titulo}"):
                st.markdown(texto)

        st.markdown("---")
        st.markdown("### 📌 Conclusiones generales")
        st.markdown(f"""
        - El dataset **{nombre_ds}** contiene **{df_vis.shape[0]:,} registros** y **{df_vis.shape[1]} variables**.
        - Se identificaron **{len(num_cols)} variables numéricas**, **{len(cat_cols)} categóricas**, 
          **{len(bin_cols)} binarias** y **{len(fecha_cols)} de fecha**.
        - La exploración visual permite identificar patrones de distribución, relaciones entre variables 
          y posibles anomalías que guiarán decisiones analíticas posteriores.
        - **Este análisis es exploratorio.** Los hallazgos deben validarse con conocimiento de dominio 
          antes de tomar decisiones basadas en ellos.
        """)

        st.info(
            "🔍 Para un análisis más profundo, combina los hallazgos del módulo de "
            "Procesamiento con las visualizaciones del módulo de Análisis Visual."
        )
