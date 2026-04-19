# -*- coding: utf-8 -*-
"""
Viz 5 — Efficacité GLD selon température × heure.
Chaque point = une heure d'un défi. Cliquez pour charger dans viz4 & viz6.

Fix important : colorscale sans blanc au milieu pour que les points près de 0%
restent bien visibles. Utilise une palette rouge-orange-vert qui garde une
luminosité homogène.
"""
import numpy as np
import plotly.graph_objects as go
from data_utils import load_data, winter_baseline, event_table, base_layout, PALETTE


def _build_records():
    df = load_data()
    ref_baseline = winter_baseline()
    ev_tbl = event_table()

    records = []
    for _, ev_row in ev_tbl.iterrows():
        ed = ev_row["date"]
        hours_in_defi = range(ev_row["heure_debut"], ev_row["heure_fin"] + 1)
        temp = ev_row["temperature_ext"]
        for h in hours_in_defi:
            ev_h = df[(df["date"] == ed) & (df["heure_locale"] == h)
                      & (df["indicateur_evenement"] == 1)]
            if ev_h.empty:
                continue
            conso_gld = ev_h["energie_totale_consommee"].sum()
            conso_ref = sum(ref_baseline.get((p, h), 0) for p in ("A", "B", "C"))
            if conso_ref > 0:
                red = (conso_ref - conso_gld) / conso_ref * 100
                records.append({
                    "temp": temp, "heure": h, "reduction": red,
                    "date": str(ed)[:10], "event_id": ev_row["event_id"],
                })
    return records


def get_figure():
    records = _build_records()
    if not records:
        return go.Figure()

    temps = np.array([r["temp"] for r in records])
    hours = np.array([r["heure"] for r in records])
    reds = np.array([r["reduction"] for r in records])
    dates = [r["date"] for r in records]
    event_ids = [r["event_id"] for r in records]

    # Deterministic jitter so points don't overlap
    rng = np.random.default_rng(42)
    tx = temps + rng.uniform(-0.5, 0.5, len(temps))
    hy = hours + rng.uniform(-0.25, 0.25, len(hours))
    reds_c = np.clip(reds, -60, 75)

    fig = go.Figure()

    # Peak zone highlighting (more vivid to anchor the reading)
    fig.add_hrect(y0=5.5, y1=10.5,
                  fillcolor="rgba(59, 130, 246, 0.10)",
                  layer="below", line_width=0)
    fig.add_hrect(y0=16.5, y1=21.5,
                  fillcolor="rgba(251, 146, 60, 0.12)",
                  layer="below", line_width=0)

    # ── KEY FIX: no white midpoint. Solid red→orange→yellow→green ramp.
    # Every point stays visible against white background.
    COLORSCALE = [
        [0.00, "#991B1B"],   # deep red (−60%)
        [0.20, "#EF4444"],   # red
        [0.35, "#F97316"],   # orange
        [0.45, "#F59E0B"],   # amber
        [0.52, "#EAB308"],   # yellow — but not near white
        [0.62, "#84CC16"],   # lime
        [0.80, "#22C55E"],   # green
        [1.00, "#166534"],   # deep green (+75%)
    ]

    fig.add_trace(go.Scatter(
        x=tx, y=hy, mode="markers",
        marker=dict(
            color=reds_c,
            colorscale=COLORSCALE,
            cmin=-60, cmax=75,
            size=14,                                    # bigger (was 13)
            line=dict(color="#1F2937", width=1),        # stronger outline
            opacity=0.95,                               # opaque
            colorbar=dict(
                title=dict(text="Réduction<br>(%)", side="top",
                           font=dict(size=11)),
                thickness=14, len=0.85,
                tickfont=dict(size=11),
                tickvals=[-60, -30, 0, 30, 60],
                outlinewidth=0,
            ),
        ),
        customdata=np.stack([event_ids, dates, hours, temps, reds], axis=-1),
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "Heure : %{customdata[2]:.0f}h<br>"
            "Température : %{customdata[3]:.1f}°C<br>"
            "<b>Réduction : %{customdata[4]:.1f}%</b>"
            "<extra>👆 cliquez pour charger</extra>"
        ),
    ))

    # Reference guides
    fig.add_vline(x=0, line_dash="dot", line_color="#6B7280",
                  line_width=1, opacity=0.6)
    fig.add_vline(x=-20, line_dash="dash",
                  line_color=PALETTE["hot"], line_width=1.5, opacity=0.6,
                  annotation_text="Seuil grand froid (−20°C)",
                  annotation_position="top",
                  annotation_font=dict(size=10, color=PALETTE["hot"]))

    # Peak zone labels (kept compact on the left margin)
    fig.add_annotation(x=-33, y=7.5,
                       text="<b>Pointe matinale</b>", showarrow=False,
                       bgcolor="#EFF6FF", bordercolor=PALETTE["primary"],
                       borderwidth=1, borderpad=4,
                       font=dict(color=PALETTE["primary"], size=11))
    fig.add_annotation(x=-33, y=18.5,
                       text="<b>Pointe soirée</b>", showarrow=False,
                       bgcolor="#FFF7ED", bordercolor=PALETTE["warm"],
                       borderwidth=1, borderpad=4,
                       font=dict(color="#9A3412", size=11))

    hour_ticks = [6, 7, 8, 9, 17, 18, 19, 20]
    fig.update_layout(**base_layout(
        "Efficacité des événements GLD selon la température et l'heure",
        f"{len(records)} points · un point = une heure d'un défi · cliquez pour explorer",
        height=560,
    ))
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        xaxis=dict(
            title="Température extérieure (°C)",
            range=[-36, 12],
            showgrid=True, gridcolor="#F1F5F9",
            zeroline=False, showline=True, linecolor="#E5E7EB",
        ),
        yaxis=dict(
            title="Heure du défi",
            tickmode="array",
            tickvals=hour_ticks,
            ticktext=[f"{h}h" for h in hour_ticks],
            range=[4.5, 21.5],
            showgrid=True, gridcolor="#F1F5F9",
            zeroline=False, showline=True, linecolor="#E5E7EB",
        ),
    )
    return fig
