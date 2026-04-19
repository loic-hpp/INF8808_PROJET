# -*- coding: utf-8 -*-
"""
Hydro-Québec · Gestion de la demande électrique lors des pics hivernaux
INF8808 — Équipe 25 — Hiver 2026

Scrollytelling dashboard Plotly/Dash avec :
  • KPI hero dynamique
  • Sections narratives reliées (problème → programme → impact → mécanisme → échelle)
  • Filtres interactifs (saison, poste, événement) pilotant plusieurs vizs
  • Cross-linking : cliquer un point sur viz5 met à jour viz4 + viz6
"""
from __future__ import annotations

import dash
from dash import Input, Output, dcc, html

# Data layer (loaded once via lru_cache)
from data_utils import event_table, global_kpis

# Viz modules (functions return figures)
from graphiques import viz1a, viz1b, viz2, viz3, viz4, viz5, viz6, viz7, viz8


# ─────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Hydro-Québec · Gestion de la demande électrique"

KPI = global_kpis()
EVENTS = event_table()


# ─────────────────────────────────────────────────────────────
# Reusable UI atoms
# ─────────────────────────────────────────────────────────────
def kpi_card(value: str, label: str, sublabel: str = "") -> html.Div:
    return html.Div(className="kpi-card", children=[
        html.Div(value, className="kpi-value"),
        html.Div(label, className="kpi-label"),
        html.Div(sublabel, className="kpi-sub") if sublabel else None,
    ])


def chapter(num: int, kicker: str) -> html.Div:
    return html.Div(className="chapter-header", children=[
        html.Span(f"CHAPITRE {num:02d}", className="chapter-num"),
        html.Span(kicker, className="chapter-kicker"),
    ])


def insight_box(title: str, body: str, icon: str = "💡") -> html.Div:
    return html.Div(className="insight-box", children=[
        html.Div(className="insight-head", children=[
            html.Span(icon, className="insight-icon"), html.Strong(title),
        ]),
        html.P(body, className="insight-body"),
    ])


def viz_section(section_id: str, question: str, figure_id: str,
                intro: str, outro: str | None = None,
                controls: html.Div | None = None,
                insight: html.Div | None = None) -> html.Section:
    children = [
        html.H2(question, id=f"title-{section_id}"),
        html.Div(className="section-body", children=[html.P(intro)]),
    ]
    if controls is not None:
        children.append(controls)
    children.append(html.Div(className="graph-container",
                             children=[dcc.Loading(dcc.Graph(id=figure_id,
                                                             config={"displayModeBar": False}))]))
    if insight is not None:
        children.append(insight)
    if outro:
        children.append(html.Div(className="section-body",
                                 children=[html.P(outro)]))
    return html.Section(id=section_id, className="content-section", children=children)


# ─────────────────────────────────────────────────────────────
# Sidebar (scroll-spy enabled via JS in assets)
# ─────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("hero",     "Accueil",            ""),
    ("viz1",     "Météo",              "01"),
    ("viz2",     "Calendrier",         "02"),
    ("viz3",     "Profils horaires",   "03"),
    ("viz4",     "Impact GLD",         "04"),
    ("viz5",     "Efficacité",         "05"),
    ("viz6",     "Thermostats",        "06"),
    ("viz7",     "Participation",      "07"),
    ("viz8",     "Postes A/B/C",       "08"),
    ("synthese", "Synthèse",           ""),
]

sidebar = html.Nav(id="sidebar", children=[
    html.Div(className="sidebar-logo", children=[
        html.Img(src="/assets/logo.svg", className="sidebar-mark",
                 alt="Hilo GLD"),
        html.Div(children=[
            html.Div("Gestion de la demande", className="sidebar-brand"),
            html.Div("Hilo · GLD", className="sidebar-sub"),
        ]),
    ]),
    html.Ul([
        html.Li(html.A([html.Span(num, className="nav-num"), html.Span(label)],
                       href=f"#{sid}", className="nav-link", **{"data-target": sid}))
        for sid, label, num in NAV_ITEMS
    ]),
    html.Div(className="sidebar-footer", children=[
        html.Div("INF8808 · Équipe 25", className="sidebar-team"),
        html.Div("Hiver 2026", className="sidebar-team-sub"),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Hero + KPIs
# ─────────────────────────────────────────────────────────────
hero = html.Section(id="hero", className="hero-section", children=[
    html.Div(className="hero-content", children=[
        html.Span("TABLEAU DE BORD ANALYTIQUE", className="hero-kicker"),
        html.H1([
            "Gestion de la demande électrique ",
            html.Br(),
            html.Span("lors des pics hivernaux", className="hero-accent"),
        ]),
        html.P(className="hero-lead", children=[
            "Analyse du programme ", html.Strong("Hilo"),
            " d'Hydro-Québec : quel est l'impact de la météo sur la consommation, "
            "et comment le comportement des participants évolue avant, pendant et après ",
            "les événements de gestion locale de la demande (GLD) ?"
        ]),
        html.Div(className="hero-meta", children=[
            html.Span(f"📅 {KPI['date_min']} → {KPI['date_max']}"),
            html.Span(f"📊 {KPI['n_obs']:,} observations horaires".replace(",", " ")),
            html.Span(f"📍 Région de Montréal · 3 postes"),
        ]),
        html.Div(className="hero-scroll-cue", children=[
            html.Span("Défilez pour explorer"), html.Span("↓", className="scroll-arrow"),
        ]),
    ]),
    html.Div(className="kpi-strip", children=[
        kpi_card(f"{KPI['n_events']}", "événements GLD analysés", "2022–2024"),
        kpi_card(f"{KPI['mean_reduction_pct']:.0f}%", "réduction moyenne",
                 "pendant la phase de défi"),
        kpi_card(f"{KPI['best_reduction_pct']:.0f}%", "meilleure performance",
                 "un seul événement"),
        kpi_card(f"{KPI['pct_events_positive']:.0f}%", "événements positifs",
                 f"le reste = effet contre-productif"),
        kpi_card(f"{KPI['n_tstats_max']:,}".replace(",", " "),
                 "thermostats Hilo max", "connectés simultanément"),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Chapter 1 — Le contexte
# ─────────────────────────────────────────────────────────────
contexte = html.Section(id="contexte", className="content-section narrative", children=[
    chapter(1, "Le contexte"),
    html.H2("Pourquoi gérer la demande lors des pics hivernaux ?"),
    html.Div(className="section-body two-col", children=[
        html.Div([
            html.P([
                "Chaque hiver, les périodes de grand froid entraînent une ",
                html.Strong("forte hausse de la consommation d'électricité au Québec"),
                ". Hydro-Québec doit maintenir l'équilibre entre production et demande en temps réel, ",
                "sous peine de surcharges et de coûts d'énergie additionnels.",
            ]),
            html.P([
                "Le programme ", html.Strong("Hilo"),
                " recrute des volontaires dont les thermostats intelligents ajustent légèrement le chauffage ",
                "durant les heures critiques (matin 6h–10h, soir 17h–21h). Répartis sur des milliers de foyers, ",
                "ces micro-ajustements stabilisent le réseau.",
            ]),
        ]),
        html.Div(className="context-card", children=[
            html.H3("Question centrale"),
            html.Blockquote([
                "Quel est l'impact de la météo sur la consommation des participants Hilo, ",
                "et comment leur comportement évolue-t-il ",
                html.Strong("avant, pendant et après"),
                " un événement GLD ?",
            ]),
            html.Div(className="audience-tag", children=[
                html.Span("🎯 Public cible : "),
                html.Span("analystes et gestionnaires Hydro-Québec"),
            ]),
        ]),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Chapter 2 — Météo & consommation (Viz 1)
# ─────────────────────────────────────────────────────────────
viz1_section = html.Section(id="viz1", className="content-section", children=[
    chapter(2, "Météo vs consommation"),
    html.H2("Quelles conditions météo font exploser la demande ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Avant de comprendre le programme, il faut comprendre ce qu'il doit ",
            html.Em("domestiquer"),
            " : la météo. Nous commençons par un classement des variables les plus corrélées ",
            "à la consommation, puis nous regardons la forme exacte de ces relations.",
        ]),
    ]),
    html.Div(className="controls-bar", children=[
        html.Label("Filtrer par saison :", className="control-label"),
        dcc.RadioItems(
            id="viz1-saison",
            options=[{"label": s, "value": s} for s in
                     ("Toutes", "Hiver", "Printemps", "Été", "Automne")],
            value="Toutes", inline=True, className="radio-pills",
        ),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz1a",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "La température domine",
        "Avec r ≈ −0,72 en hiver, la température extérieure est la variable qui dicte la consommation. "
        "Les autres variables (vent, humidité, neige) sont bien plus marginales — mais la neige "
        "coïncide souvent avec le grand froid.",
        "🌡️",
    ),
    html.Div(className="section-body", children=[
        html.P("Regardons maintenant la forme exacte de ces relations :"),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz1b",
                                             config={"displayModeBar": False}))]),
    html.Div(className="section-body", children=[
        html.P([
            "La relation température-consommation est clairement ",
            html.Strong("non linéaire"),
            " : en dessous de 0°C la consommation explose, au-dessus de 10°C elle se stabilise. ",
            "La neige est presque toujours associée à une consommation élevée car elle coïncide avec les grands froids.",
        ]),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Chapter 3 — Calendrier (Viz 2)
# ─────────────────────────────────────────────────────────────
viz2_section = html.Section(id="viz2", className="content-section", children=[
    chapter(3, "Vue calendrier"),
    html.H2("Quels jours et quels mois concentrent la demande ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Agréger sur 3 ans jour × mois révèle la structure saisonnière et hebdomadaire. "
            "Basculez entre la vue brute (MWh absolus) et la vue relative (% d'écart à la moyenne annuelle) ",
            "pour comprendre ", html.Em("où"), " et ", html.Em("quand"),
            " l'effort GLD aura le plus d'impact.",
        ]),
    ]),
    html.Div(className="controls-bar", children=[
        html.Label("Mode d'affichage :", className="control-label"),
        dcc.RadioItems(
            id="viz2-mode",
            options=[{"label": "MWh absolus", "value": "absolu"},
                     {"label": "% d'écart à la moyenne", "value": "ecart"}],
            value="absolu", inline=True, className="radio-pills",
        ),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz2",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "L'hiver est une autre planète",
        "Les fins de semaine de février culminent à près de 20 MWh/j alors que les étés plafonnent sous 8 MWh/j. "
        "Décembre voit une anomalie liée aux fêtes — les jours fériés battent tous les records.",
        "📅",
    ),
])


# ─────────────────────────────────────────────────────────────
# Chapter 4 — Profils horaires (Viz 3)
# ─────────────────────────────────────────────────────────────
viz3_section = html.Section(id="viz3", className="content-section", children=[
    chapter(4, "Profils horaires"),
    html.H2("À quelles heures la demande explose-t-elle ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Chaque saison présente deux pics — matin et soir — qui coïncident précisément ",
            "avec les fenêtres ciblées par les défis Hilo (6h–10h et 17h–21h). ",
            "Comparez les postes pour voir si leurs profils diffèrent.",
        ]),
    ]),
    html.Div(className="controls-bar", children=[
        html.Label("Poste électrique :", className="control-label"),
        dcc.RadioItems(
            id="viz3-poste",
            options=[{"label": p, "value": p} for p in ("Tous", "A", "B", "C")],
            value="Tous", inline=True, className="radio-pills",
        ),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz3",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "Deux pointes, une fenêtre d'action",
        "En hiver, les pics atteignent ~230 kWh/h contre ~85 en été — un ratio de 2,7×. "
        "Les pics rouges sur les roses correspondent aux 6 heures ciblées par les défis Hilo. "
        "C'est là que le programme doit frapper.",
        "⏰",
    ),
])


# ─────────────────────────────────────────────────────────────
# Chapter 5 — Impact GLD + exploration d'événement (Viz 4, 5, 6 cross-linked)
# ─────────────────────────────────────────────────────────────
# Build scannable event labels with visual cues (emoji) for réussi/échoué + matin/soir
def _event_label(row):
    status = "✅" if row["reduction_pct"] >= 20 else ("🟡" if row["reduction_pct"] >= 0 else "❌")
    moment = "🌅" if row["periode_jour"] == "matin" else "🌙"
    date_only = row["date_str"].split("-matin")[0].split("-soir")[0]
    return (f"{status} {moment}  {date_only}  ·  "
            f"{row['heure_debut']}h-{row['heure_fin']+1}h  ·  "
            f"{row['temperature_ext']:+.0f}°C  ·  "
            f"réd. {row['reduction_pct']:+.0f}%")

event_options = [{"label": "📊  Moyenne sur tous les événements (vue par défaut)", "value": "__all__"}]
# sort events best→worst so the top of the list shows the program at its best
for _, row in EVENTS.sort_values("reduction_pct", ascending=False).iterrows():
    event_options.append({"label": _event_label(row), "value": row["date_str"]})


viz4_section = html.Section(id="viz4", className="content-section", children=[
    chapter(5, "L'impact du programme"),
    html.H2("Le programme Hilo réduit-il vraiment la consommation ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Voici le cœur de l'analyse. Pour chaque événement GLD, nous comparons la ",
            "consommation réelle à un ", html.Strong("baseline"),
            " (mêmes heures, mêmes postes, mais en hiver sans défi). ",
            "L'aire verte visualise l'énergie économisée.",
        ]),
        html.P(className="helper-note", children=[
            html.Span("💡", className="helper-icon"),
            html.Span([
                "Par défaut, les courbes montrent la ", html.Strong("moyenne sur les 46 événements"),
                ". Pour explorer un cas précis, utilisez le sélecteur ci-dessous ",
                html.Em("ou"), " cliquez un point dans le graphique du chapitre 6."
            ]),
        ]),
    ]),
    html.Div(className="event-picker-wrap", children=[
        html.Div(className="event-picker-header", children=[
            html.Div(className="picker-left", children=[
                html.Span("🎯", className="picker-emoji"),
                html.Div(children=[
                    html.Div("Événement affiché", className="picker-title"),
                    html.Div("Tous les événements (moyenne)",
                             id="picker-subtitle", className="picker-subtitle"),
                ]),
            ]),
            html.Button("↺ Voir la moyenne", id="event-reset", n_clicks=0,
                        className="reset-btn"),
        ]),
        dcc.Dropdown(
            id="event-picker",
            options=event_options, value="__all__",
            clearable=False, className="event-dropdown",
            placeholder="Choisir un événement spécifique…",
        ),
        html.Div(className="picker-legend", children=[
            html.Span("✅ réussi (>20%)"), html.Span("·"),
            html.Span("🟡 modéré (0–20%)"), html.Span("·"),
            html.Span("❌ contre-productif (<0%)"), html.Span("·"),
            html.Span("🌅 matin  ·  🌙 soir"),
        ]),
        html.Div(id="event-badge", className="event-badge-wrap"),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz4",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "Réduction ≈ 33% en moyenne · mais attention au rebond",
        "La baisse est nette pendant la phase de défi. Le préchauffage facultatif crée une hausse "
        "de consommation avant 0h (stockage thermique). À la fin du défi (+4h), un rebond marqué "
        "est inévitable car les logements doivent retrouver leur consigne.",
        "⚡",
    ),
])


viz5_section = html.Section(id="viz5", className="content-section", children=[
    chapter(6, "Quand le programme fonctionne-t-il ?"),
    html.H2("L'efficacité varie-t-elle selon la température et l'heure ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Tous les événements ne se valent pas. Dans les températures modérées (−15 à 0°C), le programme ",
            "est massivement efficace. En dessous de −20°C, il perd sa capacité de réduction ",
            "— les bâtiments luttent juste pour conserver leur température.",
        ]),
        html.P([
            html.Em("👆 Astuce : "),
            "cliquez un point sur le graphique pour charger cet événement dans les visualisations précédente et suivante.",
        ]),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz5",
                                             figure=viz5.get_figure(),
                                             config={"displayModeBar": False}))]),
    insight_box(
        "Le seuil des −20°C",
        f"Sur {KPI['n_events']} événements, {100 - KPI['pct_events_positive']:.0f}% sont contre-productifs "
        "(réduction < 0%). Ils surviennent presque tous par grand froid extrême : le chauffage compensatoire "
        "annule l'effet du défi.",
        "🧊",
    ),
])


viz6_section = html.Section(id="viz6", className="content-section", children=[
    chapter(7, "Le mécanisme"),
    html.H2("Comment les thermostats Hilo réagissent-ils ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Le programme ne pourrait pas fonctionner sans la ",
            html.Strong("réactivité des thermostats"),
            ". Dès 0h, la consigne plonge de ~4°C. La température intérieure, elle, suit avec un délai "
            "— c'est l'inertie thermique des bâtiments, et c'est ce qui préserve le confort.",
        ]),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz6",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "Réactivité rapide, confort préservé",
        "La chute de consigne est brutale (instantanée), mais la température intérieure ne suit "
        "qu'à moitié, protégeant le confort des participants. L'écart Δ entre consigne et intérieure "
        "pendant le défi est la signature de l'inertie thermique.",
        "🌡️",
    ),
])


# ─────────────────────────────────────────────────────────────
# Chapter 8 — Participation (Viz 7)
# ─────────────────────────────────────────────────────────────
viz7_section = html.Section(id="viz7", className="content-section", children=[
    chapter(8, "Le rôle de l'échelle"),
    html.H2("Plus de participants = plus de réduction ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Chaque événement est représenté par un point. À gauche, selon le nombre de clients ; ",
            "à droite, selon le nombre de thermostats. Les ",
            html.Strong("points rouges"), " sont les événements contre-productifs.",
        ]),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Graph(id="graph-viz7",
                                 figure=viz7.get_figure(),
                                 config={"displayModeBar": False})]),
    insight_box(
        "Les points de contrôle priment",
        "La corrélation est plus forte avec le nombre de thermostats (r ≈ 0,57) qu'avec le nombre "
        "de clients (r ≈ 0,34) : c'est bien le nombre d'actionneurs — pas de foyers — qui détermine "
        "la capacité de modulation.",
        "🔌",
    ),
])


# ─────────────────────────────────────────────────────────────
# Chapter 9 — Postes (Viz 8)
# ─────────────────────────────────────────────────────────────
viz8_section = html.Section(id="viz8", className="content-section", children=[
    chapter(9, "Hétérogénéité des postes"),
    html.H2("Les trois postes se comportent-ils pareil ?"),
    html.Div(className="section-body", children=[
        html.P([
            "Les postes A, B et C agrègent des clientèles différentes. ",
            "En absolu, le poste C pèse presque autant que A et B réunis. ",
            "Mais ", html.Em("par client"), ", les profils se rapprochent — ",
            "c'est bien une question de volume, pas de comportement.",
        ]),
    ]),
    html.Div(className="controls-bar", children=[
        html.Label("Mode d'affichage :", className="control-label"),
        dcc.RadioItems(
            id="viz8-mode",
            options=[{"label": "Consommation absolue", "value": "absolu"},
                     {"label": "Par client connecté", "value": "normalise"}],
            value="absolu", inline=True, className="radio-pills",
        ),
    ]),
    html.Div(className="graph-container",
             children=[dcc.Loading(dcc.Graph(id="graph-viz8",
                                             config={"displayModeBar": False}))]),
    insight_box(
        "Saisonnalité universelle",
        "Malgré les écarts absolus, les trois postes suivent la même courbe saisonnière : "
        "maximum en hiver, minimum en été. Le chauffage électrique est le déterminant commun.",
        "🏘️",
    ),
])


# ─────────────────────────────────────────────────────────────
# Synthèse finale
# ─────────────────────────────────────────────────────────────
synthese = html.Section(id="synthese", className="content-section synthesis", children=[
    chapter(10, "Ce que nous avons appris"),
    html.H2("Synthèse"),
    html.Div(className="synthesis-grid", children=[
        html.Div(className="synthesis-card primary", children=[
            html.H3("✅ Le programme fonctionne"),
            html.P([
                "En moyenne ", html.Strong(f"{KPI['mean_reduction_pct']:.0f}% de réduction"),
                f" sur {KPI['n_events']} événements, avec des pics à {KPI['best_reduction_pct']:.0f}%. ",
                f"{KPI['pct_events_positive']:.0f}% des événements produisent une baisse nette."
            ]),
        ]),
        html.Div(className="synthesis-card warning", children=[
            html.H3("⚠️ Limite thermique à −20°C"),
            html.P([
                "Le programme perd son efficacité lors des grands froids extrêmes. ",
                "Repenser la stratégie ces jours-là : préchauffage plus agressif ou fenêtres plus courtes."
            ]),
        ]),
        html.Div(className="synthesis-card", children=[
            html.H3("🔄 L'effet rebond est réel"),
            html.P([
                "À la fin du défi (+4h), un rebond de ~53% par rapport à la référence est observé. ",
                "Il doit être intégré dans la planification réseau pour ne pas créer un nouveau pic."
            ]),
        ]),
        html.Div(className="synthesis-card", children=[
            html.H3("📈 Scaling par thermostats"),
            html.P([
                "L'impact dépend du nombre de ", html.Strong("thermostats"),
                " connectés (r = 0,57), pas du nombre de foyers. ",
                "Recommandation : équiper davantage les clients existants avant d'en recruter."
            ]),
        ]),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Team footer
# ─────────────────────────────────────────────────────────────
equipe = html.Section(id="equipe", className="content-section team-section", children=[
    html.H2("Équipe 25 · INF8808 · Hiver 2026"),
    html.Div(className="team-grid", children=[
        html.Div(className="team-card", children=[html.P(n)])
        for n in ("Ayat Wissem", "Boutera Hamza", "Diarra Halima Sadia",
                  "Letieu Tchemeni Axelle Stévia", "Nguemegne Temena Loïc")
    ]),
    html.Footer(className="footer", children=[
        html.P("Données : Hydro-Québec — Programme Hilo (GLD) — CC BY-NC 4.0"),
        html.P("Polytechnique Montréal — INF8808 Visualisation de données — Hiver 2026"),
    ]),
])


# ─────────────────────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────────────────────
app.layout = html.Div(id="app-container", children=[
    sidebar,
    html.Div(id="main-content", children=[
        hero,
        contexte,
        viz1_section,
        viz2_section,
        viz3_section,
        viz4_section,
        viz5_section,
        viz6_section,
        viz7_section,
        viz8_section,
        synthese,
        equipe,
    ]),
])


# ─────────────────────────────────────────────────────────────
# CALLBACKS — real interactivity
# ─────────────────────────────────────────────────────────────
@app.callback(Output("graph-viz1a", "figure"), Input("viz1-saison", "value"))
def _cb_viz1a(saison):
    return viz1a.get_figure(saison)


@app.callback(Output("graph-viz1b", "figure"), Input("viz1-saison", "value"))
def _cb_viz1b(saison):
    if saison == "Toutes":
        return viz1b.get_figure()
    return viz1b.get_figure(saisons=[saison])


@app.callback(Output("graph-viz2", "figure"), Input("viz2-mode", "value"))
def _cb_viz2(mode):
    return viz2.get_figure(mode)


@app.callback(Output("graph-viz3", "figure"), Input("viz3-poste", "value"))
def _cb_viz3(poste):
    return viz3.get_figure(poste)


# Cross-linking: clicking a point on viz5 populates the picker, which drives viz4 + viz6.
# Single source of truth = the picker's value. No intermediate store → no feedback loop.
@app.callback(
    Output("event-picker", "value"),
    Input("graph-viz5", "clickData"),
    Input("event-reset", "n_clicks"),
    prevent_initial_call=True,
)
def _cb_set_event(click_data, reset_clicks):
    trigger = dash.ctx.triggered_id if hasattr(dash, "ctx") else None
    if trigger == "event-reset":
        return "__all__"
    if trigger == "graph-viz5" and click_data and click_data.get("points"):
        return click_data["points"][0]["customdata"][0]
    return dash.no_update


@app.callback(
    [Output("graph-viz4", "figure"),
     Output("graph-viz6", "figure"),
     Output("event-badge", "children"),
     Output("picker-subtitle", "children")],
    Input("event-picker", "value"),
)
def _cb_event_views(event_value):
    if not event_value or event_value == "__all__":
        return (
            viz4.get_figure(None),
            viz6.get_figure(None),
            html.Div(),   # empty badge
            f"Tous les événements ({KPI['n_events']} au total · moyenne)",
        )
    row = EVENTS[EVENTS["date_str"] == event_value]
    if row.empty:
        return viz4.get_figure(None), viz6.get_figure(None), html.Div(), "—"
    r = row.iloc[0]
    date_only = r["date_str"].split("-matin")[0].split("-soir")[0]
    period_label = "pointe matinale 🌅" if r["periode_jour"] == "matin" else "pointe du soir 🌙"
    subtitle = f"{date_only} · {period_label} ({r['heure_debut']}h → {r['heure_fin']+1}h) · {r['temperature_ext']:+.0f}°C"
    badge_class = "event-badge good" if r["reduction_pct"] >= 0 else "event-badge bad"
    badge = html.Div(className=badge_class, children=[
        html.Div(className="badge-main", children=[
            html.Span(f"{r['reduction_pct']:+.1f}%", className="badge-number"),
            html.Span("de réduction", className="badge-suffix"),
        ]),
        html.Div(className="badge-meta", children=[
            html.Span(f"🌡️ {r['temperature_ext']:+.1f}°C"),
            html.Span(f"👥 {r['tstats_moy']} thermostats"),
            html.Span(f"🕐 {r['heure_debut']}h → {r['heure_fin']+1}h"),
            html.Span(f"🔆 {r['periode_jour']}"),
        ]),
    ])
    return viz4.get_figure(event_value), viz6.get_figure(event_value), badge, subtitle


@app.callback(Output("graph-viz8", "figure"), Input("viz8-mode", "value"))
def _cb_viz8(mode):
    return viz8.get_figure(mode)


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Dash ≥2.17 uses .run(); older versions use .run_server() — both work on older .run()
    app.run(debug=True, port=8050)
