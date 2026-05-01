"""
Parte 2: Evaluación de Modelos de Proveedores (AB vs XY)
Solventa - Prueba Técnica Data Scientist Jr.

Objetivo: Determinar cuál de los dos modelos es más efectivo para
la calificación de clientes y recomendar el proveedor a contratar.

Criterios de análisis:
- Capacidad discriminante (ROC-AUC, KS, Gini)
- Estabilidad del puntaje (PSI)
- Distribución de buenos y malos por rangos de score
- Indicadores comparativos
"""

import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve
import os
import json

os.makedirs("output/figures", exist_ok=True)

# ============================================
# 1. CARGA Y PREPARACIÓN
# ============================================
print("=" * 60)
print("PARTE 2: EVALUACIÓN DE MODELOS DE PROVEEDORES")
print("=" * 60)

print("\n[1] Cargando datos...")
df = pd.read_excel("ModelosCompetencia.xlsx")
print(f"   Registros: {df.shape[0]}")
print(f"   Columnas: {list(df.columns)}")

# Limpiar puntajes (PuntajeXY tiene "." como missing)
df["PuntajeXY"] = pd.to_numeric(df["PuntajeXY"], errors="coerce")

print(
    f"\n   PuntajeXY missing: {df['PuntajeXY'].isnull().sum()} ({df['PuntajeXY'].isnull().mean() * 100:.2f}%)"
)

df_clean = df.dropna(subset=["PuntajeXY"]).copy()
print(f"   Registros limpios (ambos puntajes): {len(df_clean)}")

# Estadísticas básicas
print("\n   Estadísticas PuntajeAB:")
print(f"     Media: {df['PuntajeAB'].mean():.4f}, Std: {df['PuntajeAB'].std():.4f}")
print(f"     Min: {df['PuntajeAB'].min():.4f}, Max: {df['PuntajeAB'].max():.4f}")
print("\n   Estadísticas PuntajeXY:")
print(
    f"     Media: {df_clean['PuntajeXY'].mean():.4f}, Std: {df_clean['PuntajeXY'].std():.4f}"
)
print(
    f"     Min: {df_clean['PuntajeXY'].min():.4f}, Max: {df_clean['PuntajeXY'].max():.4f}"
)

print(f"\n   Tasa de Default: {df['Default'].mean() * 100:.2f}%")

# ============================================
# 2. CAPACIDAD DISCRIMINANTE
# ============================================
print("\n[2] Evaluando capacidad discriminante...")

# ROC-AUC
auc_ab = roc_auc_score(df["Default"], df["PuntajeAB"])
auc_xy = roc_auc_score(df_clean["Default"], df_clean["PuntajeXY"])

# Determinar si score más alto = más riesgo o menos riesgo
# Si AUC < 0.5, el score está invertido (mayor score = menos riesgo)
auc_ab_direction = auc_ab if auc_ab > 0.5 else 1 - auc_ab
auc_xy_direction = auc_xy if auc_xy > 0.5 else 1 - auc_xy

print(
    f"\n   ROC-AUC PuntajeAB: {auc_ab:.4f} ({'invertido' if auc_ab < 0.5 else 'normal'})"
)
print(
    f"   ROC-AUC PuntajeXY: {auc_xy:.4f} ({'invertido' if auc_xy < 0.5 else 'normal'})"
)
print(f"   ROC-AUC Ajustado AB: {auc_ab_direction:.4f}")
print(f"   ROC-AUC Ajustado XY: {auc_xy_direction:.4f}")


# KS Statistic
def ks_statistic(y_true, y_score):
    """Calcula el estadístico Kolmogorov-Smirnov"""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    ks = max(tpr - fpr)
    return ks


# Para KS necesitamos scores donde mayor = más probabilidad de default
# Si AUC < 0.5, invertimos
score_ab = -df["PuntajeAB"] if auc_ab < 0.5 else df["PuntajeAB"]
score_xy = -df_clean["PuntajeXY"] if auc_xy < 0.5 else df_clean["PuntajeXY"]

ks_ab = ks_statistic(df["Default"], score_ab)
ks_xy = ks_statistic(df_clean["Default"], score_xy)

print(f"\n   KS PuntajeAB: {ks_ab:.4f}")
print(f"   KS PuntajeXY: {ks_xy:.4f}")

# Gini Coefficient
gini_ab = 2 * auc_ab_direction - 1
gini_xy = 2 * auc_xy_direction - 1

print(f"\n   Gini PuntajeAB: {gini_ab:.4f}")
print(f"   Gini PuntajeXY: {gini_xy:.4f}")

# ============================================
# 3. CURVAS ROC COMPARATIVAS
# ============================================
print("\n[3] Generando curvas ROC...")

fig, ax = plt.subplots(figsize=(8, 6))

# Para ROC, si score invertido, usar -score
fpr_ab, tpr_ab, _ = roc_curve(
    df["Default"], -df["PuntajeAB"] if auc_ab < 0.5 else df["PuntajeAB"]
)
fpr_xy, tpr_xy, _ = roc_curve(
    df_clean["Default"],
    -df_clean["PuntajeXY"] if auc_xy < 0.5 else df_clean["PuntajeXY"],
)

ax.plot(
    fpr_ab,
    tpr_ab,
    label=f"Proveedor AB (AUC={auc_ab_direction:.4f})",
    linewidth=2,
    color="#3498db",
)
ax.plot(
    fpr_xy,
    tpr_xy,
    label=f"Proveedor XY (AUC={auc_xy_direction:.4f})",
    linewidth=2,
    color="#e74c3c",
)
ax.plot([0, 1], [0, 1], "k--", linewidth=1)
ax.set_xlabel("Tasa de Falsos Positivos", fontsize=12)
ax.set_ylabel("Tasa de Verdaderos Positivos", fontsize=12)
ax.set_title("Curva ROC - Proveedor AB vs Proveedor XY", fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Marcar punto KS
idx_ks_ab = np.argmax(tpr_ab - fpr_ab)
ax.scatter(fpr_ab[idx_ks_ab], tpr_ab[idx_ks_ab], color="#3498db", s=100, zorder=5)
idx_ks_xy = np.argmax(tpr_xy - fpr_xy)
ax.scatter(fpr_xy[idx_ks_xy], tpr_xy[idx_ks_xy], color="#e74c3c", s=100, zorder=5)

plt.tight_layout()
plt.savefig("output/figures/09_roc_competencia.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 09_roc_competencia.png")

# ============================================
# 4. ANÁLISIS POR DECILES
# ============================================
print("\n[4] Análisis por deciles...")


def analyze_by_deciles(df, score_col, target_col, label):
    """Analiza distribución de buenos/malos por deciles de score"""
    df_analysis = df[[score_col, target_col]].copy()

    # Deciles: ordenar según si mayor score = más riesgo o menos
    if roc_auc_score(df_analysis[target_col], df_analysis[score_col]) < 0.5:
        df_analysis["decile"] = pd.qcut(
            df_analysis[score_col], 10, labels=False, duplicates="drop"
        )
        # Invertir: decil 1 = mejor score (menor riesgo)
        df_analysis["decile"] = 9 - df_analysis["decile"]
    else:
        df_analysis["decile"] = pd.qcut(
            df_analysis[score_col], 10, labels=False, duplicates="drop"
        )

    decile_stats = df_analysis.groupby("decile").agg(
        {target_col: ["sum", "count", "mean"], score_col: ["mean", "min", "max"]}
    )
    decile_stats.columns = [
        "defaults",
        "total",
        "default_rate",
        "mean_score",
        "min_score",
        "max_score",
    ]
    decile_stats["good"] = decile_stats["total"] - decile_stats["defaults"]
    decile_stats["pct_good"] = decile_stats["good"] / decile_stats["total"] * 100
    decile_stats["pct_bad"] = decile_stats["defaults"] / decile_stats["total"] * 100

    return decile_stats


decile_ab = analyze_by_deciles(df, "PuntajeAB", "Default", "AB")
decile_xy = analyze_by_deciles(df_clean, "PuntajeXY", "Default", "XY")

print("\n   Deciles - Proveedor AB:")
print(decile_ab[["defaults", "total", "default_rate"]].to_string())
print("\n   Deciles - Proveedor XY:")
print(decile_xy[["defaults", "total", "default_rate"]].to_string())

# Visualización por deciles
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# AB - stacked bar
decile_ab[["pct_good", "pct_bad"]].plot(
    kind="bar", stacked=True, ax=axes[0], color=["#2ecc71", "#e74c3c"], width=0.7
)
axes[0].set_title("Proveedor AB - Distribución por Deciles", fontsize=12)
axes[0].set_xlabel("Decil (1=mejor, 10=peor)")
axes[0].set_ylabel("Porcentaje (%)")
axes[0].legend(["Buenos", "Malos"])
axes[0].grid(True, alpha=0.3, axis="y")

# XY - stacked bar
decile_xy[["pct_good", "pct_bad"]].plot(
    kind="bar", stacked=True, ax=axes[1], color=["#2ecc71", "#e74c3c"], width=0.7
)
axes[1].set_title("Proveedor XY - Distribución por Deciles", fontsize=12)
axes[1].set_xlabel("Decil (1=mejor, 10=peor)")
axes[1].set_ylabel("Porcentaje (%)")
axes[1].legend(["Buenos", "Malos"])
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("output/figures/10_deciles_competencia.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 10_deciles_competencia.png")

# Default rate por decil
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    decile_ab.index,
    decile_ab["default_rate"] * 100,
    "o-",
    linewidth=2,
    label="AB",
    color="#3498db",
)
ax.plot(
    decile_xy.index,
    decile_xy["default_rate"] * 100,
    "s-",
    linewidth=2,
    label="XY",
    color="#e74c3c",
)
ax.axhline(
    y=df["Default"].mean() * 100, color="gray", linestyle="--", label="Tasa promedio"
)
ax.set_xlabel("Decil")
ax.set_ylabel("Tasa de Default (%)")
ax.set_title("Tasa de Default por Decil - AB vs XY")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output/figures/11_default_rate_deciles.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 11_default_rate_deciles.png")

# ============================================
# 5. ESTABILIDAD DEL PUNTAJE (PSI)
# ============================================
print("\n[5] Analizando estabilidad del puntaje (PSI)...")


def calculate_psi(expected, actual, buckets=10):
    """Population Stability Index - mide cambio en distribución"""
    # Crear buckets basados en la distribución esperada
    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    breakpoints = np.unique(breakpoints)

    if len(breakpoints) < 3:
        return 0.0

    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]

    # Evitar división por cero
    expected_pct = np.maximum(expected_counts / len(expected), 0.0001)
    actual_pct = np.maximum(actual_counts / len(actual), 0.0001)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return psi


# Dividir datos en dos mitades para calcular PSI temporal
mid_date = df["Fecha Estudio"].median()
df_first = df[df["Fecha Estudio"] <= mid_date]
df_second = df[df["Fecha Estudio"] > mid_date]

psi_ab = calculate_psi(df_first["PuntajeAB"].values, df_second["PuntajeAB"].values)

df_clean_first = df_clean[df_clean["Fecha Estudio"] <= mid_date]
df_clean_second = df_clean[df_clean["Fecha Estudio"] > mid_date]

if len(df_clean_first) > 0 and len(df_clean_second) > 0:
    psi_xy = calculate_psi(
        df_clean_first["PuntajeXY"].values, df_clean_second["PuntajeXY"].values
    )
else:
    psi_xy = np.nan

print(f"\n   PSI PuntajeAB: {psi_ab:.4f}")
print(
    f"   PSI PuntajeXY: {psi_xy:.4f}"
    if not np.isnan(psi_xy)
    else "   PSI PuntajeXY: N/A (datos insuficientes)"
)


def psi_interpretation(psi):
    if psi < 0.1:
        return "Bajo - Sin cambio significativo"
    elif psi < 0.2:
        return "Moderado - Cambio leve"
    else:
        return "Alto - Cambio significativo, revisar modelo"


print(f"\n   Interpretación AB: {psi_interpretation(psi_ab)}")
if not np.isnan(psi_xy):
    print(f"   Interpretación XY: {psi_interpretation(psi_xy)}")

# Distribución de scores
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.histplot(df["PuntajeAB"], bins=50, kde=True, ax=axes[0], color="#3498db")
axes[0].set_title(f"Distribución PuntajeAB (PSI={psi_ab:.4f})")
axes[0].set_xlabel("Score")
axes[0].set_ylabel("Frecuencia")

if not np.isnan(psi_xy):
    sns.histplot(df_clean["PuntajeXY"], bins=50, kde=True, ax=axes[1], color="#e74c3c")
    axes[1].set_title(f"Distribución PuntajeXY (PSI={psi_xy:.4f})")
else:
    sns.histplot(df_clean["PuntajeXY"], bins=50, kde=True, ax=axes[1], color="#e74c3c")
    axes[1].set_title(f"Distribución PuntajeXY (PSI=N/A)")
axes[1].set_xlabel("Score")
axes[1].set_ylabel("Frecuencia")

plt.tight_layout()
plt.savefig("output/figures/12_score_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 12_score_distribution.png")

# ============================================
# 6. ANÁLISIS DE SEPARACIÓN
# ============================================
print("\n[6] Analizando separación entre buenos y malos...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# AB
for label, val in [("No Default", 0), ("Default", 1)]:
    sns.kdeplot(
        df[df.Default == val]["PuntajeAB"],
        label=label,
        ax=axes[0],
        fill=True,
        alpha=0.3,
    )
axes[0].set_title("Proveedor AB - Distribución por Default")
axes[0].set_xlabel("Score")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# XY
for label, val in [("No Default", 0), ("Default", 1)]:
    sns.kdeplot(
        df_clean[df_clean.Default == val]["PuntajeXY"],
        label=label,
        ax=axes[1],
        fill=True,
        alpha=0.3,
    )
axes[1].set_title("Proveedor XY - Distribución por Default")
axes[1].set_xlabel("Score")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("output/figures/13_separation_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 13_separation_analysis.png")

# Estadísticos de separación
print("\n   Separación de scores (Mean diff / Std):")
mean_ab_good = df[df.Default == 0]["PuntajeAB"].mean()
mean_ab_bad = df[df.Default == 1]["PuntajeAB"].mean()
std_ab = df["PuntajeAB"].std()
print(
    f"   AB: Buenos={mean_ab_good:.4f}, Malos={mean_ab_bad:.4f}, Separación={abs(mean_ab_good - mean_ab_bad) / std_ab:.4f}"
)

mean_xy_good = df_clean[df_clean.Default == 0]["PuntajeXY"].mean()
mean_xy_bad = df_clean[df_clean.Default == 1]["PuntajeXY"].mean()
std_xy = df_clean["PuntajeXY"].std()
print(
    f"   XY: Buenos={mean_xy_good:.4f}, Malos={mean_xy_bad:.4f}, Separación={abs(mean_xy_good - mean_xy_bad) / std_xy:.4f}"
)

# ============================================
# 7. COMPARACIÓN LIFT
# ============================================
print("\n[7] Análisis de Lift...")


def calculate_lift(df, score_col, target_col, n_bins=10):
    """Calcula lift por deciles"""
    df_lift = df[[score_col, target_col]].copy()
    if roc_auc_score(df_lift[target_col], df_lift[score_col]) < 0.5:
        df_lift["rank"] = pd.qcut(
            df_lift[score_col], n_bins, labels=range(n_bins, 0, -1), duplicates="drop"
        )
    else:
        df_lift["rank"] = pd.qcut(
            df_lift[score_col], n_bins, labels=range(n_bins, 0, -1), duplicates="drop"
        )

    lift = df_lift.groupby("rank").agg({target_col: ["mean", "count"]})
    lift.columns = ["default_rate", "count"]
    overall_rate = df_lift[target_col].mean()
    lift["lift"] = lift["default_rate"] / overall_rate
    lift["cumulative_pct"] = (lift["count"].cumsum() / lift["count"].sum() * 100).round(
        1
    )
    lift["cumulative_defaults"] = (
        lift["count"].cumsum() / df_lift[target_col].sum() * 100
    )

    return lift


lift_ab = calculate_lift(df, "PuntajeAB", "Default")
lift_xy = calculate_lift(df_clean, "PuntajeXY", "Default")

print("\n   Lift Proveedor AB:")
print(lift_ab.to_string())
print("\n   Lift Proveedor XY:")
print(lift_xy.to_string())

# Lift chart
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].bar(range(1, len(lift_ab) + 1), lift_ab["lift"], color="#3498db", alpha=0.8)
axes[0].axhline(y=1, color="red", linestyle="--", label="Lift=1 (aleatorio)")
axes[0].set_title("Lift por Decil - Proveedor AB")
axes[0].set_xlabel("Decil (1=mejor)")
axes[0].set_ylabel("Lift")
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis="y")

axes[1].bar(range(1, len(lift_xy) + 1), lift_xy["lift"], color="#e74c3c", alpha=0.8)
axes[1].axhline(y=1, color="red", linestyle="--", label="Lift=1 (aleatorio)")
axes[1].set_title("Lift por Decil - Proveedor XY")
axes[1].set_xlabel("Decil (1=mejor)")
axes[1].set_ylabel("Lift")
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("output/figures/14_lift_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("   -> Guardado: 14_lift_analysis.png")

# ============================================
# 8. REPORTE FINAL
# ============================================
print("\n" + "=" * 60)
print("RESUMEN COMPARATIVO - PROVEEDORES AB vs XY")
print("=" * 60)

psi_xy_str = f"{psi_xy:.4f}" if not np.isnan(psi_xy) else "N/A"

print(f"""
{"Metrica":<25} {"Proveedor AB":<20} {"Proveedor XY":<20}
{"-" * 65}
ROC-AUC:                 {auc_ab_direction:<20.4f} {auc_xy_direction:<20.4f}
KS Statistic:            {ks_ab:<20.4f} {ks_xy:<20.4f}
Gini Coefficient:        {gini_ab:<20.4f} {gini_xy:<20.4f}
PSI (Estabilidad):       {psi_ab:<20.4f} {psi_xy_str:<20}
Registros:               {len(df):<20} {len(df_clean):<20}
Tasa Default:            {df["Default"].mean() * 100:<20.2f}% {df_clean["Default"].mean() * 100:.2f}%
""")

winner = "AB" if auc_ab_direction > auc_xy_direction else "XY"
winner_auc = max(auc_ab_direction, auc_xy_direction)

print(f"\nRECOMENDACIÓN: Contratar al Proveedor {winner}")
print(f"Justificación: Mayor capacidad discriminante (AUC={winner_auc:.4f})")

# Guardar resultados
competitor_results = {
    "auc_ab": auc_ab_direction,
    "auc_xy": auc_xy_direction,
    "ks_ab": ks_ab,
    "ks_xy": ks_xy,
    "gini_ab": gini_ab,
    "gini_xy": gini_xy,
    "psi_ab": psi_ab,
    "psi_xy": psi_xy if not np.isnan(psi_xy) else None,
    "recommended_provider": winner,
    "records_ab": len(df),
    "records_xy": len(df_clean),
    "default_rate_ab": df["Default"].mean(),
    "default_rate_xy": df_clean["Default"].mean(),
    "decile_ab": decile_ab.reset_index().to_dict("records"),
    "decile_xy": decile_xy.reset_index().to_dict("records"),
    "lift_ab": lift_ab.reset_index().to_dict("records"),
    "lift_xy": lift_xy.reset_index().to_dict("records"),
}

with open("output/competitor_metrics.json", "w") as f:
    json.dump(competitor_results, f, indent=2)

print("\nParte 2 completada exitosamente!")
