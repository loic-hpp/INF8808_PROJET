# -*- coding: utf-8 -*-
"""
Viz 1B — Nuages de points 2×2 : météo ↔ consommation.
Palette 100% bleue : quatre saisons sont distinguées par intensité,
du bleu marine (Hiver) au bleu pâle (Été), en passant par cyan (Printemps)
et slate (Automne).
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_utils import daily_weather, base_layout, PALETTE


# Saisons dans la famille bleu uniquement, distinguées par luminance et ton
SEASON_COLORS = {
    "Hiver":     "#0B3D66",   # navy (froid / dense)
    "Printemps": "#38BDF8",   # sky-blue (frais / vif)
    "Été":       "#93C5FD",   # pâle (léger / aéré)
    "Automne":   "#64748B",   # slate (muted / transition)
}
SEASON_ORDER = ["Hiver", "Printemps", "Été", "Automne"]


def _add_trend(fig, x, y, row, col, color=None):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5:
        return
    z = np.polyfit(x[mask], y[mask], 1)
    p = np.poly1d(z)
    tx = np.linspace(np.min(x[mask]), np.max(x[mask]), 50)
    fig.add_trace(go.Scatter(
        x=tx, y=p(tx), mode="lines",
        line=dict(color=color or PALETTE["primary"], width=2.2, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ), row=row, col=col)


def get_figure(saisons=None):
    daily = daily_weather().copy()
    if saisons:
        daily = daily[daily["saison"].isin(saisons)]

    no_snow_mean = daily[daily["neige"] == 0]["conso_mwh"].mean()

    specs = [
        ("temp",      "Température extérieure (°C)",  1, 1, False),
        ("vent",      "Vitesse du vent (km/h)",       1, 2, False),
        ("neige",     "Précipitations de neige (mm)", 2, 1, True),
        ("humidite",  "Humidité relative (%)",        2, 2, False),
    ]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["<b>Température</b>", "<b>Vent</b>",
                        "<b>Neige</b>", "<b>Humidité</b>"],
        vertical_spacing=0.16, horizontal_spacing=0.10,
    )

    for season in SEASON_ORDER:
        color = SEASON_COLORS[season]
        if saisons and season not in saisons:
            continue
        sub = daily[daily["saison"] == season]
        if sub.empty:
            continue
        for col_key, xtitle, row, col, snow_only in specs:
            if snow_only:
                mask = sub["neige"] > 0
                x = sub.loc[mask, col_key]
                y = sub.loc[mask, "conso_mwh"]
                dates = sub.loc[mask, "date"].dt.strftime("%Y-%m-%d")
            else:
                x = sub[col_key]
                y = sub["conso_mwh"]
                dates = sub["date"].dt.strftime("%Y-%m-%d")

            fig.add_trace(go.Scatter(
                x=x, y=y, mode="markers",
                name=season, legendgroup=season,
                showlegend=(col == 1 and row == 1),
                marker=dict(
                    color=color, size=8, opacity=0.8,
                    line=dict(color="white", width=0.8),
                ),
                customdata=dates,
                hovertemplate=(
                    f"<b>{season}</b><br>"
                    "Date : %{customdata}<br>"
                    f"{xtitle.split(' (')[0]}"" : %{x:.1f}<br>"
                    "Consommation : %{y:.1f} MWh"
                    "<extra></extra>"
                ),
            ), row=row, col=col)

    # Trend lines — global, in primary blue
    for col_key, _xtitle, row, col, snow_only in specs:
        if snow_only:
            s = daily[daily["neige"] > 0]
            _add_trend(fig, s[col_key].values, s["conso_mwh"].values, row, col)
        else:
            _add_trend(fig, daily[col_key].values, daily["conso_mwh"].values, row, col)

    fig.add_vline(x=0, line_dash="dot", line_color=PALETTE["muted"],
                  opacity=0.6, row=1, col=1)
    fig.add_hline(
        y=no_snow_mean, line_dash="dash", line_color=PALETTE["muted"],
        line_width=1.5,
        annotation_text=f"Sans neige : {no_snow_mean:.1f} MWh",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color=PALETTE["muted"]),
        row=2, col=1,
    )

    fig.update_layout(**base_layout(
        "Influence des conditions météorologiques sur la consommation électrique",
        "Chaque point = une journée · cliquez une saison dans la légende pour la masquer",
        height=720,
    ))

    for annot in fig.layout.annotations:
        if annot.text and annot.text.startswith("<b>"):
            annot.font = dict(size=14, color=PALETTE["primary"])

    fig.update_layout(
        legend=dict(
            orientation="h", y=-0.08, x=0.5, xanchor="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=PALETTE["blue_100"], borderwidth=1,
            font=dict(size=13), itemsizing="constant",
        ),
        plot_bgcolor="#FFFFFF",
    )
    fig.update_xaxes(showgrid=True, gridcolor=PALETTE["grid"],
                     zeroline=False, showline=True, linecolor=PALETTE["blue_100"])
    fig.update_yaxes(showgrid=True, gridcolor=PALETTE["grid"],
                     zeroline=False, showline=True, linecolor=PALETTE["blue_100"],
                     title_text="Conso (MWh/j)", title_standoff=8)
    for _, xt, r, c, _ in specs:
        fig.update_xaxes(title_text=xt, row=r, col=c, title_standoff=6)
    return fig
