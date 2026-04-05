# -*- coding: utf-8 -*-
"""
Viz 6 — Comportement des thermostats intelligents Hilo avant/pendant/après GLD
"""

import pandas as pd
import plotly.graph_objects as go

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


def get_figure():
    df = pd.read_csv("assets/data/consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])

    event_dates = df[df["indicateur_evenement"] == 1]["date"].unique()

    records = []
    for ed in event_dates[:15]:
        ev = df[(df["date"] == ed) & (df["indicateur_evenement"] == 1)]
        if len(ev) == 0:
            continue
        start_h = ev["heure_locale"].min()
        for h_offset in range(-3, 6):
            target_h = (start_h + h_offset) % 24
            target_date = ed if h_offset >= 0 else pd.Timestamp(ed) - pd.Timedelta(days=1)
            subset = df[(df["date"] == target_date) & (df["heure_locale"] == target_h)]
            if len(subset) > 0:
                records.append({
                    "offset": h_offset,
                    "consigne": subset["temperature_consigne_moyenne"].mean(),
                    "int": subset["temperature_interieure_moyenne"].mean(),
                })

    temp_df = pd.DataFrame(records).groupby("offset").mean().reset_index()
    x_labels = [f"{o}h" for o in temp_df["offset"]]

    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    fig = go.Figure()

    fig.add_vrect(x0="-2h", x1="0h", fillcolor="#f59e0b", opacity=0.09,
                  layer="below", line_width=0,
                  annotation_text="Préchauffage<br>optionnel",
                  annotation_position="top left",
                  annotation_font=dict(color="#92400e", size=10))
    fig.add_vrect(x0="0h", x1="4h", fillcolor="#ef4444", opacity=0.09,
                  layer="below", line_width=0,
                  annotation_text="Phase de réduction<br>(défi Hilo actif)",
                  annotation_position="top right",
                  annotation_font=dict(color="#991b1b", size=10))
    for xv in ["0h", "4h"]:
        fig.add_vline(x=xv, line_dash="dash", line_color="#ef4444",
                      line_width=1.5, opacity=0.6)

    fig.add_trace(go.Scatter(
        x=x_labels,
        y=temp_df["consigne"],
        mode="lines+markers",
        name="Température de consigne (°C)",
        line=dict(color="#dc2626", width=2.5),
        marker=dict(size=7, color="#dc2626"),
        hovertemplate="<b>%{x}</b><br>Consigne : %{y:.2f}°C<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=x_labels,
        y=temp_df["int"],
        mode="lines+markers",
        name="Température intérieure mesurée (°C)",
        line=dict(color=HQ_LIGHT, width=2.5, dash="dot"),
        marker=dict(size=7, symbol="square", color=HQ_LIGHT),
        hovertemplate="<b>%{x}</b><br>Intérieure : %{y:.2f}°C<extra></extra>",
    ))

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=90, b=70, l=70, r=30),
        title=dict(
            text="Comportement des thermostats intelligents (Hilo)<br>"
                 "<sup>avant, pendant et après un événement GLD</sup>",
            font=dict(size=16, color=HQ_BLUE),
        ),
        xaxis=dict(
            title="Heures par rapport au début de l'événement GLD",
            showgrid=True, gridcolor=GRID, zeroline=False,
        ),
        yaxis=dict(
            title="Température (°C)", showgrid=True,
            gridcolor=GRID, zeroline=False,
            range=[temp_df["consigne"].min() - 2,
                   max(temp_df["consigne"].max(), temp_df["int"].max()) * 1.1]
        ),
        legend=dict(
            x=0.01, y=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#ddd", borderwidth=1,
        ),
        height=500,
    )

    return fig
