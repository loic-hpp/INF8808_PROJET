# -*- coding: utf-8 -*-
"""
Viz 2 — Heatmap calendrier : consommation électrique par jour et mois
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

HQ_BLUE = "#00557F"


def get_figure():
    df = pd.read_csv("consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["dow"] = df["date"].dt.dayofweek

    daily = df.groupby("date").agg(
        conso=("energie_totale_consommee", "sum"),
        ferie=("indicateur_jour_ferie", "max"),
    ).reset_index()
    daily["conso_mwh"] = daily["conso"] / 1000
    daily["month"] = daily["date"].dt.month
    daily["dow"] = daily["date"].dt.dayofweek

    MONTHS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                 "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    DAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

    pivot = daily.groupby(["dow", "month"])["conso_mwh"].mean().unstack()
    pivot = pivot.reindex(index=range(7), columns=range(1, 13))

    wd_avg = pivot.loc[0:4].mean(axis=0)
    we_avg = pivot.loc[5:6].mean(axis=0)
    ferie_avg = daily[daily["ferie"] == True].groupby("month")["conso_mwh"].mean()
    ferie_row = pd.Series([ferie_avg.get(m, None) for m in range(1, 13)])
    all_avg = pivot.mean(axis=0)

    z_main = pivot.values
    z_summary = np.array([wd_avg.values, we_avg.values,
                          ferie_row.values.astype(float), all_avg.values])
    z_full = np.vstack([z_main, [[np.nan] * 12], z_summary])

    vmin = float(np.nanmin(z_main))
    vmax = float(np.nanmax(z_main))

    def fmt(v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "—"
        return f"{v:.1f}"

    text_full = []
    for row in z_full:
        text_full.append([fmt(v) for v in row])

    ylabels = DAYS_FR + [""] + ["\u2300 Ouvrables", "\u2300 Weekend",
                                 "\u2300 Fériés", "\u2300 Mensuelle"]

    custom = []
    for r in range(7):
        row = []
        for c in range(12):
            v = pivot.iloc[r, c]
            row.append(f"{DAYS_FR[r]} \u00b7 {MONTHS_FR[c]}<br>Conso moy. : {fmt(v)} MWh")
        custom.append(row)
    custom.append([""] * 12)
    summ_labels = ["\u2300 Ouvrables", "\u2300 Weekend", "\u2300 Fériés", "\u2300 Mensuelle"]
    summ_data = [wd_avg.values, we_avg.values, ferie_row.values, all_avg.values]
    for s, label in enumerate(summ_labels):
        row = []
        for c in range(12):
            v = summ_data[s][c]
            row.append(f"{label} \u00b7 {MONTHS_FR[c]}<br>{fmt(v)} MWh")
        custom.append(row)

    fig = go.Figure(go.Heatmap(
        z=z_full,
        x=MONTHS_FR,
        y=ylabels,
        colorscale=[
            [0.00, "#e6f2f8"],
            [0.15, "#b3d9f0"],
            [0.30, "#66b2d6"],
            [0.50, "#009FE3"],
            [0.70, "#007CB0"],
            [0.85, "#00557F"],
            [1.00, "#003050"],
        ],
        zmin=vmin,
        zmax=vmax,
        text=text_full,
        texttemplate="%{text}",
        textfont=dict(size=11),
        customdata=custom,
        hovertemplate="%{customdata}<extra></extra>",
        colorbar=dict(title="MWh", thickness=15),
        xgap=3,
        ygap=3,
    ))

    fig.add_shape(
        type="line",
        x0=-0.5, x1=11.5, y0=7.5, y1=7.5,
        line=dict(color="#aaaaaa", width=1.5, dash="dot"),
    )

    fig.update_layout(
        font=dict(family="Arial", size=12, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        margin=dict(t=80, b=80, l=110, r=30),
        title=dict(
            text="Consommation électrique moyenne par jour et mois",
            font=dict(size=16, color=HQ_BLUE),
        ),
        xaxis=dict(title="", showgrid=False, zeroline=False),
        yaxis=dict(title="", showgrid=False, zeroline=False, autorange="reversed"),
        annotations=[dict(
            x=0.5, y=1.04, xref="paper", yref="paper",
            text="Moyenne 2022\u20132024 \u00b7 tous postes \u00b7 kWh/jour",
            showarrow=False, font=dict(size=11, color="#888780"),
        )],
        height=580,
    )

    return fig
