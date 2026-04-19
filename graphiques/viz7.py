# -*- coding: utf-8 -*-
"""
Viz 7 — Clients / thermostats connectés ↔ ampleur de réduction GLD.
Palette 100% bleue : réductions positives en navy, négatives en bleu pâle.
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

    # Positive reduction → deep navy (strong/effective)
    # Negative reduction → pale sky blue (weak/counter-productive)
    colors = np.where(ev["reduction_pct"] >= 0,
                      PALETTE["navy"],
                      PALETTE["blue_300"])

    for col_idx, col_key, xtitle in [
        (1, "clients_moy", "Nombre moyen de clients connectés"),
        (2, "tstats_moy",  "Nombre moyen de thermostats connectés"),
    ]:
        fig.add_trace(go.Scatter(
            x=ev[col_key], y=ev["reduction_pct"],
            mode="markers",
            marker=dict(color=colors, size=12, opacity=0.88,
                        line=dict(color=PALETTE["primary"], width=0.8)),
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

        x = ev[col_key].values
        y = ev["reduction_pct"].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        tx = np.linspace(x.min() * 0.97, x.max() * 1.03, 50)
        r = np.corrcoef(x, y)[0, 1]
        fig.add_trace(go.Scatter(
            x=tx, y=p(tx), mode="lines",
            line=dict(color=PALETTE["accent"], width=2.2, dash="dash"),
            name=f"Tendance (r = {r:.2f})",
            showlegend=(col_idx == 1),
            hoverinfo="skip",
        ), row=1, col=col_idx)

        fig.add_hline(y=0, line_dash="dot", line_color=PALETTE["muted"],
                      line_width=1, opacity=0.7, row=1, col=col_idx)

    fig.update_layout(**base_layout(
        "Participation et ampleur de la réduction GLD",
        f"Un point = un événement · {len(ev)} événements · "
        "navy = positif, bleu pâle = contre-productif",
        height=500,
    ))
    fig.update_layout(
        legend=dict(x=0.5, y=-0.18, xanchor="center", orientation="h",
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor=PALETTE["blue_100"], borderwidth=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor=PALETTE["grid"], zeroline=False)
    fig.update_yaxes(title_text="Réduction de consommation (%)", showgrid=True,
                     gridcolor=PALETTE["grid"], zeroline=False, dtick=25)
    return fig
