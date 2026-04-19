# -*- coding: utf-8 -*-
"""
Viz 6 — Thermostats intelligents : consigne vs intérieure vs extérieure.
Peut être piloté par un événement spécifique (sinon moyenne sur TOUS).
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_utils import event_profile, base_layout, PALETTE


def get_figure(event_date=None):
    df = event_profile(event_date, offsets=range(-3, 6))
    x_labels = [f"{o:+d}h" if o != 0 else "0h" for o in df["offset"]]

    fig = go.Figure()

    fig.add_vrect(x0="-2h", x1="0h", fillcolor="#FEF3C7", opacity=0.5,
                  layer="below", line_width=0,
                  annotation_text="Préchauffage", annotation_position="top left",
                  annotation_font=dict(color="#92400e", size=10))
    fig.add_vrect(x0="0h", x1="+4h", fillcolor="#FEE2E2", opacity=0.5,
                  layer="below", line_width=0,
                  annotation_text="Défi GLD", annotation_position="top right",
                  annotation_font=dict(color="#991b1b", size=10))
    for xv in ("0h", "+4h"):
        fig.add_vline(x=xv, line_dash="dash", line_color=PALETTE["hot"],
                      line_width=1.5, opacity=0.6)

    fig.add_trace(go.Scatter(
        x=x_labels, y=df["temp_consigne"], mode="lines+markers",
        name="Consigne (°C)",
        line=dict(color=PALETTE["hot"], width=3),
        marker=dict(size=9, color=PALETTE["hot"],
                    line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Consigne : %{y:.2f}°C<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=df["temp_interieure"], mode="lines+markers",
        name="Température intérieure (°C)",
        line=dict(color=PALETTE["accent"], width=3, dash="dot"),
        marker=dict(size=9, symbol="square", color=PALETTE["accent"],
                    line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Intérieure : %{y:.2f}°C<extra></extra>",
    ))

    # Key annotation: delta at hour 2 (middle of defi)
    if (df["offset"] == 2).any():
        idx_2 = df.index[df["offset"] == 2][0]
        delta = df["temp_interieure"].iloc[idx_2] - df["temp_consigne"].iloc[idx_2]
        if delta > 0:
            fig.add_annotation(
                x="+2h",
                y=(df["temp_interieure"].iloc[idx_2] + df["temp_consigne"].iloc[idx_2]) / 2,
                text=f"<b>Δ ≈ {delta:.1f}°C</b><br><span style='font-size:10px'>inertie thermique</span>",
                showarrow=True, arrowhead=2, ax=60, ay=0,
                font=dict(color="#1f2937", size=11),
                bgcolor="#FEF9C3", bordercolor="#FDE047", borderwidth=1,
            )

    title_suffix = f" · {event_date}" if event_date else " · moyenne sur tous les événements"
    fig.update_layout(**base_layout(
        "Comportement des thermostats intelligents Hilo" + title_suffix,
        "La consigne plonge dès 0h · l'intérieure suit avec un décalage (inertie)",
        height=500,
    ))
    fig.update_layout(
        xaxis=dict(title="Heures par rapport au début de l'événement",
                   showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
        yaxis=dict(title="Température (°C)",
                   showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
        legend=dict(x=0.01, y=0.02, yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="#e5e7eb", borderwidth=1),
    )
    return fig
