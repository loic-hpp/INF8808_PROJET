# -*- coding: utf-8 -*-
"""
Viz 8 — Profils par poste A/B/C. Palette 100% bleue : trois nuances
distinctes (navy profond / bleu HQ / bleu sky) pour distinguer les postes.
"""
import plotly.graph_objects as go
from data_utils import load_data, base_layout, SEASONS_ORD, PALETTE


# Three distinct blue shades so postes are distinguishable without hue change
POSTE_COLORS = {
    "A": PALETTE["navy"],      # deep navy
    "B": PALETTE["accent"],    # HQ cyan
    "C": PALETTE["blue_400"],  # mid sky-blue
}


def get_figure(mode="absolu"):
    df = load_data()

    if mode == "normalise":
        agg = (df.groupby(["saison", "poste"])
                 .apply(lambda x: (x["energie_totale_consommee"] / x["clients_connectes"]).mean())
                 .unstack())
        ytitle = "Consommation moyenne par client (kWh/h/client)"
        fmt = "{:.2f}"
        subtitle = "Normalisé par client connecté — neutralise l'effet de taille du poste"
    else:
        agg = df.groupby(["saison", "poste"])["energie_totale_consommee"].mean().unstack()
        ytitle = "Consommation moyenne (kWh/h)"
        fmt = "{:.0f}"
        subtitle = "Consommation horaire moyenne par saison · 2022–2024"

    agg = agg.reindex(SEASONS_ORD)

    fig = go.Figure()
    for poste in ("A", "B", "C"):
        vals = agg[poste].values
        fig.add_trace(go.Bar(
            name=f"Poste {poste}",
            x=SEASONS_ORD, y=vals,
            marker_color=POSTE_COLORS[poste],
            marker_line=dict(color="white", width=0.8),
            text=[fmt.format(v) for v in vals],
            textposition="outside",
            textfont=dict(size=11, color=POSTE_COLORS[poste]),
            hovertemplate=(f"<b>Poste {poste}</b><br>"
                           "Saison : %{x}<br>"
                           f"Conso : %{{y:{',.2f' if mode == 'normalise' else ',.0f'}}} "
                           f"{'kWh/h/client' if mode == 'normalise' else 'kWh/h'}"
                           "<extra></extra>"),
        ))

    fig.update_layout(**base_layout(
        "Profils de consommation selon les postes A, B et C",
        subtitle, height=500,
    ))
    fig.update_layout(
        barmode="group", bargap=0.22, bargroupgap=0.06,
        xaxis=dict(title="Saison", showgrid=False, zeroline=False),
        yaxis=dict(title=ytitle, showgrid=True,
                   gridcolor=PALETTE["grid"], zeroline=False),
        legend=dict(x=0.98, y=0.98, xanchor="right",
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor=PALETTE["blue_100"], borderwidth=1),
    )
    return fig
