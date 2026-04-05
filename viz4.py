# -*- coding: utf-8 -*-
"""
Viz 4 — Profil de consommation avant, pendant et après un événement GLD
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


def get_figure():
    df = pd.read_csv("consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["is_winter"] = df["month"].isin([12, 1, 2, 3])

    df_ref = df[(df["indicateur_evenement"] == 0) &
                (df["pre_post_indicateur_evenement"] == 0) &
                df["is_winter"]]
    ref_baseline = df_ref.groupby(["poste", "heure_locale"])["energie_totale_consommee"].mean()

    event_dates = df[df["indicateur_evenement"] == 1]["date"].unique()

    hilo_records, ref_records = [], []
    for ed in event_dates:
        ev = df[(df["date"] == ed) &
                (df["indicateur_evenement"] == 1) &
                (df["heure_locale"] != 16)]
        if len(ev) == 0:
            continue
        start_h = ev["heure_locale"].min()
        for h_offset in range(-4, 7):
            target_h = (start_h + h_offset) % 24
            target_date = ed if h_offset >= 0 else pd.Timestamp(ed) - pd.Timedelta(days=1)
            subset = df[(df["date"] == target_date) & (df["heure_locale"] == target_h)]
            if len(subset) > 0:
                hilo_records.append({"offset": h_offset,
                                     "conso": subset["energie_totale_consommee"].sum()})
            ref_h = df_ref[df_ref["heure_locale"] == target_h]
            by_date = ref_h.groupby("date")["energie_totale_consommee"].sum()
            if len(by_date) > 0:
                ref_records.append({"offset": h_offset, "conso": by_date.mean()})

    hilo_curve = pd.DataFrame(hilo_records).groupby("offset")["conso"].mean()
    ref_curve = pd.DataFrame(ref_records).groupby("offset")["conso"].mean()

    offsets = list(range(-4, 7))
    x_labels = [f"{o}h" for o in offsets]
    h_vals = [float(hilo_curve.get(o, np.nan)) for o in offsets]
    r_vals = [float(ref_curve.get(o, np.nan)) for o in offsets]

    event_idx = [i for i, o in enumerate(offsets) if 0 <= o <= 3]
    h_event = np.nanmean([h_vals[i] for i in event_idx])
    r_event = np.nanmean([r_vals[i] for i in event_idx])
    reduction = (r_event - h_event) / r_event * 100
    rebound = (h_vals[8] - r_vals[8]) / r_vals[8] * 100 if not np.isnan(r_vals[8]) else 0

    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    fig = go.Figure()

    fig.add_vrect(x0="-2h", x1="0h", fillcolor="#f59e0b", opacity=0.10,
                  layer="below", line_width=0,
                  annotation_text="Préchauffage<br>optionnel",
                  annotation_position="top left",
                  annotation_font=dict(color="#92400e", size=11))
    fig.add_vrect(x0="0h", x1="4h", fillcolor="#ef4444", opacity=0.10,
                  layer="below", line_width=0,
                  annotation_text="Défi GLD<br>actif",
                  annotation_position="top right",
                  annotation_font=dict(color="#991b1b", size=11))
    for xv in ["0h", "4h"]:
        fig.add_vline(x=xv, line_dash="dash", line_color="#ef4444",
                      line_width=1.5, opacity=0.7)

    fig.add_trace(go.Scatter(
        x=x_labels, y=r_vals,
        fill=None, mode="lines",
        line_color="rgba(0,0,0,0)",
        showlegend=False, hoverinfo="skip",
    ))
    fill_y = [h if (not np.isnan(h) and not np.isnan(r) and r > h) else np.nan
              for h, r in zip(h_vals, r_vals)]
    fig.add_trace(go.Scatter(
        x=x_labels, y=fill_y,
        fill="tonexty",
        fillcolor="rgba(22,163,74,0.15)",
        mode="lines",
        line_color="rgba(0,0,0,0)",
        showlegend=False, hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter(
        x=x_labels, y=r_vals,
        mode="lines+markers",
        name="Référence — hiver sans GLD",
        line=dict(color="#6b7280", width=2.5, dash="dot"),
        marker=dict(size=7, color="#6b7280"),
        hovertemplate="<b>%{x}</b><br>Référence : %{y:.0f} kWh<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=x_labels, y=h_vals,
        mode="lines+markers",
        name="Clients Hilo — tous postes confondus",
        line=dict(color=HQ_LIGHT, width=2.8),
        marker=dict(size=8, color=HQ_LIGHT),
        hovertemplate="<b>%{x}</b><br>Hilo : %{y:.0f} kWh<extra></extra>",
    ))

    fig.add_annotation(
        x="2h", y=h_vals[6],
        text=f"\u2193 {reduction:.0f}%<br>pendant le défi",
        showarrow=True, arrowhead=2, ax=60, ay=-50,
        font=dict(color="#15803d", size=11),
        bgcolor="#dcfce7", bordercolor="#86efac",
    )
    fig.add_annotation(
        x="4h", y=h_vals[8],
        text=f"Effet rebond<br>(+{rebound:.0f}% vs référence)",
        showarrow=True, arrowhead=2, ax=70, ay=-40,
        font=dict(color="#dc2626", size=11),
        bgcolor="#fee2e2", bordercolor="#fca5a5",
    )

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=80, b=70, l=80, r=40),
        title=dict(
            text="Profil de consommation avant, pendant et après un événement GLD",
            font=dict(size=16, color=HQ_BLUE),
        ),
        xaxis=dict(title="Heures par rapport au début de l'événement GLD",
                   showgrid=True, gridcolor=GRID, zeroline=False),
        yaxis=dict(
            title="Consommation totale (kWh) — tous postes",
            showgrid=True,
            gridcolor=GRID,
            zeroline=False,
            range=[0, max(
                max([v for v in h_vals if not np.isnan(v)]),
                max([v for v in r_vals if not np.isnan(v)])
            ) * 1.1]
        ),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#ddd", borderwidth=1),
        height=500,
    )

    return fig
