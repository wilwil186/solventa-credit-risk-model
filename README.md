# Solventa - Prueba Técnica Data Scientist Jr.

## Descripción

Este repositorio contiene la solución completa a la prueba técnica de Data Scientist Jr. para Solventa. El análisis se divide en dos partes:

1. **Desarrollo de Modelo Predictivo** - Construcción de un modelo para calificar clientes potenciales de un producto de alto riesgo.
2. **Evaluación de Modelos de Proveedores** - Análisis comparativo de dos proveedores (AB y XY) que proponen modelos de scoring crediticio.

## Estructura del Proyecto

```
solventa-credit-risk-model/
├── src/
│   ├── 01_eda_preparacion_datos.ipynb      # EDA y preparación de datos
│   ├── 02_modelo_predictivo_interno.ipynb  # Parte 1: Modelo predictivo
│   ├── 03_evaluacion_proveedores.ipynb      # Parte 2: Evaluación de proveedores
│   ├── model_building.py                     # Script: modelo predictivo (genera 01/02)
│   ├── competitor_analysis.py               # Script: evaluación proveedores (genera 03)
│   ├── 04_generar_reporte_pdf.py            # Generador de reporte PDF
│   ├── 05_generar_presentacion.py           # Generador de presentación ejecutiva
│   └── 06_convertir_notebooks.py           # Conversor .py a .ipynb (obsoleto)
├── output/
│   ├── analisis_completo.pdf          # Documento PDF con análisis completo
│   ├── presentacion_ejecutiva.pptx    # Presentación ejecutiva (10 slides)
│   ├── model_metrics.json             # Métricas del modelo interno
│   ├── competitor_metrics.json        # Métricas de proveedores
│   ├── model.pkl                      # Modelo serializado
│   └── figures/                       # 14 gráficos de análisis
├── ProductoNuevo.xlsx                  # Datos de clientes potenciales (4,315 registros)
├── ModelosCompetencia.xlsx            # Datos de proveedores (114,109 registros)
└── README.md
```

---

## Parte 1: Desarrollo de Modelo Predictivo

### 1.1 Selección de Variable Objetivo

**Decisión:** Se utilizó **Mora30** como variable objetivo (en lugar de Mora60).

**Justificación técnica:**

| Criterio | Mora30 | Mora60 |
|----------|--------|--------|
| Tasa de positivos | 24.4% | 11.7% |
| Detección | Temprana (30 días) | Tardía (60 días) |
| Balance de clases | Mejor para el modelo | Muy desbalanceado |
| Valor de negocio | Mayor (cobro preventivo) | Menor (daño ya ocurrido) |

Para un producto de **alto riesgo**, detectar morosidad temprana es fundamental. Mora30 permite:
- Acciones de cobro preventivas antes de que la situación se agrave
- Mayor cantidad de eventos positivos (1,052 vs 504) para que el modelo aprenda patrones
- Capturar un espectro más amplio de clientes problemáticos

### 1.2 Detección y Manejo de Data Leakage

**Hallazgo crítico:** La variable `MoraMax_UltimoSemestre` presentaba una correlación de **0.76** con Mora30.

**Análisis:** Al revisar la tabla cruzada, se descubrió que cuando `MoraMax_UltimoSemestre > 0`, el 100% de los casos eran Mora30=1. Esto significa que la variable contiene información **post-evento** sobre la morosidad del cliente.

**Decisión:** Se excluyó explícitamente del modelo. En un escenario real de originación, esta información no estaría disponible al momento de tomar la decisión de crédito. Incluirlo generaría un modelo con AUC perfecto (1.0) pero inútil en producción.

### 1.3 Feature Engineering

Se crearon 4 variables derivadas para capturar relaciones que las variables originales no expresaban directamente:

| Variable | Fórmula | Razonamiento |
|----------|---------|--------------|
| `Debt_to_Income` | Obligaciones / Ingresos | Ratio de endeudamiento clásico en scoring crediticio |
| `Expense_Ratio` | GastosFamiliares / Ingresos | Presión financiera relativa |
| `Experience_to_Age` | TiempoActividad / Edad | Proporción de vida laboral activa |
| `Cliente_Years` | TiempoClienteMeses / 12 | Antigüedad en años (más interpretable) |

### 1.4 Preprocesamiento

- **Encoding:** Label Encoding para 6 variables categóricas (OCUPACION, TIPCONTRATO, Estado_Civil, Genero, Nivel_Academico, Tipo_Vivienda). Se usó Label Encoding en lugar de One-Hot Encoding porque los modelos de árboles manejan bien variables ordinales codificadas numéricamente, y para Logistic Regression las categorías no tienen un orden inherente fuerte.
- **Train/Test Split:** 75/25 con estratificación por la variable objetivo para mantener la misma proporción de mora en ambos sets.
- **No se realizó imputación:** El dataset no tiene valores nulos.

### 1.5 Selección de Modelo

Se evaluaron 3 algoritmos:

| Modelo | ROC-AUC | Razón |
|--------|---------|-------|
| Logistic Regression | **0.6125** | ✓ Seleccionado: mejor AUC, interpretable |
| Random Forest | 0.6032 | Similar performance, menos interpretable |
| Gradient Boosting | 0.6011 | Similar performance, más complejo |

**Decisión:** Se seleccionó **Logistic Regression** porque:
1. Mejor ROC-AUC de los tres modelos
2. Coeficientes interpretables para el equipo de riesgo
3. Menor riesgo de overfitting con datos limitados
4. Más fácil de implementar en producción
5. Los modelos más complejos no mejoraron significativamente el AUC

### 1.6 Selección del Punto de Corte

**Proceso:** Se evaluaron thresholds de 0.10 a 0.90 en incrementos de 0.01, calculando para cada uno: accuracy, precision, recall, F1, y tasa de aprobación.

**Criterios de selección:**
- Para un producto de **alto riesgo**, se prioriza la captura de morosos (recall) sin rechazar más del 50% de los buenos.
- Se buscó el threshold que maximizara Youden's J statistic (sensibilidad + especificidad - 1) como referencia.
- Se seleccionó el threshold que logra al menos 50% de recall y 50% de approval rate.

**Resultado:** Punto de corte = **0.49**

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| ROC-AUC | 0.61 | Capacidad discriminante moderada |
| Precision | 30.5% | De rechazados, 30% son morosos reales |
| Recall | 58.6% | Se detecta 59% de los morosos |
| Approval Rate | 53.2% | Se aprueba poco más de la mitad |

### 1.7 Limitaciones Identificadas

1. **Poder predictivo moderado (AUC=0.61):** Las variables disponibles tienen capacidad limitada para predecir morosidad. Factores no capturados (historial crediticio bureau, comportamiento transaccional) son probablemente determinantes.
2. **Variables limitadas:** El dataset no incluye información de buró de crédito, historial de pagos, ni datos transaccionales.
3. **Trade-off negocio-riesgo:** Con el punto de corte, se rechazan ~47% de clientes pero solo se captura ~59% de morosos. Existe riesgo residual significativo.
4. **Datos estáticos:** Información de 2017-2018; condiciones macroeconómicas cambiantes pueden afectar la performance.

---

## Parte 2: Evaluación de Proveedores

### 2.1 Calidad de los Datos

| Aspecto | Proveedor AB | Proveedor XY |
|---------|-------------|-------------|
| Registros | 114,109 | 101,309 |
| Cobertura | 100% | 88.8% (12,800 missing) |
| Rango de scores | 6.0 - 12.1 | 0.1 - 27.8 |
| Std del score | 0.65 (muy estrecho) | 5.19 |
| Tasa de Default | 60.45% | 60.41% |

**Hallazgo:** El Proveedor XY tiene un 11.2% de datos sin puntaje, lo cual es una limitación operativa importante.

### 2.2 Capacidad Discriminante

| Métrica | Proveedor AB | Proveedor XY | Benchmark |
|---------|-------------|-------------|-----------|
| **ROC-AUC** | 0.5013 | 0.5018 | > 0.65 |
| **KS** | 0.0052 | 0.0051 | > 0.20 |
| **Gini** | 0.0026 | 0.0035 | > 0.30 |

**Conclusión crítica:** Ambos modelos tienen un poder discriminante **equivalente al azar**. Un AUC de 0.50 significa que el modelo no puede diferenciar entre buenos y malos pagadores mejor que una moneda.

### 2.3 Estabilidad (PSI)

| Métrica | Proveedor AB | Proveedor XY |
|---------|-------------|-------------|
| PSI | 0.0006 | 0.0011 |
| Interpretación | Estable | Estable |

Ambos modelos son estables en sus distribuciones (PSI < 0.10), pero la estabilidad no compensa la falta de poder predictivo.

### 2.4 Análisis por Deciles

Se segmentó la población en deciles según el puntaje de cada proveedor. Los resultados mostraron:

- **Sin monotonicidad:** La tasa de default oscila entre 59.7% y 61.1% en todos los deciles, sin la tendencia creciente esperada.
- **Sin lift significativo:** El lift por decil varía entre 0.98 y 1.01, lo que indica que ningún decil concentra significativamente más morosos que el promedio.
- **Superposición total:** Las distribuciones de scores para buenos y malos pagadores son prácticamente idénticas.

### 2.5 Recomendación

**No contratar a ninguno de los dos proveedores.**

Ambos modelos tienen un poder discriminante equivalente al azar. La inversión en estos proveedores no generaría valor agregado respecto a una selección aleatoria de clientes.

**Alternativas recomendadas:**
1. Incorporar datos de buró de crédito (historial, score, consultas)
2. Desarrollar modelo interno robusto con mejores datos
3. Explorar proveedores alternativos con modelos validados
4. Implementar scoring híbrido (interno + externo)

---

## Entregables

| Entregable | Ubicación | Descripción |
|-----------|-----------|-------------|
| Código comentado | `src/*.ipynb` | Notebooks con análisis paso a paso |
| Documento PDF | `output/analisis_completo.pdf` | Análisis detallado con gráficas y conclusiones |
| Presentación | `output/presentacion_ejecutiva.pptx` | Presentación ejecutiva (10 slides) |
| Gráficos | `output/figures/` | 14 figuras de análisis |
| Modelo | `output/model.pkl` | Modelo Logistic Regression serializado |

---

## Configuración del Entorno

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install pandas openpyxl scikit-learn matplotlib seaborn numpy reportlab python-pptx

# Ejecutar análisis
jupyter notebook src/
```

---

## Hallazgos Clave

1. **Data Leakage detectado:** La variable `MoraMax_UltimoSemestre` contenía información post-evento. Su exclusión redujo el AUC de 1.0 a 0.61, revelando el verdadero poder predictivo de las variables disponibles.
2. **Modelo interno viable:** Con AUC=0.61, el modelo interno es mejor que los proveedores evaluados (AUC≈0.50), aunque aún necesita mejores datos.
3. **Proveedores inviables:** Ninguno de los dos proveedores demostró capacidad discriminante significativa.
4. **Urgencia de datos externos:** La principal limitación es la falta de información de buró de crédito y datos transaccionales.
s