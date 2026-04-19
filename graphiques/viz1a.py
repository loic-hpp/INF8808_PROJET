# -*- coding: utf-8 -*-
"""
Viz 1A — Corrélations météo ↔ consommation (lollipop).
Palette entièrement bleue : navy pour corrélations négatives,
sky-blue pour corrélations positives.
"""
import plotly.graph_objects as go
from data_utils import daily_weather, base_layout, PALETTE


VARS = {
    "Température extérieure (°C)": "temp",
    "Précipitations de neige (mm)": "neige",
    "Humidité relative (%)": "humidite",
    "Vitesse du vent (km/h)": "vent",
    "Irradiance solaire (W/m²)": "irradiance",
}


def _compute_corrs(saison):
    df = daily_weather()
    if saison and saison != "Toutes":
        df = df[df["saison"] == saison]
    pairs = [(lbl, df["conso"].corr(df[col])) for lbl, col in VARS.items()]
    pairs.sort(key=lambda x: x[1])
    return pairs


def get_figure(saison=None):
    pairs = _compute_corrs(saison)
    labels, values = zip(*pairs)

    fig = go.Figure()
    for i, (lbl, val) in enumerate(pairs):
        # Negative corr = deep navy (strong/alarming), positive = bright sky-blue
        color = PALETTE["navy"] if val < 0 else PALETTE["accent"]
        fig.add_shape(
            type="line", x0=0, x1=val, y0=i, y1=i,
            line=dict(color=color, width=4),
        )
        fig.add_trace(go.Scatter(
            x=[val], y=[i],
            mode="markers+text",
            marker=dict(color=color, size=18,
                        line=dict(color=PALETTE["primary"], width=1.5)),
            text=[f"{val:+.2f}"],
            textposition="middle right" if val >= 0 else "middle left",
            textfont=dict(size=12, color=color, family="Inter"),
            hovertemplate=f"<b>{lbl}</b><br>r = {val:.3f}<extra></extra>",
            showlegend=False,
        ))

    fig.add_vline(x=0, line_color=PALETTE["primary"], line_width=1.5)
    fig.add_vrect(x0=-0.3, x1=0.3, fillcolor=PALETTE["blue_50"],
                  opacity=0.6, layer="below", line_width=0)
    fig.add_annotation(x=0, y=-0.8, text="Corrélation faible",
                       showarrow=False,
                       font=dict(size=10, color=PALETTE["muted"]),
                       xanchor="center")

    sous_titre = (f"Saison : {saison}" if saison and saison != "Toutes"
                  else "Toutes saisons · navy = négative · sky = positive")
    fig.update_layout(**base_layout(
        "Corrélation des variables météo avec la consommation électrique",
        sous_titre, height=420,
    ))
    fig.update_layout(
        xaxis=dict(
            title="Corrélation de Pearson",
            range=[-1, 1], showgrid=True, gridcolor=PALETTE["grid"], zeroline=False,
            tickvals=[-1, -0.5, 0, 0.5, 1],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(labels))),
            ticktext=list(labels),
            showgrid=False,
        ),
        margin=dict(t=100, b=60, l=220, r=60),
    )
    return fig
