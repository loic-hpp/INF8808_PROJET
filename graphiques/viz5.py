# -*- coding: utf-8 -*-
"""
Viz 5 — Efficacité des événements GLD selon la température et l'heure
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

HQ_BLUE = "#00557F"


def get_figure():
    df = pd.read_csv("assets/data/consommation-clients-evenements-pointe.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["is_winter"] = df["month"].isin([12, 1, 2, 3])

    df_ref = df[(df["indicateur_evenement"] == 0) &
                (df["pre_post_indicateur_evenement"] == 0) &
                df["is_winter"]]
    ref_baseline = df_ref.groupby(["poste", "heure_locale"])["energie_totale_consommee"].mean()

    event_dates = df[df["indicateur_evenement"] == 1]["date"].unique()

    records = []
    for ed in event_dates:
        ev = df[(df["date"] == ed) &
                (df["indicateur_evenement"] == 1) &
                (df["heure_locale"] != 16)]
        if len(ev) == 0:
            continue
        temp = ev["temperature_exterieure_moyenne"].mean()
        for h in ev["heure_locale"].unique():
            ev_h = ev[ev["heure_locale"] == h]
            conso_gld = ev_h["energie_totale_consommee"].sum()
            conso_ref = sum(ref_baseline.get((p, h), 0) for p in ["A", "B", "C"])
            if conso_ref > 0:
                red = (conso_ref - conso_gld) / conso_ref * 100
                records.append({"temp": temp, "heure": h,
                                "reduction": red, "date": str(ed)[:10]})

    res = pd.DataFrame(records)
    np.random.seed(42)
    res["temp_j"] = res["temp"] + np.random.uniform(-0.5, 0.5, len(res))
    res["heure_j"] = res["heure"] + np.random.uniform(-0.2, 0.2, len(res))
    res["red_clip"] = res["reduction"].clip(-60, 75)

    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    fig = go.Figure(go.Scatter(
        x=res["temp_j"],
        y=res["heure_j"],
        mode="markers",
        marker=dict(
            color=res["red_clip"],
            colorscale="RdYlGn",
            cmin=-60, cmax=75,
            size=10,
            line=dict(color="#374151", width=0.4),
            opacity=0.9,
            colorbar=dict(
                title="Réduction (%)",
                thickness=15,
                tickfont=dict(size=11),
            ),
        ),
        customdata=np.stack(
            [res["date"], res["heure"], res["temp"], res["reduction"]], axis=-1
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Heure : %{customdata[1]:.0f}h<br>"
            "Température : %{customdata[2]:.1f}°C<br>"
            "Réduction : %{customdata[3]:.1f}%<extra></extra>"
        ),
    ))

    fig.add_hline(y=13, line_dash="dash", line_color="gray",
                  line_width=1, opacity=0.6)
    fig.add_vline(x=0, line_dash="dot", line_color="gray",
                  line_width=1, opacity=0.6)

    fig.add_annotation(x=-32, y=7.5, text="Pointe<br>matinale",
                       showarrow=False,
                       bgcolor="#e6f2f8", bordercolor=HQ_BLUE,
                       font=dict(color=HQ_BLUE, size=11))
    fig.add_annotation(x=-32, y=18.5, text="Pointe<br>en soirée",
                       showarrow=False,
                       bgcolor="#e6f2f8", bordercolor=HQ_BLUE,
                       font=dict(color=HQ_BLUE, size=11))

    hour_ticks = [6, 7, 8, 9, 17, 18, 19, 20]

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=90, b=70, l=80, r=20),
        title=dict(
            text="Efficacité des événements GLD selon la température et l'heure",
            font=dict(size=16, color=HQ_BLUE),
        ),
        xaxis=dict(
            title="Température extérieure (°C)",
            range=[-35, 12],
            showgrid=True, gridcolor=GRID, zeroline=False,
        ),
        yaxis=dict(
            title="Heure du défi",
            tickmode="array",
            tickvals=hour_ticks,
            ticktext=[f"{h}h" for h in hour_ticks],
            range=[4.5, 21.5],
            showgrid=True, gridcolor=GRID, zeroline=False,
        ),
        annotations=[dict(
            x=0.5, y=1.05, xref="paper", yref="paper",
            text="Tous postes confondus",
            showarrow=False, font=dict(size=11, color="#888780"),
        )],
        height=520,
    )

    return fig
