# -*- coding: utf-8 -*-
"""
Viz 3 — Graphiques polaires (rose charts) : consommation horaire par saison
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


def get_figure():
    df = pd.read_csv("consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month

    def get_season(m):
        if m in [12, 1, 2]:
            return "Hiver"
        elif m in [3, 4, 5]:
            return "Printemps"
        elif m in [6, 7, 8]:
            return "Été"
        else:
            return "Automne"

    df["saison"] = df["month"].apply(get_season)
    hourly = df.groupby(["saison", "heure_locale"])["energie_totale_consommee"].mean().reset_index()

    SEASONS_ORD = ["Hiver", "Printemps", "Été", "Automne"]

    global_max = max(
        hourly[hourly["saison"] == s]["energie_totale_consommee"].max()
        for s in SEASONS_ORD
    ) * 1.08

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "polar"}, {"type": "polar"}],
               [{"type": "polar"}, {"type": "polar"}]],
        subplot_titles=SEASONS_ORD,
        horizontal_spacing=0.05,
        vertical_spacing=0.12,
    )

    for ann in fig.layout.annotations:
        if ann.text in SEASONS_ORD:
            ann.y += 0.03
            ann.font.size = 15

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    positions_paper = {
        "Hiver": (0.22, 0.78),
        "Printemps": (0.78, 0.78),
        "Été": (0.22, 0.22),
        "Automne": (0.78, 0.22),
    }

    for (row, col), saison in zip(positions, SEASONS_ORD):
        data = hourly[hourly["saison"] == saison].sort_values("heure_locale")
        angles = (data["heure_locale"] * 360 / 24).tolist()
        values = data["energie_totale_consommee"].tolist()
        hours = data["heure_locale"].tolist()
        avg = data["energie_totale_consommee"].mean()

        fig.add_trace(go.Barpolar(
            r=values,
            theta=angles,
            width=[360 / 24] * len(values),
            marker=dict(
                color=HQ_LIGHT,
                opacity=0.82,
                line=dict(color="white", width=0.6),
            ),
            hovertemplate=(
                "<b>%{customdata}h</b><br>"
                f"{saison}<br>"
                "Conso : %{r:.0f} kWh<extra></extra>"
            ),
            customdata=hours,
            name=saison,
            showlegend=False,
        ), row=row, col=col)

        x_paper, y_paper = positions_paper[saison]
        fig.add_annotation(
            text=f"moy.<br>{avg:.0f} kWh",
            x=x_paper,
            y=y_paper,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=9, color=HQ_BLUE),
            align="center",
        )

    polar_config = dict(
        radialaxis=dict(
            visible=True,
            range=[0, global_max],
            tickfont=dict(size=12, color=HQ_BLUE, family="Arial Black"),
            gridcolor="rgba(0,85,127,0.3)",
            gridwidth=2,
        ),
        angularaxis=dict(
            tickmode="array",
            tickvals=[h * 360 / 24 for h in range(0, 24, 1)],
            ticktext=[f"{h}h" if h % 3 == 0 else "" for h in range(24)],
            direction="clockwise",
            rotation=90,
            gridcolor="rgba(0,85,127,0.3)",
            tickfont=dict(size=11),
        ),
        bgcolor="#e6f2f8",
    )

    for i in range(1, 5):
        key = "polar" if i == 1 else f"polar{i}"
        fig.update_layout(**{key: polar_config})

    fig.update_layout(
        title=dict(
            text="Consommation électrique moyenne par heure selon la saison",
            font=dict(size=16, color=HQ_BLUE),
        ),
        paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        margin=dict(t=100, b=40, l=40, r=40),
        annotations=[a for a in fig.layout.annotations] + [dict(
            x=0.5, y=1.04, xref="paper", yref="paper",
            text="Tous postes confondus \u00b7 moyenne 2022\u20132024 \u00b7 kWh/heure",
            showarrow=False, font=dict(size=11, color="#888780"),
        )],
        height=800,
    )

    return fig
