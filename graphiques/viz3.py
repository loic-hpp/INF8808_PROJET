# -*- coding: utf-8 -*-
"""
Viz 3 — Roses polaires par saison. Palette 100% bleue : heures de pointe
en navy foncé, heures hors-pointe en bleu ciel clair.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_utils import load_data, base_layout, SEASONS_ORD, PALETTE


def get_figure(poste=None):
    df = load_data()
    if poste and poste != "Tous":
        df = df[df["poste"] == poste]
    hourly = (df.groupby(["saison", "heure_locale"])["energie_totale_consommee"]
                .mean().reset_index())

    global_max = hourly["energie_totale_consommee"].max() * 1.08

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "polar"}] * 2, [{"type": "polar"}] * 2],
        subplot_titles=SEASONS_ORD,
        horizontal_spacing=0.05, vertical_spacing=0.14,
    )
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    PEAK_HOURS = {7, 8, 9, 17, 18, 19}

    for (row, col), saison in zip(positions, SEASONS_ORD):
        data = hourly[hourly["saison"] == saison].sort_values("heure_locale")
        if data.empty:
            continue
        angles = (data["heure_locale"] * 360 / 24).tolist()
        values = data["energie_totale_consommee"].tolist()
        hours = data["heure_locale"].tolist()
        avg = data["energie_totale_consommee"].mean()

        # Peak hours → deep HQ primary blue; off-peak → light sky blue
        colors = [PALETTE["primary"] if h in PEAK_HOURS else PALETTE["blue_300"]
                  for h in hours]
        opacities = [0.95 if h in PEAK_HOURS else 0.75 for h in hours]

        fig.add_trace(go.Barpolar(
            r=values, theta=angles,
            width=[360 / 24] * len(values),
            marker=dict(color=colors, opacity=opacities,
                        line=dict(color="white", width=0.6)),
            hovertemplate=(f"<b>%{{customdata}}h · {saison}</b>"
                           "<br>Consommation : %{r:.0f} kWh<extra></extra>"),
            customdata=hours, showlegend=False,
        ), row=row, col=col)

        pos_paper = {"Hiver": (0.22, 0.77), "Printemps": (0.78, 0.77),
                     "Été": (0.22, 0.23), "Automne": (0.78, 0.23)}
        xp, yp = pos_paper[saison]
        fig.add_annotation(
            text=f"<b>{avg:.0f}</b><br><span style='font-size:9px'>kWh moy</span>",
            x=xp, y=yp, xref="paper", yref="paper", showarrow=False,
            font=dict(size=13, color=PALETTE["primary"]), align="center",
        )

    polar_cfg = dict(
        radialaxis=dict(
            visible=True, range=[0, global_max],
            tickfont=dict(size=10, color=PALETTE["muted"]),
            gridcolor="rgba(0,85,127,0.18)", nticks=3,
        ),
        angularaxis=dict(
            tickmode="array",
            tickvals=[h * 360 / 24 for h in range(24)],
            ticktext=[f"{h}h" if h % 3 == 0 else "" for h in range(24)],
            direction="clockwise", rotation=90,
            gridcolor="rgba(0,85,127,0.18)",
            tickfont=dict(size=10),
        ),
        bgcolor=PALETTE["blue_50"],   # very pale blue background
    )
    for i in range(1, 5):
        key = "polar" if i == 1 else f"polar{i}"
        fig.update_layout(**{key: polar_cfg})

    subtitle = ("Tous postes confondus" if not poste or poste == "Tous"
                else f"Poste {poste}") + " · 2022–2024 · pointes en bleu foncé"
    fig.update_layout(**base_layout(
        "Consommation moyenne par heure selon la saison",
        subtitle, height=780,
    ))
    fig.update_layout(margin=dict(t=100, b=30, l=40, r=40))
    return fig
