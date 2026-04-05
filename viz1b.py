# -*- coding: utf-8 -*-
"""
Viz 1B — Nuages de points 2×2 : influence météo sur la consommation
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


def get_figure():
    df = pd.read_csv("consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])

    daily = df.groupby("date").agg(
        conso=("energie_totale_consommee", "sum"),
        temp=("temperature_exterieure_moyenne", "mean"),
        vent=("vitesse_vent_moyenne", "mean"),
        neige=("precipitations_neige_moyenne", "mean"),
        humidite=("humidite_relative_moyenne", "mean"),
    ).reset_index()

    daily["conso_mwh"] = daily["conso"] / 1000
    no_snow_mean = daily[daily["neige"] == 0]["conso_mwh"].mean()

    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Température vs Consommation",
            "Vent vs Consommation",
            "Neige vs Consommation",
            "Humidité vs Consommation",
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    scatter_kw = dict(
        mode="markers",
        marker=dict(color=HQ_LIGHT, size=6, opacity=0.6,
                    line=dict(color=HQ_BLUE, width=0.3)),
        showlegend=False,
    )

    fig.add_trace(go.Scatter(
        x=daily["temp"], y=daily["conso_mwh"],
        customdata=daily["date"].dt.strftime("%Y-%m-%d"),
        hovertemplate="Date: %{customdata}<br>Température: %{x:.1f}°C<br>Conso: %{y:.1f} MWh<extra></extra>",
        **scatter_kw,
    ), row=1, col=1)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1, row=1, col=1)

    fig.add_trace(go.Scatter(
        x=daily["vent"], y=daily["conso_mwh"],
        customdata=daily["date"].dt.strftime("%Y-%m-%d"),
        hovertemplate="Date: %{customdata}<br>Vent: %{x:.1f} km/h<br>Conso: %{y:.1f} MWh<extra></extra>",
        **scatter_kw,
    ), row=1, col=2)

    snow = daily[daily["neige"] > 0]
    fig.add_trace(go.Scatter(
        x=snow["neige"], y=snow["conso_mwh"],
        customdata=snow["date"].dt.strftime("%Y-%m-%d"),
        hovertemplate="Date: %{customdata}<br>Neige: %{x:.1f} mm<br>Conso: %{y:.1f} MWh<extra></extra>",
        **scatter_kw,
    ), row=2, col=1)
    fig.add_hline(
        y=no_snow_mean,
        line_dash="dash", line_color="gray", line_width=1.5,
        annotation_text=f"Moy. sans neige ({no_snow_mean:.1f} MWh)",
        annotation_position="bottom right",
        row=2, col=1,
    )

    fig.add_trace(go.Scatter(
        x=daily["humidite"], y=daily["conso_mwh"],
        customdata=daily["date"].dt.strftime("%Y-%m-%d"),
        hovertemplate="Date: %{customdata}<br>Humidité: %{x:.0f}%<br>Conso: %{y:.1f} MWh<extra></extra>",
        **scatter_kw,
    ), row=2, col=2)

    fig.update_layout(
        title=dict(
            text="Influence des conditions météorologiques sur la consommation électrique",
            font=dict(size=16, color=HQ_BLUE),
        ),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        font=dict(family="Arial", size=12),
        showlegend=False,
        height=700,
        margin=dict(t=80, b=60, l=70, r=30),
    )

    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                     title_text="Consommation totale journalière (MWh)")
    fig.update_xaxes(title_text="Température extérieure (°C)", row=1, col=1)
    fig.update_xaxes(title_text="Vitesse du vent moyenne (km/h)", row=1, col=2)
    fig.update_xaxes(title_text="Précipitations de neige (mm)", row=2, col=1)
    fig.update_xaxes(title_text="Humidité relative moyenne (%)", row=2, col=2)

    return fig
