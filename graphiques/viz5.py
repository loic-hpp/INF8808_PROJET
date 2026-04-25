# -*- coding: utf-8 -*-
"""
Viz 5 — Efficacité GLD selon température × heure (palette 100% bleue).

Pour encoder la réduction (−60% à +75%) tout en bleu :
  - Réduction très négative (contre-productif)  → bleu très pâle (discret)
  - Autour de 0                                 → bleu moyen
  - Réduction positive                          → bleu profond navy (impact fort)

Ainsi, plus le point est foncé, plus le défi a été efficace — lecture
intuitive et conforme à la palette Hydro-Québec.
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
                    "temp": float(temp), "heure": int(h), "reduction": float(red),
                    "date": str(ed)[:10], "event_id": str(ev_row["event_id"]),
                })
    return records


def get_figure():
    records = _build_records()
    if not records:
        fig = go.Figure()
        fig.add_annotation(text="Aucun événement GLD à afficher",
                           x=0.5, y=0.5, xref="paper", yref="paper",
                           showarrow=False, font=dict(size=16))
        fig.update_layout(height=500)
        return fig

    temps = np.array([r["temp"] for r in records], dtype=float)
    hours = np.array([r["heure"] for r in records], dtype=float)
    reds = np.array([r["reduction"] for r in records], dtype=float)
    dates = [r["date"] for r in records]
    event_ids = [r["event_id"] for r in records]

    rng = np.random.default_rng(42)
    tx = temps + rng.uniform(-0.5, 0.5, len(temps))
    hy = hours + rng.uniform(-0.3, 0.3, len(hours))
    reds_c = np.clip(reds, -60, 75)

    fig = go.Figure()

    # Peak zones — both in very pale blue shades (monochromatic)
    fig.add_hrect(y0=5.5, y1=10.5,
                  fillcolor=PALETTE["blue_100"], opacity=0.45,
                  layer="below", line_width=0)
    fig.add_hrect(y0=16.5, y1=21.5,
                  fillcolor=PALETTE["blue_200"], opacity=0.35,
                  layer="below", line_width=0)

    # BLUE-ONLY diverging colorscale
    # The full range is [-60, +75], i.e. total span = 135
    #   0 clipped   → normalized = 60/135 ≈ 0.44
    # So we place the "neutral" colour near 0.44.
    BLUE_SCALE = [
        [0.00, "#E0F2FE"],  # very pale sky — heavy under-performance
        [0.22, "#BAE6FD"],  # pale sky
        [0.44, "#93C5FD"],  # near-zero reduction = middle blue
        [0.60, "#60A5FA"],
        [0.75, "#2563EB"],
        [0.88, "#1D4ED8"],
        [1.00, "#0B3D66"],  # deep navy — high efficacy
    ]

    fig.add_trace(go.Scatter(
        x=tx.tolist(), y=hy.tolist(), mode="markers",
        marker=dict(
            size=16,
            color=reds_c.tolist(),
            colorscale=BLUE_SCALE,
            cmin=-60, cmax=75,
            showscale=True,
            line=dict(color=PALETTE["primary"], width=1.2),
            opacity=1.0,
            colorbar=dict(
                title="Réduction (%)",
                thickness=14, len=0.85,
                tickvals=[-60, -30, 0, 30, 60],
                tickfont=dict(size=11),
            ),
        ),
        customdata=np.column_stack([event_ids, dates, hours.astype(int), temps, reds]),
        hovertemplate=(
            "Date : %{customdata[1]}<br>"
            "Heure : %{customdata[2]}h<br>"
            "Température : %{customdata[3]:.1f}°C<br>"
            "Réduction : %{customdata[4]:.1f}%"
            "<extra>Cliquez pour charger</extra>"
        ),
        name="",
    ))

    fig.add_vline(x=0, line_dash="dot", line_color=PALETTE["muted"],
                  line_width=1, opacity=0.6)
    fig.add_vline(x=-20, line_dash="dash",
                  line_color=PALETTE["navy"], line_width=1.5, opacity=0.7,
                  annotation_text="Seuil grand froid (−20°C)",
                  annotation_position="top",
                  annotation_font=dict(size=10, color=PALETTE["navy"]))

    fig.add_annotation(x=-33, y=7.5,
                       text="<b>Pointe matinale</b>", showarrow=False,
                       bgcolor=PALETTE["blue_50"], bordercolor=PALETTE["primary"],
                       borderwidth=1, borderpad=4,
                       font=dict(color=PALETTE["primary"], size=11))
    fig.add_annotation(x=-33, y=18.5,
                       text="<b>Pointe soirée</b>", showarrow=False,
                       bgcolor=PALETTE["blue_100"], bordercolor=PALETTE["navy"],
                       borderwidth=1, borderpad=4,
                       font=dict(color=PALETTE["navy"], size=11))

    hour_ticks = [6, 7, 8, 9, 17, 18, 19, 20]
    fig.update_layout(**base_layout(
        "Efficacité des événements GLD selon la température et l'heure",
        f"{len(records)} points · un point = une heure d'un défi · cliquez pour explorer",
        height=560,
    ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(
            title="Température extérieure (°C)",
            range=[-36, 12],
            showgrid=True, gridcolor=PALETTE["grid"],
            zeroline=False,
            showline=True, linecolor=PALETTE["blue_100"], linewidth=1,
            ticks="outside", tickcolor=PALETTE["muted"],
        ),
        yaxis=dict(
            title="Heure du défi",
            tickmode="array",
            tickvals=hour_ticks,
            ticktext=[f"{h}h" for h in hour_ticks],
            range=[4.5, 21.5],
            showgrid=True, gridcolor=PALETTE["grid"],
            zeroline=False,
            showline=True, linecolor=PALETTE["blue_100"], linewidth=1,
            ticks="outside", tickcolor=PALETTE["muted"],
        ),
    )
    return fig
