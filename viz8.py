# -*- coding: utf-8 -*-
"""
Viz 8 — Profils de consommation selon les postes A, B et C (barres groupées)
"""

import pandas as pd
import plotly.graph_objects as go

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"
HQ_GREEN = "#78BE20"


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

    SEASONS_ORD = ["Hiver", "Printemps", "Été", "Automne"]
    COLORS = {"A": HQ_BLUE, "B": HQ_GREEN, "C": HQ_LIGHT}
    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    agg = df.groupby(["saison", "poste"])["energie_totale_consommee"].mean().unstack()
    agg = agg.reindex(SEASONS_ORD)

    fig = go.Figure()

    for poste in ["A", "B", "C"]:
        vals = agg[poste].values
        fig.add_trace(go.Bar(
            name=f"Poste {poste}",
            x=SEASONS_ORD,
            y=vals,
            marker_color=COLORS[poste],
            marker_line=dict(color="white", width=0.5),
            text=[f"{v:.0f}" for v in vals],
            textposition="outside",
            textfont=dict(size=11, color=COLORS[poste]),
            hovertemplate=(
                f"<b>Poste {poste}</b><br>"
                "Saison : %{x}<br>"
                "Conso moy. : %{y:.0f} kWh/h<extra></extra>"
            ),
        ))

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=90, b=70, l=80, r=30),
        title=dict(
            text="Profils de consommation selon les postes A, B et C",
            font=dict(size=16, color=HQ_BLUE),
        ),
        barmode="group",
        bargap=0.20,
        bargroupgap=0.05,
        xaxis=dict(
            title="Saison",
            showgrid=False, zeroline=False,
        ),
        yaxis=dict(
            title="Consommation moyenne (kWh/heure)",
            showgrid=True, gridcolor=GRID, zeroline=False,
        ),
        legend=dict(
            x=0.98, y=0.98, xanchor="right",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#ddd", borderwidth=1,
        ),
        annotations=[dict(
            x=0.5, y=1.05, xref="paper", yref="paper",
            text="Consommation horaire moyenne par saison \u00b7 2022\u20132024",
            showarrow=False, font=dict(size=11, color="#888780"),
        )],
        height=500,
    )

    return fig
