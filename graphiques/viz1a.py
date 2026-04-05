# -*- coding: utf-8 -*-
"""
Viz 1A — Corrélation des variables météo avec la consommation (Lollipop)
"""

import pandas as pd
import plotly.graph_objects as go

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


def get_figure():
    df = pd.read_csv("assets/data/consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])

    daily = df.groupby("date").agg(
        conso=("energie_totale_consommee", "sum"),
        temp=("temperature_exterieure_moyenne", "mean"),
        vent=("vitesse_vent_moyenne", "mean"),
        neige=("precipitations_neige_moyenne", "mean"),
        humidite=("humidite_relative_moyenne", "mean"),
    ).reset_index()

    variables = {
        "Température extérieure": "temp",
        "Précipitations / neige": "neige",
        "Humidité relative": "humidite",
        "Vitesse du vent": "vent",
    }

    corrs = {name: daily["conso"].corr(daily[col]) for name, col in variables.items()}
    corrs_sorted = dict(sorted(corrs.items(), key=lambda x: x[1]))

    labels = list(corrs_sorted.keys())
    values = list(corrs_sorted.values())
    colors = ["#dc2626" if v < 0 else "#16a34a" for v in values]

    BG = "#fafafa"
    GRID = "rgba(200,200,200,0.4)"

    fig = go.Figure()

    for i, (label, val, col) in enumerate(zip(labels, values, colors)):
        fig.add_shape(
            type="line",
            x0=0, x1=val, y0=i, y1=i,
            line=dict(color=col, width=3),
        )
        fig.add_trace(go.Scatter(
            x=[val], y=[i],
            mode="markers+text",
            marker=dict(color=col, size=14, line=dict(color="#374151", width=1)),
            text=[f"{'+' if val >= 0 else ''}{val:.2f}"],
            textposition="middle right" if val >= 0 else "middle left",
            textfont=dict(size=12, color=col),
            showlegend=False,
            hovertemplate=f"<b>{label}</b><br>r = {val:.3f}<extra></extra>",
        ))

    fig.add_vline(x=0, line_color="#374151", line_width=1.5)

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=90, b=60, l=200, r=60),
        title=dict(
            text="Corrélation des variables météorologiques avec la consommation électrique",
            font=dict(size=16, color=HQ_BLUE),
        ),
        xaxis=dict(
            title="Corrélation de Pearson avec energie_totale_consommee",
            showgrid=True, gridcolor=GRID, zeroline=False,
            range=[min(values) * 1.25, max(values) * 1.4],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(labels))),
            ticktext=labels,
            showgrid=False,
        ),
        annotations=[dict(
            x=0.5, y=1.06, xref="paper", yref="paper",
            text="Rouge = corrélation négative   |   Vert = corrélation positive",
            showarrow=False,
            font=dict(size=11, color="#888780"),
        )],
        height=400,
    )

    return fig
