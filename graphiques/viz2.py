# -*- coding: utf-8 -*-
"""
Viz 2 — Heatmap calendrier jour × mois (palette 100% bleue).

Couleur du texte adaptative : noir sur les cases pâles, blanc sur les cases
foncées, calculée par cellule via une luminance pondérée. Plotly ne permettant
pas de couleur de texte par cellule sur un Heatmap, le texte est dessiné via
des annotations individuelles.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data_utils import load_data, base_layout, MONTHS_FR, DAYS_FR, PALETTE


# ─────────────────────────────────────────────────────────────
# Helpers — couleur de texte adaptative
# ─────────────────────────────────────────────────────────────
def _hex_to_rgb(hex_str: str):
    """Convert '#RRGGBB' to (r, g, b) ints."""
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _interp_color(stops, t):
    """
    Interpolation linéaire dans une colorscale Plotly.
    stops = [(pos, '#RRGGBB'), …] avec pos ∈ [0, 1] trié.
    t = position normalisée ∈ [0, 1].
    Retourne un tuple RGB.
    """
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            r0, g0, b0 = _hex_to_rgb(c0)
            r1, g1, b1 = _hex_to_rgb(c1)
            f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            return (
                int(r0 + (r1 - r0) * f),
                int(g0 + (g1 - g0) * f),
                int(b0 + (b1 - b0) * f),
            )
    # Fallback: end stop
    return _hex_to_rgb(stops[-1][1])


def _luminance(rgb):
    """Luminance perçue (formule W3C) — utilisée pour décider noir/blanc."""
    r, g, b = [c / 255.0 for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _adaptive_text_color(value, vmin, vmax, stops, threshold=0.55):
    """
    Retourne la couleur de texte (noir ou blanc) la plus lisible sur la
    couleur de cellule correspondante. `threshold` ajuste le point de bascule
    (plus bas = bascule plus tôt vers le blanc).
    """
    if pd.isna(value):
        return "#374151"   # gris-ardoise pour les NaN sur fond blanc
    if vmax == vmin:
        t = 0.5
    else:
        t = (value - vmin) / (vmax - vmin)
    rgb = _interp_color(stops, t)
    return "#FFFFFF" if _luminance(rgb) < threshold else "#0F172A"


# ─────────────────────────────────────────────────────────────
# Aggregation
# ─────────────────────────────────────────────────────────────
def _aggregate():
    df = load_data()
    daily = df.groupby("date").agg(
        conso=("energie_totale_consommee", "sum"),
        ferie=("indicateur_jour_ferie", "max"),
    ).reset_index()
    daily["conso_mwh"] = daily["conso"] / 1000
    daily["month"] = daily["date"].dt.month
    daily["dow"] = daily["date"].dt.dayofweek

    pivot = daily.groupby(["dow", "month"])["conso_mwh"].mean().unstack()
    pivot = pivot.reindex(index=range(7), columns=range(1, 13))
    wd_avg = pivot.loc[0:4].mean(axis=0)
    we_avg = pivot.loc[5:6].mean(axis=0)
    ferie_avg = daily[daily["ferie"] == 1].groupby("month")["conso_mwh"].mean()
    ferie_row = pd.Series([ferie_avg.get(m, np.nan) for m in range(1, 13)])
    all_avg = pivot.mean(axis=0)
    return pivot, wd_avg, we_avg, ferie_row, all_avg


# ─────────────────────────────────────────────────────────────
# Figure
# ─────────────────────────────────────────────────────────────
def get_figure(mode="absolu"):
    pivot, wd_avg, we_avg, ferie_row, all_avg = _aggregate()

    if mode == "ecart":
        mean_year = pivot.stack().mean()
        z_main = (pivot.values - mean_year) / mean_year * 100
        z_summary = np.array([
            (wd_avg.values - mean_year) / mean_year * 100,
            (we_avg.values - mean_year) / mean_year * 100,
            (ferie_row.values - mean_year) / mean_year * 100,
            (all_avg.values - mean_year) / mean_year * 100,
        ])
        unit = "%"
        colorbar_title = "Écart vs moy (%)"
        fmt = lambda v: "—" if pd.isna(v) else f"{v:+.0f}%"
        colorscale = [
            (0.00, "#93C5FD"),   # bleu ciel pâle (très en-dessous de la moy)
            (0.30, "#BFDBFE"),
            (0.50, "#F1F5F9"),   # quasi-blanc neutre
            (0.70, "#2563EB"),
            (1.00, "#0B3D66"),   # navy profond (au-dessus de la moy)
        ]
        vabs = max(abs(np.nanmin(z_main)), abs(np.nanmax(z_main)))
        vmin, vmax = -vabs, vabs
    else:
        z_main = pivot.values
        z_summary = np.array([wd_avg.values, we_avg.values,
                              ferie_row.values.astype(float), all_avg.values])
        unit = " MWh"
        colorbar_title = "MWh / jour"
        fmt = lambda v: "—" if pd.isna(v) else f"{v:.1f}"
        colorscale = [
            (0.00, "#EFF6FF"),
            (0.15, "#DBEAFE"),
            (0.35, "#BFDBFE"),
            (0.55, "#60A5FA"),
            (0.75, "#2563EB"),
            (0.90, "#1D4ED8"),
            (1.00, "#0B3D66"),
        ]
        vmin = float(np.nanmin(z_main))
        vmax = float(np.nanmax(z_main))

    z_full = np.vstack([z_main, [[np.nan] * 12], z_summary])

    ylabels = (DAYS_FR + [""]
               + ["⌀ Ouvrables", "⌀ Weekend", "⌀ Fériés", "⌀ Mensuelle"])

    # ── Hover (customdata) ──
    custom = []
    for r in range(7):
        custom.append([f"<b>{DAYS_FR[r]} · {MONTHS_FR[c]}</b><br>Conso : {fmt(pivot.iloc[r, c])}{unit}"
                       for c in range(12)])
    custom.append([""] * 12)
    summ_labels = ["⌀ Ouvrables", "⌀ Weekend", "⌀ Fériés", "⌀ Mensuelle"]
    summ_data = [wd_avg.values, we_avg.values, ferie_row.values, all_avg.values]
    for s_idx, lbl in enumerate(summ_labels):
        custom.append([f"<b>{lbl} · {MONTHS_FR[c]}</b><br>{fmt(summ_data[s_idx][c])}{unit}"
                       for c in range(12)])

    # ── Heatmap (sans texte intégré — on dessine le texte par-dessus) ──
    fig = go.Figure(go.Heatmap(
        z=z_full,
        x=MONTHS_FR,
        y=ylabels,
        colorscale=[[p, c] for p, c in colorscale],
        zmin=vmin, zmax=vmax,
        customdata=custom,
        hovertemplate="%{customdata}<extra></extra>",
        colorbar=dict(title=colorbar_title, thickness=15, tickfont=dict(size=11)),
        xgap=3, ygap=3,
        showscale=True,
    ))

    # ── Annotations texte avec couleur ADAPTATIVE par cellule ──
    # Pour chaque case, on calcule la luminance de la couleur de fond
    # (interpolée depuis la colorscale) et on choisit noir ou blanc.
    n_rows, n_cols = z_full.shape
    for r in range(n_rows):
        for c in range(n_cols):
            v = z_full[r, c]
            if pd.isna(v):
                continue
            text_color = _adaptive_text_color(v, vmin, vmax, colorscale)
            fig.add_annotation(
                x=MONTHS_FR[c], y=ylabels[r],
                text=fmt(v),
                showarrow=False,
                font=dict(size=11, color=text_color, family="Inter, Arial"),
                xref="x", yref="y",
            )

    # Séparateur entre la grille hebdomadaire et les lignes de résumé
    fig.add_shape(
        type="line", x0=-0.5, x1=11.5, y0=7.5, y1=7.5,
        line=dict(color=PALETTE["muted"], width=1.5, dash="dot"),
    )

    fig.update_layout(**base_layout(
        "Consommation électrique moyenne par jour et mois",
        "Moyenne 2022–2024 · tous postes · "
        + ("% d'écart à la moyenne" if mode == "ecart" else "MWh/jour"),
        height=580,
    ))
    fig.update_layout(
        xaxis=dict(title="", showgrid=False, zeroline=False, side="top"),
        yaxis=dict(title="", showgrid=False, zeroline=False, autorange="reversed"),
        margin=dict(t=110, b=40, l=120, r=30),
    )
    return fig