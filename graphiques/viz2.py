# -*- coding: utf-8 -*-
"""
Viz 2 — Heatmap calendrier jour × mois (palette 100% bleue).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data_utils import load_data, base_layout, MONTHS_FR, DAYS_FR, PALETTE


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
        # Diverging scale — BLUE only. Sky-blue for below-average,
        # light neutral slate at midpoint, deep navy for above-average.
        colorscale = [
            [0.00, "#93C5FD"],   # light sky blue (well below avg)
            [0.30, "#BFDBFE"],
            [0.50, "#F1F5F9"],   # near-white neutral
            [0.70, "#2563EB"],
            [1.00, "#0B3D66"],   # deep navy (well above avg)
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
        # Sequential monochromatic blue ramp — low conso = pale blue,
        # high conso = deep HQ navy. Single-hue, very readable.
        colorscale = [
            [0.00, "#EFF6FF"],
            [0.15, "#DBEAFE"],
            [0.35, "#BFDBFE"],
            [0.55, "#60A5FA"],
            [0.75, "#2563EB"],
            [0.90, "#1D4ED8"],
            [1.00, "#0B3D66"],
        ]
        vmin = float(np.nanmin(z_main))
        vmax = float(np.nanmax(z_main))

    z_full = np.vstack([z_main, [[np.nan] * 12], z_summary])
    text = [[fmt(v) for v in row] for row in z_full]
    ylabels = DAYS_FR + [""] + ["⌀ Ouvrables", "⌀ Weekend", "⌀ Fériés", "⌀ Mensuelle"]

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

    fig = go.Figure(go.Heatmap(
        z=z_full, x=MONTHS_FR, y=ylabels,
        colorscale=colorscale, zmin=vmin, zmax=vmax,
        text=text, texttemplate="%{text}",
        textfont=dict(size=11, color=PALETTE["primary"]),
        customdata=custom, hovertemplate="%{customdata}<extra></extra>",
        colorbar=dict(title=colorbar_title, thickness=15, tickfont=dict(size=11)),
        xgap=3, ygap=3,
    ))
    fig.add_shape(type="line", x0=-0.5, x1=11.5, y0=7.5, y1=7.5,
                  line=dict(color=PALETTE["muted"], width=1.5, dash="dot"))

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
