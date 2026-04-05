# -*- coding: utf-8 -*-
"""
Viz 7 — Nombre de clients/thermostats connectés et ampleur de la réduction GLD
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HQ_BLUE = "#00557F"
HQ_LIGHT = "#009FE3"


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
        tstats = ev["tstats_intelligents_connectes"].sum() / ev["heure_locale"].nunique()
        clients = ev["clients_connectes"].sum() / ev["heure_locale"].nunique()
        total_gld, total_ref = 0, 0
        for h in ev["heure_locale"].unique():
            ev_h = ev[ev["heure_locale"] == h]
            total_gld += ev_h["energie_totale_consommee"].sum()
            total_ref += sum(ref_baseline.get((p, h), 0) for p in ["A", "B", "C"])
        if total_ref > 0:
            red = (total_ref - total_gld) / total_ref * 100
            records.append({"tstats": tstats, "clients": clients,
                            "reduction": red, "date": str(ed)[:10]})

    res = pd.DataFrame(records)

    GRID = "rgba(200,200,200,0.4)"
    BG = "#fafafa"

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "Nombre moyen de clients connectés",
            "Nombre moyen de thermostats connectés",
        ],
        horizontal_spacing=0.12,
    )

    scatter_kw = dict(
        mode="markers",
        marker=dict(color=HQ_LIGHT, size=10, opacity=0.88,
                    line=dict(color="#374151", width=0.5)),
        showlegend=False,
    )

    for col_name, col_idx in [("clients", 1), ("tstats", 2)]:
        fig.add_trace(go.Scatter(
            x=res[col_name],
            y=res["reduction"],
            customdata=np.stack(
                [res["date"], res[col_name], res["reduction"]], axis=-1
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Valeur : %{customdata[1]:.0f}<br>"
                "Réduction : %{customdata[2]:.1f}%<extra></extra>"
            ),
            **scatter_kw,
        ), row=1, col=col_idx)

        z = np.polyfit(res[col_name], res["reduction"], 1)
        p = np.poly1d(z)
        tx = np.linspace(res[col_name].min() * 0.97, res[col_name].max() * 1.03, 50)
        r = res[col_name].corr(res["reduction"])
        fig.add_trace(go.Scatter(
            x=tx, y=p(tx),
            mode="lines",
            name=f"Tendance (r = {r:.2f})",
            line=dict(color=HQ_BLUE, width=1.8, dash="dash"),
            showlegend=(col_idx == 1),
            hoverinfo="skip",
        ), row=1, col=col_idx)

        fig.add_hline(y=0, line_dash="dot", line_color="gray",
                      line_width=1, opacity=0.7, row=1, col=col_idx)

    fig.update_layout(
        font=dict(family="Arial", size=13, color="#333"),
        paper_bgcolor="white",
        plot_bgcolor=BG,
        margin=dict(t=90, b=70, l=80, r=30),
        title=dict(
            text="Nombre de clients connectés et ampleur de la réduction GLD",
            font=dict(size=16, color=HQ_BLUE),
        ),
        legend=dict(x=0.5, y=-0.15, xanchor="center", orientation="h",
                    bgcolor="rgba(255,255,255,0.9)", bordercolor="#ddd", borderwidth=1),
        annotations=[dict(
            x=0.5, y=1.05, xref="paper", yref="paper",
            text="Un point = un événement GLD \u00b7 tous postes confondus",
            showarrow=False, font=dict(size=11, color="#888780"),
        )],
        height=500,
    )

    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(title_text="Réduction de consommation (%)",
                     showgrid=True, gridcolor=GRID, zeroline=False, dtick=25)

    return fig
