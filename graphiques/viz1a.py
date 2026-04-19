# -*- coding: utf-8 -*-
"""
Viz 1A — Corrélations météo ↔ consommation (lollipop)
Interaction: filtre par saison (all / Hiver / Printemps / Été / Automne)
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


def _compute_corrs(saison: str | None):
    df = daily_weather()
    if saison and saison != "Toutes":
        df = df[df["saison"] == saison]
    pairs = [(lbl, df["conso"].corr(df[col])) for lbl, col in VARS.items()]
    pairs.sort(key=lambda x: x[1])
    return pairs


def get_figure(saison: str | None = None):
    pairs = _compute_corrs(saison)
    labels, values = zip(*pairs)

    fig = go.Figure()
    for i, (lbl, val) in enumerate(pairs):
        color = PALETTE["hot"] if val < 0 else PALETTE["cool"]
        # stick
        fig.add_shape(
            type="line", x0=0, x1=val, y0=i, y1=i,
            line=dict(color=color, width=4),
        )
        # lollipop head + value label
        fig.add_trace(go.Scatter(
            x=[val], y=[i],
            mode="markers+text",
            marker=dict(color=color, size=18,
                        line=dict(color="#1f2937", width=1.5)),
            text=[f"{val:+.2f}"],
            textposition="middle right" if val >= 0 else "middle left",
            textfont=dict(size=12, color=color, family="Inter"),
            hovertemplate=f"<b>{lbl}</b><br>r = {val:.3f}<extra></extra>",
            showlegend=False,
        ))

    fig.add_vline(x=0, line_color="#374151", line_width=1.5)
    # Reference bands for interpretation
    fig.add_vrect(x0=-0.3, x1=0.3, fillcolor="#f3f4f6",
                  opacity=0.5, layer="below", line_width=0)
    fig.add_annotation(x=0, y=-0.8, text="Corrélation faible",
                       showarrow=False, font=dict(size=10, color="#9ca3af"),
                       xanchor="center")

    sous_titre = f"Saison : {saison}" if saison and saison != "Toutes" else "Toutes saisons · rouge = négative · vert = positive"
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
        margin=dict(t=90, b=60, l=220, r=60),
    )
    return fig
