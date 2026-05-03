"""
Generación de Reporte PDF - Análisis Completo
Solventa - Prueba Técnica Data Scientist Jr.

Documento PDF con análisis de Partes 1 y 2, hallazgos, limitaciones y conclusiones.
"""

import warnings

warnings.filterwarnings("ignore")

import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    ListFlowable,
    ListItem,
    KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable

# Load metrics
with open("output/model_metrics.json", "r") as f:
    model_metrics = json.load(f)
with open("output/competitor_metrics.json", "r") as f:
    competitor_metrics = json.load(f)

# Create PDF
doc = SimpleDocTemplate(
    "output/analisis_completo.pdf",
    pagesize=letter,
    rightMargin=72,
    leftMargin=72,
    topMargin=72,
    bottomMargin=72,
)

styles = getSampleStyleSheet()

# Custom styles
styles.add(
    ParagraphStyle(
        name="CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=HexColor("#2C3E50"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
)

styles.add(
    ParagraphStyle(
        name="Subtitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=HexColor("#7F8C8D"),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
)

styles.add(
    ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=HexColor("#2C3E50"),
        spaceBefore=20,
        spaceAfter=10,
        borderWidth=0,
        borderColor=HexColor("#3498DB"),
        borderPadding=5,
    )
)

styles.add(
    ParagraphStyle(
        name="SubsectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=HexColor("#2980B9"),
        spaceBefore=12,
        spaceAfter=6,
    )
)

styles.add(
    ParagraphStyle(
        name="BodyText2",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
)

styles.add(
    ParagraphStyle(
        name="BulletPoint",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=3,
    )
)

styles.add(
    ParagraphStyle(
        name="MetricBox",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=HexColor("#2C3E50"),
    )
)

# Build content
story = []

# =====================
# COVER PAGE
# =====================
story.append(Spacer(1, 2 * inch))
story.append(Paragraph("Solventa", styles["CustomTitle"]))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="80%", thickness=2, color=HexColor("#3498DB")))
story.append(Spacer(1, 30))
story.append(
    Paragraph(
        "Análisis de Modelo Predictivo y<br/>Evaluación de Proveedores",
        ParagraphStyle(
            "cover_sub",
            parent=styles["Title"],
            fontSize=20,
            textColor=HexColor("#34495E"),
            alignment=TA_CENTER,
        ),
    )
)
story.append(Spacer(1, 20))
story.append(Paragraph("Prueba Técnica - Data Scientist Jr.", styles["Subtitle"]))
story.append(Spacer(1, 40))
story.append(HRFlowable(width="80%", thickness=1, color=HexColor("#BDC3C7")))
story.append(Spacer(1, 20))
story.append(
    Paragraph(
        "Fecha: Mayo 2026",
        ParagraphStyle(
            "date",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=HexColor("#7F8C8D"),
        ),
    )
)

story.append(PageBreak())

# =====================
# TABLA DE CONTENIDOS
# =====================
story.append(Paragraph("Tabla de Contenido", styles["SectionTitle"]))
story.append(Spacer(1, 10))
toc_items = [
    ("1.", "Desarrollo de Modelo Predictivo", "3"),
    ("  1.1", "Selección de Variable Objetivo", "3"),
    ("  1.2", "Análisis Exploratorio de Datos", "3"),
    ("  1.3", "Preprocesamiento y Feature Engineering", "4"),
    ("  1.4", "Entrenamiento y Comparación de Modelos", "5"),
    ("  1.5", "Selección del Punto de Corte", "6"),
    ("  1.6", "Limitaciones del Modelo", "7"),
    ("2.", "Evaluación de Modelos de Proveedores", "8"),
    ("  2.1", "Capacidad Discriminante", "8"),
    ("  2.2", "Análisis por Deciles", "9"),
    ("  2.3", "Estabilidad del Puntaje (PSI)", "9"),
    ("  2.4", "Separación entre Buenos y Malos", "10"),
    ("  2.5", "Recomendación de Proveedor", "10"),
    ("3.", "Conclusiones y Recomendaciones Finales", "11"),
]

for num, title, page in toc_items:
    is_main = "." in num and num.count(".") == 1
    style = ParagraphStyle(
        "toc",
        parent=styles["BodyText"],
        fontSize=11 if is_main else 10,
        leftIndent=0 if is_main else 20,
        textColor=HexColor("#2C3E50") if is_main else HexColor("#555555"),
        fontName="Helvetica-Bold" if is_main else "Helvetica",
        spaceAfter=4,
    )
    story.append(Paragraph(f"<b>{num}</b> {title}", style))

story.append(PageBreak())

# =====================
# PARTE 1: MODELO PREDICTIVO
# =====================
story.append(Paragraph("1. Desarrollo de Modelo Predictivo", styles["SectionTitle"]))
story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#3498DB")))
story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "El objetivo de esta sección es construir un modelo que permita calificar a los clientes "
        "potenciales del nuevo producto de alto riesgo y seleccionar aquellos con menor probabilidad "
        "de incumplimiento. La base de datos <b>ProductoNuevo.xlsx</b> contiene 4,315 registros "
        "con 22 variables incluyendo información demográfica, financiera y de comportamiento.",
        styles["BodyText2"],
    )
)

# 1.1 Variable Objetivo
story.append(Paragraph("1.1 Selección de Variable Objetivo", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "Se evaluaron dos posibles variables objetivo: <b>Mora30</b> (morosidad a 30 días) y "
        "<b>Mora60</b> (morosidad a 60 días). La distribución observada fue:",
        styles["BodyText2"],
    )
)

story.append(
    Paragraph(
        f"• <b>Mora30:</b> {model_metrics['mora30_rate'] * 100:.1f}% de clientes en mora (1,052 de 4,315)",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        f"• <b>Mora60:</b> {model_metrics['mora60_rate'] * 100:.1f}% de clientes en mora (504 de 4,315)",
        styles["BulletPoint"],
    )
)

story.append(
    Paragraph(
        "<b>Decisión:</b> Se seleccionó <b>Mora30</b> como variable objetivo.",
        styles["BodyText2"],
    )
)

story.append(Paragraph("<b>Justificación:</b>", styles["BodyText2"]))
story.append(
    Paragraph(
        "Para un producto de alto riesgo, detectar morosidad temprana es fundamental. Mora30 "
        "permite identificar clientes problemáticos antes de que la situación se agrave, facilitando "
        "acciones de cobro preventivas. Además, la mayor proporción de eventos positivos (24.4% vs 11.7%) "
        "proporciona más información al modelo para aprender patrones de riesgo.",
        styles["BodyText2"],
    )
)

# EDA Image
story.append(Spacer(1, 10))
story.append(
    Paragraph(
        "<b>Figura 1:</b> Distribución de variable objetivo y correlaciones",
        ParagraphStyle(
            "caption",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)
story.append(
    Image("output/figures/01_eda_overview.png", width=6.5 * inch, height=2.5 * inch)
)

# 1.2 EDA
story.append(Paragraph("1.2 Análisis Exploratorio de Datos", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "Se analizaron las relaciones entre las variables categóricas y continuas con la tasa de morosidad. "
        "Los hallazgos principales fueron:",
        styles["BodyText2"],
    )
)

story.append(
    Image(
        "output/figures/02_categorical_mora_rate.png",
        width=6.5 * inch,
        height=3.5 * inch,
    )
)
story.append(
    Paragraph(
        "<b>Figura 2:</b> Tasa de Mora30 por variable categórica",
        ParagraphStyle(
            "caption2",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 1.3 Preprocesamiento
story.append(
    Paragraph("1.3 Preprocesamiento y Feature Engineering", styles["SubsectionTitle"])
)

story.append(
    Paragraph("Se realizaron las siguientes transformaciones:", styles["BodyText2"])
)
story.append(
    Paragraph(
        "• <b>Encoding:</b> Label encoding para 6 variables categóricas (OCUPACION, TIPCONTRATO, Estado_Civil, Genero, Nivel_Academico, Tipo_Vivienda)",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• <b>Feature engineering:</b> Se crearon 4 nuevas variables:",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "  - Debt_to_Income: Ratio de endeudamiento (obligaciones/ingresos)",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "  - Expense_Ratio: Ratio gastos familiares sobre ingresos",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "  - Experience_to_Age: Experiencia laboral relativa a la edad",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "  - Cliente_Years: Antigüedad como cliente en años", styles["BulletPoint"]
    )
)

story.append(
    Paragraph(
        "<b>Nota importante sobre Data Leakage:</b> La variable <b>MoraMax_UltimoSemestre</b> fue excluida "
        "del modelo porque contiene información post-evento sobre la morosidad máxima del cliente. "
        "Presenta una correlación de 0.76 con Mora30 y, si se incluyera, permitiría predecir perfectamente "
        "el target. En un escenario real de originación, esta información no estaría disponible al momento "
        "de la decisión de crédito.",
        styles["BodyText2"],
    )
)

story.append(
    Paragraph(
        "La división train/test fue 75/25 con estratificación, resultando en 3,236 registros de "
        "entrenamiento y 1,079 de prueba, ambos con 24.4% de tasa de mora.",
        styles["BodyText2"],
    )
)

# 1.4 Modelos
story.append(
    Paragraph("1.4 Entrenamiento y Comparación de Modelos", styles["SubsectionTitle"])
)

story.append(
    Paragraph(
        "Se entrenaron tres algoritmos con hyperparámetros optimizados para evitar overfitting:",
        styles["BodyText2"],
    )
)

model_data = [
    ["Modelo", "ROC-AUC", "Descripción"],
    [
        "Logistic Regression",
        f"{model_metrics['all_model_auc']['Logistic Regression']:.4f}",
        "Modelo lineal interpretable, buen baseline",
    ],
    [
        "Random Forest",
        f"{model_metrics['all_model_auc']['Random Forest']:.4f}",
        "Ensemble de árboles, robusto a ruido",
    ],
    [
        "Gradient Boosting",
        f"{model_metrics['all_model_auc']['Gradient Boosting']:.4f}",
        "Ensemble secuencial, alto poder predictivo",
    ],
]

t = Table(model_data, colWidths=[2 * inch, 1 * inch, 3 * inch])
t.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), HexColor("#ECF0F1")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDC3C7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.append(t)
story.append(Spacer(1, 10))

story.append(
    Paragraph(
        f"El modelo seleccionado fue <b>{model_metrics['best_model']}</b> con un ROC-AUC de "
        f"{model_metrics['roc_auc']:.4f}. Aunque este valor es moderado, es consistente con la "
        "complejidad del problema: los datos disponibles tienen poder predictivo limitado para "
        "diferenciar entre buenos y malos pagadores.",
        styles["BodyText2"],
    )
)

story.append(
    Image("output/figures/04_roc_pr_curves.png", width=6.5 * inch, height=2.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 3:</b> Curvas ROC y Precision-Recall de los modelos",
        ParagraphStyle(
            "caption3",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

story.append(
    Image("output/figures/05_feature_importance.png", width=6 * inch, height=4.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 4:</b> Importancia de variables en el modelo seleccionado",
        ParagraphStyle(
            "caption4",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 1.5 Punto de Corte
story.append(Paragraph("1.5 Selección del Punto de Corte", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "La selección del punto de corte es crítica para el negocio. Para un producto de alto riesgo, "
        "se debe balancear la captura de clientes morosos (recall) con la aprobación de clientes buenos "
        "(approval rate).",
        styles["BodyText2"],
    )
)

mm = model_metrics
story.append(
    Paragraph(
        f"<b>Punto de corte recomendado:</b> {mm['threshold']:.2f}", styles["BodyText2"]
    )
)
story.append(Spacer(1, 5))

metrics_table = [
    ["Métrica", "Valor", "Interpretación"],
    ["ROC-AUC", f"{mm['roc_auc']:.4f}", "Capacidad discriminante moderada"],
    [
        "Precision",
        f"{mm['precision']:.4f}",
        f"De los rechazados, {mm['precision']*100:.0f}% son realmente morosos",
    ],
    [
        "Recall",
        f"{mm['recall']:.4f}",
        f"Se captura {mm['recall']*100:.0f}% de los morosos",
    ],
    ["F1-Score", f"{mm['f1']:.4f}", "Balance entre precision y recall"],
    [
        "Approval Rate",
        f"{mm['approval_rate'] * 100:.1f}%",
        "Porcentaje de clientes aprobados",
    ],
]

t2 = Table(metrics_table, colWidths=[1.5 * inch, 1.5 * inch, 3 * inch])
t2.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), HexColor("#ECF0F1")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDC3C7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.append(t2)
story.append(Spacer(1, 10))

story.append(
    Image("output/figures/06_cutoff_analysis.png", width=6.5 * inch, height=2.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 5:</b> Análisis de punto de corte - métricas y tasa de aprobación",
        ParagraphStyle(
            "caption5",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

story.append(
    Image("output/figures/07_confusion_matrix.png", width=3 * inch, height=2.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 6:</b> Matriz de confusión",
        ParagraphStyle(
            "caption6",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 1.6 Limitaciones
story.append(Paragraph("1.6 Limitaciones del Modelo", styles["SubsectionTitle"]))

story.append(
    Paragraph("Las principales limitaciones identificadas son:", styles["BodyText2"])
)
story.append(
    Paragraph(
        "• <b>Poder predictivo moderado (AUC=0.61):</b> Las variables disponibles tienen capacidad "
        "limitada para predecir morosidad. Esto sugiere que factores no capturados en los datos "
        "(historial crediticio bureau, comportamiento transaccional) podrían ser determinantes.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• <b>Variables limitadas:</b> El dataset no incluye información de buró de crédito, "
        "historial de pagos, ni datos transaccionales, que son típicamente los predictores más "
        "fuertes en scoring crediticio.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• <b>Trade-off negocio-riesgo:</b> Con el punto de corte seleccionado, se rechazan ~47% "
        "de los clientes, pero solo se captura ~59% de los morosos. Existe un riesgo residual "
        "significativo de aprobar clientes que caerán en mora.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• <b>Datos estáticos:</b> La información corresponde a un corte temporal específico "
        "(2017-2018). Condiciones macroeconómicas cambiantes pueden afectar la performance del modelo.",
        styles["BulletPoint"],
    )
)

story.append(PageBreak())

# =====================
# PARTE 2: PROVEEDORES
# =====================
story.append(
    Paragraph("2. Evaluación de Modelos de Proveedores", styles["SectionTitle"])
)
story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#3498DB")))
story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "La base <b>ModelosCompetencia.xlsx</b> contiene 114,109 registros con los puntajes de "
        "dos proveedores (AB y XY) y la variable de default. El análisis se realiza para determinar "
        "cuál proveedor ofrece el modelo más efectivo.",
        styles["BodyText2"],
    )
)

# 2.1 Capacidad Discriminante
story.append(Paragraph("2.1 Capacidad Discriminante", styles["SubsectionTitle"]))

cm = competitor_metrics
story.append(
    Paragraph(
        f"La tasa de default en la muestra es <b>{cm['default_rate_ab'] * 100:.2f}%</b>, lo que indica "
        "un segmento de alto riesgo. Los resultados de capacidad discriminante fueron:",
        styles["BodyText2"],
    )
)

disc_table = [
    ["Métrica", "Proveedor AB", "Proveedor XY", "Interpretación"],
    [
        "ROC-AUC",
        f"{cm['auc_ab']:.4f}",
        f"{cm['auc_xy']:.4f}",
        "Cercano a 0.5 = sin poder discriminante",
    ],
    [
        "KS",
        f"{cm['ks_ab']:.4f}",
        f"{cm['ks_xy']:.4f}",
        "Muy bajo (< 0.10 = pobre separación)",
    ],
    [
        "Gini",
        f"{cm['gini_ab']:.4f}",
        f"{cm['gini_xy']:.4f}",
        "Cercano a 0 = sin capacidad predictiva",
    ],
]

t3 = Table(disc_table, colWidths=[1.2 * inch, 1.3 * inch, 1.3 * inch, 2.2 * inch])
t3.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), HexColor("#ECF0F1")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDC3C7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.append(t3)
story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "<b>Hallazgo crítico:</b> Ambos proveedores presentan un ROC-AUC cercano a 0.50 y un "
        "estadístico KS inferior a 0.01. Esto significa que <b>ninguno de los dos modelos tiene "
        "capacidad discriminante significativa</b>. Los puntajes no permiten diferenciar entre "
        "clientes buenos y malos de manera efectiva.",
        styles["BodyText2"],
    )
)

story.append(
    Image("output/figures/09_roc_competencia.png", width=5 * inch, height=3.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 7:</b> Curva ROC comparativa - ambos modelos cerca del azar",
        ParagraphStyle(
            "caption7",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 2.2 Deciles
story.append(Paragraph("2.2 Análisis por Deciles", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "Al segmentar los clientes en deciles según el puntaje, se observa que la tasa de default "
        "es prácticamente uniforme en todos los rangos para ambos proveedores, sin la monotonicidad "
        "esperada (donde deciles más altos deberían tener mayor tasa de default).",
        styles["BodyText2"],
    )
)

story.append(
    Image(
        "output/figures/10_deciles_competencia.png", width=6.5 * inch, height=3 * inch
    )
)
story.append(
    Paragraph(
        "<b>Figura 8:</b> Distribución de buenos y malos por deciles",
        ParagraphStyle(
            "caption8",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

story.append(
    Image("output/figures/11_default_rate_deciles.png", width=6 * inch, height=3 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 9:</b> Tasa de default por decil - sin tendencia clara",
        ParagraphStyle(
            "caption9",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 2.3 PSI
story.append(Paragraph("2.3 Estabilidad del Puntaje (PSI)", styles["SubsectionTitle"]))

psi_ab = cm["psi_ab"]
psi_xy = cm["psi_xy"] if cm["psi_xy"] else float("nan")
psi_xy_str = f"{psi_xy:.4f}" if not __import__("numpy").isnan(psi_xy) else "N/A"

story.append(
    Paragraph(
        f"• <b>PSI Proveedor AB:</b> {psi_ab:.4f} - Estable", styles["BulletPoint"]
    )
)
story.append(
    Paragraph(
        f"• <b>PSI Proveedor XY:</b> {psi_xy_str} - Estable", styles["BulletPoint"]
    )
)

story.append(
    Paragraph(
        "Ambos modelos muestran estabilidad en sus distribuciones de puntaje a lo largo del tiempo "
        "(PSI < 0.10). Sin embargo, la estabilidad no compensa la falta de poder predictivo.",
        styles["BodyText2"],
    )
)

story.append(
    Image(
        "output/figures/12_score_distribution.png", width=6.5 * inch, height=2.5 * inch
    )
)
story.append(
    Paragraph(
        "<b>Figura 10:</b> Distribución de puntajes por proveedor",
        ParagraphStyle(
            "caption10",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

# 2.4 Separación
story.append(
    Paragraph("2.4 Separación entre Buenos y Malos", styles["SubsectionTitle"])
)

story.append(
    Image(
        "output/figures/13_separation_analysis.png", width=6.5 * inch, height=2.5 * inch
    )
)
story.append(
    Paragraph(
        "<b>Figura 11:</b> Distribución de scores por default - superposición total",
        ParagraphStyle(
            "caption11",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

story.append(
    Paragraph(
        "Las curvas de densidad muestran una superposición casi total entre la distribución de scores "
        "de clientes buenos y malos. Esto confirma que los puntajes no separan efectivamente a los "
        "dos grupos.",
        styles["BodyText2"],
    )
)

# 2.5 Recomendación
story.append(Paragraph("2.5 Recomendación de Proveedor", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "<b>Recomendación: Ninguno de los dos proveedores es adecuado para la tarea.</b>",
        styles["BodyText2"],
    )
)

story.append(
    Paragraph(
        "Si bien el Proveedor XY presenta un AUC marginalmente superior (0.5018 vs 0.5013), "
        "la diferencia es estadísticamente insignificante. Ambos modelos tienen un poder discriminante "
        "equivalente al azar.",
        styles["BodyText2"],
    )
)

story.append(Paragraph("<b>Observaciones adicionales:</b>", styles["BodyText2"]))
story.append(
    Paragraph(
        f"• El Proveedor AB tiene cobertura completa (114,109 registros) mientras que XY tiene "
        f"11.2% de datos faltantes (12,800 registros sin puntaje), lo cual es una limitación operativa importante.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• El rango de scores de AB es muy estrecho (6.0 a 12.1, std=0.65) mientras que XY tiene "
        "mayor variabilidad (0.1 a 27.8, std=5.19), pero ninguna se traduce en poder predictivo.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• Se recomienda explorar proveedores alternativos o desarrollar un modelo interno que "
        "incorpore variables de buró de crédito y datos transaccionales.",
        styles["BulletPoint"],
    )
)

story.append(
    Image("output/figures/14_lift_analysis.png", width=6.5 * inch, height=2.5 * inch)
)
story.append(
    Paragraph(
        "<b>Figura 12:</b> Análisis de Lift por decil - sin lift significativo",
        ParagraphStyle(
            "caption12",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        ),
    )
)

story.append(PageBreak())

# =====================
# 3. CONCLUSIONES
# =====================
story.append(
    Paragraph("3. Conclusiones y Recomendaciones Finales", styles["SectionTitle"])
)
story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#3498DB")))
story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "<b>3.1 Sobre el Modelo Predictivo Interno</b>", styles["SubsectionTitle"]
    )
)

story.append(
    Paragraph(
        "Se logró construir un modelo con ROC-AUC de 0.61, que si bien es moderado, representa "
        "un punto de partida útil para la selección de clientes del nuevo producto. El modelo "
        "de Logistic Regression fue seleccionado por su interpretabilidad y performance comparable "
        "a modelos más complejos.",
        styles["BodyText2"],
    )
)

story.append(Paragraph("<b>Recomendaciones:</b>", styles["BodyText2"]))
story.append(
    Paragraph(
        "• Incorporar variables externas: datos de buró de crédito, historial de pagos, variables "
        "macroeconómicas.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• Implementar un proceso de monitoreo continuo con recálculo del modelo cada trimestre.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "• Definir políticas de aprobación por segmento, no solo por score (ej: diferentes thresholds "
        "por rango de ingresos o tipo de ocupación).",
        styles["BulletPoint"],
    )
)

story.append(Paragraph("<b>3.2 Sobre los Proveedores</b>", styles["SubsectionTitle"]))

story.append(
    Paragraph(
        "Ambos proveedores evaluados (AB y XY) presentan modelos sin capacidad discriminante "
        "significativa (AUC ≈ 0.50). <b>No se recomienda contratar a ninguno</b> en su estado actual. "
        "La inversión en estos proveedores no generaría valor agregado respecto a una selección aleatoria "
        "de clientes.",
        styles["BodyText2"],
    )
)

story.append(
    Paragraph("<b>3.3 Recomendación Estratégica</b>", styles["SubsectionTitle"])
)

story.append(
    Paragraph(
        "Dada la debilidad tanto del modelo interno como de los proveedores evaluados, se recomienda:",
        styles["BodyText2"],
    )
)
story.append(
    Paragraph(
        "1. <b>Enriquecer los datos:</b> Integrar fuentes adicionales de información crediticia "
        "para mejorar el poder predictivo.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "2. <b>Desarrollar modelo interno robusto:</b> Con mejores datos, un modelo interno "
        "puede superar a proveedores externos y ser más económico a largo plazo.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "3. <b>Implementar políticas complementarias:</b> Además del score, usar límites de crédito "
        "diferenciados, períodos de prueba, y garantías para mitigar el riesgo en este segmento.",
        styles["BulletPoint"],
    )
)
story.append(
    Paragraph(
        "4. <b>Monitoreo riguroso:</b> Establecer KPIs de performance del modelo (vintage analysis, "
        "roll rates, PSI) para detectar degradación temprana.",
        styles["BulletPoint"],
    )
)

# Build PDF
doc.build(story)
print("PDF generado: output/analisis_completo.pdf")
