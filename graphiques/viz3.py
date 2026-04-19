# -*- coding: utf-8 -*-
"""
Viz 3 — Roses polaires par saison (palette orange, conforme mockup).
Bars coloured by intensity (highlights peaks) + peak-hour ring overlay.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_utils import load_data, base_layout, SEASONS_ORD, PALETTE


def _hourly_by_season():
    df = load_data()
    return (df.groupby(["saison", "heure_locale"])["energie_totale_consommee"]
              .mean().reset_index())


def get_figure(poste: str | None = None):
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

    # Peak hours: morning 7-9, evening 17-19 → always highlight
    PEAK_HOURS = {7, 8, 9, 17, 18, 19}

    for (row, col), saison in zip(positions, SEASONS_ORD):
        data = hourly[hourly["saison"] == saison].sort_values("heure_locale")
        if data.empty:
            continue
        angles = (data["heure_locale"] * 360 / 24).tolist()
        values = data["energie_totale_consommee"].tolist()
        hours = data["heure_locale"].tolist()
        avg = data["energie_totale_consommee"].mean()

        # Dual colour: peaks in strong orange, rest in light orange
        colors = [PALETTE["hot"] if h in PEAK_HOURS else "#F59E0B"
                  for h in hours]
        opacities = [0.95 if h in PEAK_HOURS else 0.65 for h in hours]

        fig.add_trace(go.Barpolar(
            r=values, theta=angles,
            width=[360 / 24] * len(values),
            marker=dict(color=colors, opacity=opacities,
                        line=dict(color="white", width=0.6)),
            hovertemplate=(f"<b>%{{customdata}}h · {saison}</b>"
                           "<br>Consommation : %{r:.0f} kWh<extra></extra>"),
            customdata=hours, showlegend=False,
        ), row=row, col=col)

        # Centre label: season average
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
            tickfont=dict(size=10, color="#6b7280"),
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
        bgcolor="#fff7ed",
    )
    for i in range(1, 5):
        key = "polar" if i == 1 else f"polar{i}"
        fig.update_layout(**{key: polar_cfg})

    subtitle = ("Tous postes confondus" if not poste or poste == "Tous"
                else f"Poste {poste}") + " · 2022–2024 · pointes en rouge"
    fig.update_layout(**base_layout(
        "Consommation moyenne par heure selon la saison",
        subtitle, height=780,
    ))
    fig.update_layout(margin=dict(t=100, b=30, l=40, r=40))
    return fig
