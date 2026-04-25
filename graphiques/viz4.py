# -*- coding: utf-8 -*-
"""
Viz 4 — Profil avant/pendant/après un événement GLD. Palette 100% bleue.
Phase préchauffage = pale sky band, phase défi = pale navy band.
"""
import numpy as np
import plotly.graph_objects as go
from data_utils import event_profile, base_layout, PALETTE


def get_figure(event_date=None):
    df = event_profile(event_date)
    x_labels = [f"{o:+d}h" if o != 0 else "0h" for o in df["offset"]]
    h_vals = df["conso_hilo"].tolist()
    r_vals = df["conso_ref"].tolist()

    during_idx = [i for i, o in enumerate(df["offset"]) if 0 <= o <= 3]
    h_event = np.nanmean([h_vals[i] for i in during_idx])
    r_event = np.nanmean([r_vals[i] for i in during_idx])
    reduction = ((r_event - h_event) / r_event * 100) if r_event else 0

    idx_4 = df.index[df["offset"] == 4][0] if (df["offset"] == 4).any() else None
    rebound = 0
    if idx_4 is not None and r_vals[idx_4] and not np.isnan(h_vals[idx_4]):
        rebound = (h_vals[idx_4] - r_vals[idx_4]) / r_vals[idx_4] * 100

    fig = go.Figure()

    # Phase bands — both blue-family shades
    fig.add_vrect(x0="-2h", x1="0h", fillcolor=PALETTE["blue_100"], opacity=0.55,
                  layer="below", line_width=0,
                  annotation_text="Préchauffage",
                  annotation_position="top left",
                  annotation_font=dict(color=PALETTE["primary"], size=11))
    fig.add_vrect(x0="0h", x1="+4h", fillcolor=PALETTE["blue_200"], opacity=0.55,
                  layer="below", line_width=0,
                  annotation_text="Défi GLD",
                  annotation_position="top right",
                  annotation_font=dict(color=PALETTE["navy"], size=11))
    for xv in ("0h", "+4h"):
        fig.add_vline(x=xv, line_dash="dash", line_color=PALETTE["navy"],
                      line_width=1.5, opacity=0.7)

    # Savings area = pale blue fill (where hilo < ref)
    fig.add_trace(go.Scatter(
        x=x_labels, y=r_vals, mode="lines",
        line_color="rgba(0,0,0,0)", showlegend=False, hoverinfo="skip",
    ))
    fill_y = [h if (not np.isnan(h) and not np.isnan(r) and r > h) else np.nan
              for h, r in zip(h_vals, r_vals)]
    fig.add_trace(go.Scatter(
        x=x_labels, y=fill_y, mode="lines",
        fill="tonexty", fillcolor="rgba(0, 159, 227, 0.18)",   # HQ accent @18%
        line_color="rgba(0,0,0,0)", showlegend=False, hoverinfo="skip",
    ))

    # Reference — slate grey (neutral / baseline), dotted
    fig.add_trace(go.Scatter(
        x=x_labels, y=r_vals, mode="lines+markers",
        name="Référence (hiver sans GLD)",
        line=dict(color=PALETTE["muted"], width=2.5, dash="dot"),
        marker=dict(size=7, color=PALETTE["muted"]),
        hovertemplate="<b>%{x}</b><br>Référence : %{y:.0f} kWh<extra></extra>",
    ))
    # Actual Hilo consumption — HQ accent blue
    fig.add_trace(go.Scatter(
        x=x_labels, y=h_vals, mode="lines+markers",
        name="Clients Hilo (tous postes)",
        line=dict(color=PALETTE["accent"], width=3),
        marker=dict(size=9, color=PALETTE["accent"],
                    line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Hilo : %{y:.0f} kWh<extra></extra>",
    ))

    # Annotations — use blue shades for good/bad instead of green/red
    mid_i = during_idx[len(during_idx) // 2] if during_idx else None
    if mid_i is not None and h_vals[mid_i] is not None and not np.isnan(h_vals[mid_i]):
        fig.add_annotation(
            x=f"+{df['offset'].iloc[mid_i]}h",
            y=h_vals[mid_i],
            text=f"<b>↓ {reduction:.0f}%</b><br><span style='font-size:10px'>pendant le défi</span>",
            showarrow=True, arrowhead=2, ax=40, ay=-55,
            font=dict(color=PALETTE["primary"], size=12),
            bgcolor=PALETTE["blue_100"], bordercolor=PALETTE["accent"],
            borderwidth=1,
        )
    if idx_4 is not None and not np.isnan(h_vals[idx_4]):
        fig.add_annotation(
            x="+4h", y=h_vals[idx_4],
            text=f"<b>Effet rebond</b><br><span style='font-size:10px'>+{rebound:.0f}% vs référence</span>",
            showarrow=True, arrowhead=2, ax=70, ay=-40,
            font=dict(color=PALETTE["navy"], size=12),
            bgcolor=PALETTE["blue_200"], bordercolor=PALETTE["navy"],
            borderwidth=1,
        )

    title_suffix = f" · {event_date}" if event_date else " · moyenne sur tous les événements"
    fig.update_layout(**base_layout(
        "Profil de consommation avant, pendant et après un événement GLD" + title_suffix,
        "Zone bleue claire = énergie économisée grâce au programme Hilo",
        height=500,
    ))
    fig.update_layout(
        xaxis=dict(title="Heures par rapport au début de l'événement",
                   showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
        yaxis=dict(title="Consommation totale (kWh)",
                   showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.95)",
                    bordercolor=PALETTE["blue_100"], borderwidth=1),
    )
    return fig
