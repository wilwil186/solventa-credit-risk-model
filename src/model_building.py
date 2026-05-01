"""
Parte 1: Desarrollo de Modelo Predictivo
Solventa - Prueba Técnica Data Scientist Jr.

Objetivo: Construir un modelo que califique clientes y seleccione aquellos
con menor probabilidad de incumplimiento para un nuevo producto de alto riesgo.

Variable objetivo: Mora30 (justificación en el análisis)
"""

import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    classification_report,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
)
from sklearn.calibration import calibration_curve
import pickle
import os

# Create output directories
os.makedirs("output/figures", exist_ok=True)

# ============================================
# 1. CARGA DE DATOS
# ============================================
print("=" * 60)
print("PARTE 1: DESARROLLO DE MODELO PREDICTIVO")
print("=" * 60)

print("\n[1] Cargando datos...")
df = pd.read_excel("ProductoNuevo.xlsx")
print(f"   Registros: {df.shape[0]}")
print(f"   Variables: {df.shape[1]}")

# ============================================
# 2. SELECCIÓN DE VARIABLE OBJETIVO
# ============================================
print("\n[2] Selección de variable objetivo...")
print(f"\n   Mora30: {df['Mora30'].mean() * 100:.2f}% positivos")
print(f"   Mora60: {df['Mora60'].mean() * 100:.2f}% positivos")
print("""
   DECISIÓN: Se utiliza MORA30 como variable objetivo.
   Justificación:
   - Para productos de alto riesgo, detectar morosidad temprana (30 días)
     es más prudente que esperar 60 días.
   - Permite acciones de cobro preventivas más rápidas.
   - Mayor proporción de eventos positivos (24.4%) mejora la capacidad
     del modelo para aprender patrones de riesgo.
   - Mora30 captura un espectro más amplio de clientes problemáticos,
     reduciendo el riesgo de originación.""")

target = "Mora30"

# ============================================
# 3. ANÁLISIS EXPLORATORIO (EDA)
# ============================================
print("\n[3] Realizando análisis exploratorio...")

# 3a. Distribución de variable objetivo
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].bar(
    ["No Mora", "Mora 30+"],
    [df[target].value_counts()[0], df[target].value_counts()[1]],
    color=["#2ecc71", "#e74c3c"],
)
axes[0].set_title(f"Distribución de {target}")
axes[0].set_ylabel("Cantidad de clientes")
for i, v in enumerate([df[target].value_counts()[0], df[target].value_counts()[1]]):
    axes[0].text(
        i, v + 50, f"{v} ({v / len(df) * 100:.1f}%)", ha="center", fontweight="bold"
    )

# 3b. Correlaciones numéricas
numeric_cols = df.select_dtypes(include=[np.number]).columns.drop(
    ["ID", "FFECHA", target]
)
corr = df[numeric_cols.tolist() + [target]].corr()[target].sort_values(ascending=False)

colors = ["#e74c3c" if c > 0 else "#3498db" for c in corr.drop(target)]
axes[1].barh(range(len(corr) - 1), corr.drop(target).values, color=colors)
axes[1].set_yticks(range(len(corr) - 1))
axes[1].set_yticklabels(corr.drop(target).index, fontsize=8)
axes[1].set_title("Correlación con Mora30")
axes[1].axvline(x=0, color="black", linewidth=0.5)

plt.tight_layout()
plt.savefig("output/figures/01_eda_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 01_eda_overview.png")

# 3c. Análisis de variables categóricas
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
categorical_cols = [
    "OCUPACION",
    "TIPCONTRATO",
    "Estado_Civil",
    "Genero",
    "Nivel_Academico",
    "Tipo_Vivienda",
]

for ax, col in zip(axes.flatten(), categorical_cols):
    grouped = df.groupby(col)[target].agg(["mean", "count"])
    grouped = grouped.sort_values("mean", ascending=True)
    colors_bar = [
        "#e74c3c" if v > df[target].mean() else "#2ecc71" for v in grouped["mean"]
    ]
    ax.barh(range(len(grouped)), grouped["mean"] * 100, color=colors_bar)
    ax.set_yticks(range(len(grouped)))
    ax.set_yticklabels(grouped.index, fontsize=8)
    ax.axvline(x=df[target].mean() * 100, color="black", linestyle="--", linewidth=0.8)
    ax.set_title(f"Tasa Mora30 por {col}", fontsize=10)
    ax.set_xlabel("Tasa de morosidad (%)")

plt.tight_layout()
plt.savefig("output/figures/02_categorical_mora_rate.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 02_categorical_mora_rate.png")

# 3d. Análisis de variables continuas
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
continuous_cols = [
    "Ingresos",
    "GastosFamiliares",
    "Edad",
    "TiempoClienteMeses",
    "TiempoActividadAnios",
    "PORCEND",
]

for ax, col in zip(axes.flatten(), continuous_cols):
    df_plot = df[[col, target]].copy()
    df_plot[target] = df_plot[target].map({0: "No Mora", 1: "Mora 30+"})
    ax.boxplot(
        [
            df_plot[df_plot[target] == "No Mora"][col].dropna(),
            df_plot[df_plot[target] == "Mora 30+"][col].dropna(),
        ],
        labels=["No Mora", "Mora 30+"],
    )
    ax.set_title(f"Distribución de {col}", fontsize=10)

plt.tight_layout()
plt.savefig(
    "output/figures/03_continuous_distributions.png", dpi=150, bbox_inches="tight"
)
plt.close()
print("   -> Guardado: 03_continuous_distributions.png")

# ============================================
# 4. PREPROCESAMIENTO
# ============================================
print("\n[4] Preprocesamiento de datos...")

df_model = df.copy()

# Feature engineering
# Ratio de endeudamiento
df_model["Debt_to_Income"] = df_model["Obligaciones_SistemaFro"] / (
    df_model["Ingresos"] + 1
)
# Ratio gastos/ingresos
df_model["Expense_Ratio"] = df_model["GastosFamiliares"] / (df_model["Ingresos"] + 1)
# Experiencia relativa
df_model["Experience_to_Age"] = df_model["TiempoActividadAnios"] / (
    df_model["Edad"] + 1
)
# Antiguedad como cliente
df_model["Cliente_Years"] = df_model["TiempoClienteMeses"] / 12

# Label encoding para categóricas
label_encoders = {}
categorical_features = [
    "OCUPACION",
    "TIPCONTRATO",
    "Estado_Civil",
    "Genero",
    "Nivel_Academico",
    "Tipo_Vivienda",
]

for col in categorical_features:
    le = LabelEncoder()
    df_model[col + "_enc"] = le.fit_transform(df_model[col].astype(str))
    label_encoders[col] = le

# Seleccionar features
feature_cols = [
    "ExperienciaSectorFinanciero",
    "PersonasCargo",
    "GastosFamiliares",
    "GastoArriendo",
    "TiempoActividadAnios",
    "Edad",
    "Ingresos",
    "Tipo_Vivienda_enc",
    "TiempoClienteMeses",
    "Tiempo_SistemaFro",
    "PORCEND",
    "Obligaciones_SistemaFro",
    "OCUPACION_enc",
    "TIPCONTRATO_enc",
    "Estado_Civil_enc",
    "Genero_enc",
    "Nivel_Academico_enc",
    "Debt_to_Income",
    "Expense_Ratio",
    "Experience_to_Age",
    "Cliente_Years",
]

# Nota: MoraMax_UltimoSemestre fue excluido por ser variable de fuga de datos (data leakage).
# Esta variable contiene información post-evento sobre la morosidad máxima del cliente,
# lo que permitiría predecir perfectamente Mora30 y Mora60. En un escenario real de
# originación, esta información no estaría disponible al momento de la decisión.

X = df_model[feature_cols]
y = df_model[target]

# Train/test split estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"   Train: {len(X_train)} registros ({y_train.mean() * 100:.1f}% mora)")
print(f"   Test:  {len(X_test)} registros ({y_test.mean() * 100:.1f}% mora)")

# ============================================
# 5. ENTRENAMIENTO DE MODELOS
# ============================================
print("\n[5] Entrenando modelos...")

models = {
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        min_samples_split=20,
        min_samples_leaf=10,
        subsample=0.8,
        random_state=42,
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
        class_weight="balanced",
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, C=0.1, class_weight="balanced", random_state=42
    ),
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    results[name] = {"model": model, "y_prob": y_prob, "auc": auc}
    print(f"   {name}: ROC-AUC = {auc:.4f}")

best_model_name = max(results, key=lambda k: results[k]["auc"])
best_model = results[best_model_name]["model"]
best_probs = results[best_model_name]["y_prob"]
print(
    f"\n   Mejor modelo: {best_model_name} (ROC-AUC: {results[best_model_name]['auc']:.4f})"
)

# ============================================
# 6. CURVAS ROC Y PR
# ============================================
print("\n[6] Generando curvas ROC y Precision-Recall...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ROC Curve
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
    axes[0].plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.4f})", linewidth=2)
axes[0].plot([0, 1], [0, 1], "k--", linewidth=1)
axes[0].set_xlabel("Tasa de Falsos Positivos")
axes[0].set_ylabel("Tasa de Verdaderos Positivos")
axes[0].set_title("Curva ROC - Comparación de Modelos")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Precision-Recall Curve
for name, res in results.items():
    precision, recall, _ = precision_recall_curve(y_test, res["y_prob"])
    axes[1].plot(recall, precision, label=name, linewidth=2)
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("Precision")
axes[1].set_title("Curva Precision-Recall")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("output/figures/04_roc_pr_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 04_roc_pr_curves.png")

# ============================================
# 7. IMPORTANCIA DE VARIABLES
# ============================================
print("\n[7] Analizando importancia de variables...")

# Feature importance del mejor modelo
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
elif hasattr(best_model, "coef_"):
    importances = np.abs(best_model.coef_[0])
else:
    importances = np.zeros(len(feature_cols))

feat_imp = pd.DataFrame(
    {"Feature": feature_cols, "Importance": importances}
).sort_values("Importance", ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(feat_imp["Feature"], feat_imp["Importance"], color="#3498db")
ax.set_xlabel("Importancia")
ax.set_title(f"Importancia de Variables - {best_model_name}")
plt.tight_layout()
plt.savefig("output/figures/05_feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 05_feature_importance.png")

# ============================================
# 8. SELECCIÓN DE PUNTO DE CORTE
# ============================================
print("\n[8] Selección de punto de corte...")

thresholds = np.arange(0.1, 0.9, 0.01)
metrics = []

for t in thresholds:
    y_pred_t = (best_probs >= t).astype(int)
    metrics.append(
        {
            "threshold": t,
            "accuracy": accuracy_score(y_test, y_pred_t),
            "precision": precision_score(y_test, y_pred_t, zero_division=0),
            "recall": recall_score(y_test, y_pred_t, zero_division=0),
            "f1": f1_score(y_test, y_pred_t, zero_division=0),
            "predicted_default": y_pred_t.sum(),
            "predicted_approved": (y_pred_t == 0).sum(),
            "approval_rate": (y_pred_t == 0).sum() / len(y_test),
        }
    )

metrics_df = pd.DataFrame(metrics)

# Encontrar punto de corte óptimo (max F1)
optimal_idx = metrics_df["f1"].idxmax()
optimal_threshold = metrics_df.loc[optimal_idx, "threshold"]

# Para un producto de ALTO RIESGO, preferimos mayor precision
# Usamos un threshold más conservador que maximice precision manteniendo recall aceptable
high_precision_thresholds = metrics_df[metrics_df["precision"] >= 0.65]
if len(high_precision_thresholds) > 0:
    conservative_threshold = high_precision_thresholds.iloc[0]["threshold"]
else:
    conservative_threshold = 0.45

recommended_threshold = conservative_threshold
y_pred_final = (best_probs >= recommended_threshold).astype(int)

print(f"   Threshold F1-max: {optimal_threshold:.2f}")
print(f"   Threshold recomendado (alto riesgo): {recommended_threshold:.2f}")
print(
    f"   Tasa de aprobación: {metrics_df[metrics_df['threshold'] == recommended_threshold]['approval_rate'].values[0] * 100:.1f}%"
)
print(
    f"   Precision a {recommended_threshold:.2f}: {precision_score(y_test, y_pred_final):.4f}"
)
print(
    f"   Recall a {recommended_threshold:.2f}: {recall_score(y_test, y_pred_final):.4f}"
)

# ============================================
# 9. ANÁLISIS DEL PUNTO DE CORTE
# ============================================
print("\n[9] Visualizando análisis de punto de corte...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Metrics vs threshold
axes[0].plot(
    metrics_df["threshold"], metrics_df["precision"], label="Precision", linewidth=2
)
axes[0].plot(metrics_df["threshold"], metrics_df["recall"], label="Recall", linewidth=2)
axes[0].plot(metrics_df["threshold"], metrics_df["f1"], label="F1-Score", linewidth=2)
axes[0].axvline(
    x=recommended_threshold,
    color="red",
    linestyle="--",
    label=f"Corte={recommended_threshold:.2f}",
)
axes[0].axvline(
    x=optimal_threshold,
    color="green",
    linestyle=":",
    label=f"F1-max={optimal_threshold:.2f}",
)
axes[0].set_xlabel("Threshold")
axes[0].set_ylabel("Valor")
axes[0].set_title("Métricas vs Punto de Corte")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Approval rate vs threshold
ax2 = axes[1]
ax2.plot(
    metrics_df["threshold"],
    metrics_df["approval_rate"] * 100,
    color="#2ecc71",
    linewidth=2,
)
ax2.axvline(
    x=recommended_threshold,
    color="red",
    linestyle="--",
    label=f"Corte={recommended_threshold:.2f}",
)
ax2.set_xlabel("Threshold")
ax2.set_ylabel("Tasa de Aprobación (%)", color="#2ecc71")
ax2.set_title("Tasa de Aprobación vs Punto de Corte")
ax2.legend(loc="upper right")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("output/figures/06_cutoff_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 06_cutoff_analysis.png")

# ============================================
# 10. MATRIZ DE CONFUSIÓN
# ============================================
print("\n[10] Matriz de confusión...")

cm = confusion_matrix(y_test, y_pred_final)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    ax=ax,
    xticklabels=["Aprobado", "Rechazado"],
    yticklabels=["No Mora", "Mora 30+"],
)
ax.set_xlabel("Predicción")
ax.set_ylabel("Real")
ax.set_title(
    f"Matriz de Confusión - {best_model_name} (corte={recommended_threshold:.2f})"
)
plt.tight_layout()
plt.savefig("output/figures/07_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 07_confusion_matrix.png")

# ============================================
# 11. CALIBRACIÓN
# ============================================
print("\n[11] Curva de calibración...")

fig, ax = plt.subplots(figsize=(6, 5))
frac_of_pos, mean_pred_val = calibration_curve(
    y_test, best_probs, n_bins=10, strategy="uniform"
)
ax.plot(mean_pred_val, frac_of_pos, "s-", label=best_model_name, markersize=8)
ax.plot([0, 1], [0, 1], "k:", label="Perfecto")
ax.set_xlabel("Probabilidad predicha")
ax.set_ylabel("Fracción de positivos")
ax.set_title("Curva de Calibración")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output/figures/08_calibration.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 08_calibration.png")

# ============================================
# 12. REPORTE FINAL
# ============================================
print("\n" + "=" * 60)
print("RESUMEN DEL MODELO")
print("=" * 60)

print(f"\nModelo seleccionado: {best_model_name}")
print(f"ROC-AUC: {results[best_model_name]['auc']:.4f}")
print(f"Punto de corte: {recommended_threshold:.2f}")
print(f"\nMétricas en test:")
print(f"  Accuracy:  {accuracy_score(y_test, y_pred_final):.4f}")
print(f"  Precision: {precision_score(y_test, y_pred_final):.4f}")
print(f"  Recall:    {recall_score(y_test, y_pred_final):.4f}")
print(f"  F1-Score:  {f1_score(y_test, y_pred_final):.4f}")
print(f"\nTasa de aprobación: {(y_pred_final == 0).sum() / len(y_test) * 100:.1f}%")
print(f"Clientes rechazados: {y_pred_final.sum()} de {len(y_test)}")

print(
    "\n"
    + classification_report(y_test, y_pred_final, target_names=["No Mora", "Mora 30+"])
)

# Guardar modelo
with open("output/model.pkl", "wb") as f:
    pickle.dump(
        {
            "model": best_model,
            "feature_cols": feature_cols,
            "label_encoders": label_encoders,
            "threshold": recommended_threshold,
            "model_name": best_model_name,
        },
        f,
    )
print("Modelo guardado en output/model.pkl")

# Guardar métricas para reporte
report_metrics = {
    "best_model": best_model_name,
    "roc_auc": results[best_model_name]["auc"],
    "threshold": recommended_threshold,
    "accuracy": accuracy_score(y_test, y_pred_final),
    "precision": precision_score(y_test, y_pred_final),
    "recall": recall_score(y_test, y_pred_final),
    "f1": f1_score(y_test, y_pred_final),
    "approval_rate": (y_pred_final == 0).sum() / len(y_test),
    "mora30_rate": y.mean(),
    "mora60_rate": df["Mora60"].mean(),
    "feature_importance": feat_imp.to_dict("records"),
    "all_model_auc": {name: res["auc"] for name, res in results.items()},
    "confusion_matrix": cm.tolist(),
    "metrics_by_threshold": metrics_df.to_dict("records"),
}

import json

with open("output/model_metrics.json", "w") as f:
    json.dump(report_metrics, f, indent=2)

print("\nParte 1 completada exitosamente!")
