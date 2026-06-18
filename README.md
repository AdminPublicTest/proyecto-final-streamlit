# 📊 App Analizadora de Datasets con Streamlit

**Proyecto Final Integrador — Especialización Python for Analytics**
**Diploma Business Analyst · DMC Institute**

---

## 👤 Autor

- **Nombre:** Chris Anthony Perea Pacaya  
- **Módulo:** Exploración y Visualización de Datos con Python  
- **Año:** 2025

---

## 🎯 Objetivo del proyecto

Construir una aplicación interactiva en **Streamlit** capaz de procesar cualquiera de los cuatro datasets propuestos, mostrando secciones de presentación, carga/procesamiento de datos y análisis visual mediante gráficos interactivos.

La herramienta está diseñada como un **producto real de análisis exploratorio de datos (EDA)**, adaptándose automáticamente a la estructura de cada dataset cargado.

---

## 📦 Datasets disponibles

| Dataset | Filas | Columnas | Contexto |
|---|---|---|---|
| `AI_Impact_on_Jobs_2030.csv` | 3,000 | 20 | Mercado laboral e impacto de IA |
| `sample_-_superstore.csv` | 10,194 | 21 | Ventas de tienda minorista |
| `synthetic_ecommerce_order_risk_dataset.csv` | 12,000 | 23 | Riesgo operativo en e-commerce |
| `Teen_Mental_Health_Dataset.csv` | 1,200 | 13 | Bienestar digital adolescente |

---

## 🗂️ Estructura del proyecto

```
proyecto_final_streamlit/
├── app.py                  ← Aplicación principal
├── requirements.txt        ← Dependencias
├── README.md               ← Documentación
└── data/
    ├── AI_Impact_on_Jobs_2030.csv
    ├── sample_-_superstore.csv
    ├── synthetic_ecommerce_order_risk_dataset.csv
    └── Teen_Mental_Health_Dataset.csv
```

---

## 🧩 Secciones de la app

### 🏠 1. Home
Presentación del proyecto, autor, descripción de los datasets, tecnologías utilizadas y nota de uso responsable.

### 📂 2. Carga y Perfil del Dataset
- Carga por `st.file_uploader()` o selección de dataset del proyecto
- Persistencia con `st.session_state`
- Vista previa, dimensiones, tipos de datos
- Métricas rápidas: filas, columnas, nulos, duplicados
- Selector de columnas con `multiselect`

### ⚙️ 3. Procesamiento de Datos
- Detección automática de tipos de variables
- Estandarización de nombres de columnas
- Conversión de fechas con `errors="coerce"`
- Análisis de nulos por columna con visualización
- Detección de duplicados
- Detección de outliers con regla IQR
- Filtros dinámicos por categoría y rango numérico

### 📊 4. Análisis Visual
Organizado en 6 tabs:
| Tab | Contenido |
|---|---|
| 📋 Resumen | Indicadores, tipos de datos, nulos, estadística descriptiva |
| 📊 Univariado | Histogramas, boxplots, conteos, proporciones |
| 🔗 Bivariado | Scatter, boxplot por categoría, barras agrupadas |
| 🕸️ Multivariado | Heatmap de correlación, barras apiladas, segmentación 3 variables |
| 📅 Temporal | Líneas de tiempo, barras por período (si hay columna fecha) |
| 💡 Insights | Hallazgos automáticos, conclusiones y recomendaciones |

---

## 🛠️ Tecnologías utilizadas

| Librería | Uso |
|---|---|
| `streamlit` | Framework principal de la app |
| `pandas` | Carga, transformación y análisis de datos |
| `numpy` | Operaciones numéricas y detección de outliers |
| `plotly` | Gráficos interactivos (histogramas, scatter, heatmap, barras) |
| `matplotlib` | Gráficos estáticos complementarios |
| `seaborn` | Boxplots y heatmaps con estilo académico |

---

## 🚀 Cómo ejecutar localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/proyecto_final_streamlit.git
cd proyecto_final_streamlit
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la app

```bash
streamlit run app.py
```

La app se abrirá en `http://localhost:8501`

---

## ☁️ Despliegue en Streamlit Cloud

1. Subir el proyecto a un repositorio público en **GitHub**
2. Ingresar a [share.streamlit.io](https://share.streamlit.io)
3. Conectar el repositorio y seleccionar `app.py` como archivo principal
4. Hacer clic en **Deploy**

> ⚠️ Asegurarse de que la carpeta `data/` con los cuatro datasets esté incluida en el repositorio.

---

## 📋 Características técnicas

- **`@st.cache_data`** para evitar recargas innecesarias del dataset
- **`st.session_state`** para persistencia de datos entre secciones
- **Validación de entradas** antes de ejecutar análisis
- **Detección automática** de tipos de variables (numéricas, categóricas, binarias, fechas)
- **Mensajes amigables** con `st.warning()`, `st.info()` y `st.error()`
- **Adaptación dinámica** al dataset cargado (sin asumir columnas fijas)

---

## ⚠️ Nota de uso responsable

Los resultados de esta aplicación son **exploratorios** y no reemplazan validación técnica o profesional especializada. Los análisis del dataset de salud mental adolescente no deben interpretarse como diagnóstico clínico.

---

## 🤖 Uso de IA como apoyo

Se utilizó inteligencia artificial (Claude - Anthropic) como apoyo para la generación de estructura de código, depuración de errores y documentación. Todo el código fue revisado, adaptado y validado con los cuatro datasets por el autor del proyecto.

---

*Especialización Python for Analytics · MSc. Carlos Carrillo Villavicencio*
