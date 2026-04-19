# -*- coding: utf-8 -*-
"""
Viz 7 — Clients / thermostats connectés ↔ ampleur de réduction GLD.
Utilise la table d'événements unique (source unique de vérité).
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_utils import event_table, base_layout, PALETTE


def get_figure():
    ev = event_table()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Clients connectés", "Thermostats connectés"],
        horizontal_spacing=0.12,
    )

    # Colour each point by sign of reduction (positive = green, negative = red)
    colors = np.where(ev["reduction_pct"] >= 0, PALETTE["cool"], PALETTE["hot"])

    for col_idx, col_key, xtitle in [
        (1, "clients_moy", "Nombre moyen de clients connectés"),
        (2, "tstats_moy",  "Nombre moyen de thermostats connectés"),
    ]:
        fig.add_trace(go.Scatter(
            x=ev[col_key], y=ev["reduction_pct"],
            mode="markers",
            marker=dict(color=colors, size=11, opacity=0.85,
                        line=dict(color="#1f2937", width=0.6)),
            customdata=np.stack([ev["date_str"], ev[col_key],
                                 ev["reduction_pct"], ev["temperature_ext"]], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{xtitle.split(' ')[-2].title()} : "
                "%{customdata[1]:.0f}<br>"
                "Réduction : %{customdata[2]:.1f}%<br>"
                "Température : %{customdata[3]:.1f}°C<extra></extra>"
            ),
            showlegend=False,
        ), row=1, col=col_idx)

        # Trend line
        x = ev[col_key].values
        y = ev["reduction_pct"].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        tx = np.linspace(x.min() * 0.97, x.max() * 1.03, 50)
        r = np.corrcoef(x, y)[0, 1]
        fig.add_trace(go.Scatter(
            x=tx, y=p(tx), mode="lines",
            line=dict(color=PALETTE["primary"], width=2, dash="dash"),
            name=f"Tendance (r = {r:.2f})",
            showlegend=(col_idx == 1),
            hoverinfo="skip",
        ), row=1, col=col_idx)

        fig.add_hline(y=0, line_dash="dot", line_color="gray",
                      line_width=1, opacity=0.7, row=1, col=col_idx)

    fig.update_layout(**base_layout(
        "Participation et ampleur de la réduction GLD",
        f"Un point = un événement · {len(ev)} événements · "
        "rouge = réduction négative",
        height=500,
    ))
    fig.update_layout(
        legend=dict(x=0.5, y=-0.18, xanchor="center", orientation="h",
                    bgcolor="rgba(255,255,255,0.9)", bordercolor="#ddd", borderwidth=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor=PALETTE["grid"], zeroline=False)
    fig.update_yaxes(title_text="Réduction de consommation (%)", showgrid=True,
                     gridcolor=PALETTE["grid"], zeroline=False, dtick=25)
    return fig
