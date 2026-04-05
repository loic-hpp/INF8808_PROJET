# -*- coding: utf-8 -*-
"""
    Gestion de la demande électrique lors des pics hivernaux
    INF8808 - Visualisation de données - Hiver 2026
    Équipe 25 - Plotly
"""

import dash
from dash import dcc, html

import graphiques.viz1a as viz1a
import graphiques.viz1b as viz1b
import graphiques.viz2 as viz2
import graphiques.viz3 as viz3
import graphiques.viz4 as viz4
import graphiques.viz5 as viz5
import graphiques.viz6 as viz6
import graphiques.viz7 as viz7
import graphiques.viz8 as viz8

app = dash.Dash(__name__)
app.title = "Hydro-Québec — Gestion de la demande électrique | INF8808"

# ── Build all figures ──
fig1a = viz1a.get_figure()
fig1b = viz1b.get_figure()
fig2 = viz2.get_figure()
fig3 = viz3.get_figure()
fig4 = viz4.get_figure()
fig5 = viz5.get_figure()
fig6 = viz6.get_figure()
fig7 = viz7.get_figure()
fig8 = viz8.get_figure()

# ── Sidebar Navigation ──
sidebar = html.Nav(id="sidebar", children=[
    html.Div(className="sidebar-logo", children=[
        html.Img(src="/assets/favicon.ico", style={"width": "40px", "marginRight": "10px"}),
        html.Span("Hydro-Québec", className="sidebar-brand"),
    ]),
    html.Ul([
        html.Li(html.A("Accueil", href="#hero")),
        html.Li(html.A("Contexte", href="#contexte")),
        html.Li(html.A("Météo & Conso", href="#viz1")),
        html.Li(html.A("Heatmap", href="#viz2")),
        html.Li(html.A("Profils horaires", href="#viz3")),
        html.Li(html.A("Événements GLD", href="#viz4")),
        html.Li(html.A("Efficacité GLD", href="#viz5")),
        html.Li(html.A("Thermostats", href="#viz6")),
        html.Li(html.A("Clients connectés", href="#viz7")),
        html.Li(html.A("Postes A/B/C", href="#viz8")),
        html.Li(html.A("Équipe", href="#equipe")),
    ]),
])

# ── Hero Section ──
hero = html.Section(id="hero", className="hero-section", children=[
    html.Div(className="hero-content", children=[
        html.H1("Gestion de la demande électrique lors des pics hivernaux"),
    ]),
])

# ── Context Section ──
contexte = html.Section(id="contexte", className="content-section", children=[
    html.H2("Mise en contexte"),
    html.Div(className="section-body", children=[
        html.H3("Contexte"),
        html.P(
            "Chaque hiver, les périodes de grand froid entraînent une forte hausse de la "
            "consommation d'électricité au Québec. Hydro-Québec, distributeur d'électricité provincial, "
            "doit alors s'assurer que la production et la demande restent équilibrées en temps réel sur le "
            "réseau afin d'éviter les surcharges et des coûts supplémentaires."
        ),
        html.P(
            "Pour limiter ces pointes, l'entreprise a mis en place un programme de gestion locale "
            "de la demande de puissance (GLD). Des clients volontaires, résidentiels et commerciaux, "
            "utilisent des thermostats intelligents (programme Hilo) qui permettent d'ajuster légèrement "
            "leur chauffage lors des périodes critiques. Ces petits ajustements, répartis sur de nombreux "
            "participants, aident à stabiliser le réseau."
        ),
        html.P(
            "Le projet vise donc à analyser les données de consommation énergétique afin de "
            "mieux comprendre l'effet de la météo sur l'utilisation d'électricité et d'observer comment les "
            "habitudes changent avant, pendant et après les événements de pointe."
        ),
        html.H3("Question centrale"),
        html.Blockquote(
            "Quel est l'impact des conditions météorologiques sur la consommation électrique de la "
            "clientèle participant au programme de gestion locale de la demande de puissance "
            "d'Hydro-Québec, et comment ce comportement évolue-t-il avant, pendant et après les "
            "événements de pointe hivernaux ?"
        ),
        html.H3("Public cible"),
        html.P(
            "Le public principal de cette visualisation est constitué des gestionnaires et analystes "
            "d'Hydro-Québec impliqués dans le programme de gestion locale de la demande (GLD). "
            "Ces professionnels cherchent à évaluer l'efficacité des événements GLD, à comprendre "
            "l'influence des conditions météorologiques sur la consommation électrique et à analyser les "
            "variations du comportement des participants avant, pendant et après les périodes de pointe "
            "hivernales."
        ),
    ]),
])


def viz_section(section_id, title, questions, description, graph_id, figure,
                discussion, interactions=None):
    """Helper to build a visualization section."""
    children = [
        html.H2(title),
        html.Div(className="section-body", children=[
            html.Div(className="questions-box", children=[
                html.H4("Questions cibles"),
                html.Ul([html.Li(q) for q in questions]),
            ]),
            html.H3("Description"),
            html.P(description),
        ]),
    ]
    if interactions:
        children.append(
            html.Div(className="section-body", children=[
                html.H3("Interactions"),
                html.P(interactions),
            ])
        )
    children.append(
        html.Div(className="graph-container", children=[
            dcc.Graph(id=graph_id, figure=figure, config={"displayModeBar": True}),
        ])
    )
    children.append(
        html.Div(className="section-body", children=[
            html.H3("Discussion"),
            html.P(discussion),
        ])
    )
    return html.Section(id=section_id, className="content-section", children=children)


# ── Visualization Sections ──

viz1_section = viz_section(
    "viz1",
    "Visualisation 1 — Corrélation météo et consommation",
    [
        "Quelles variables météorologiques présentent les corrélations les plus fortes avec la consommation électrique ?",
        "Comment la consommation varie-t-elle lorsque la température extérieure fluctue ?",
        "L'effet du vent amplifie-t-il la consommation lors des grands froids ?",
    ],
    "Cette visualisation est composée de deux graphiques complémentaires. "
    "Le premier graphique est un graphique en lollipop horizontal. Chaque point représente "
    "une variable météorologique et sa position sur l'axe des abscisses correspond au coefficient "
    "de corrélation de Pearson avec la consommation électrique totale. La couleur encode le signe "
    "de la corrélation : rouge pour une corrélation négative et vert pour une corrélation positive. "
    "Le deuxième graphique est un ensemble de quatre nuages de points disposés en grille 2\u00d72, "
    "un pour chaque variable météorologique principale.",
    "graph-viz1a",
    fig1a,
    "Le graphique en lollipop révèle que la température extérieure est la variable la plus corrélée "
    "avec la consommation électrique, une corrélation forte et négative (r = \u22120,72) : plus la "
    "température baisse, plus la consommation électrique augmente. La vitesse du vent et "
    "l'humidité relative présentent des corrélations positives mais faibles. "
    "Les nuages de points confirment ces relations. La température extérieure montre une relation "
    "non-linéaire nette : en dessous de 0\u00b0C, la consommation est systématiquement élevée. "
    "La vitesse du vent montre une tendance à la hausse de consommation avec l'intensité des "
    "rafales, suggérant que le facteur éolien amplifie la perception du froid.",
    "Dans les nuages de points, au survol d'un point, une info-bulle affiche la date, la valeur de la "
    "variable météorologique correspondante et la consommation journalière totale en MWh.",
)

# Add viz1b graph to viz1_section
viz1_section.children.insert(-1, html.Div(className="graph-container", children=[
    dcc.Graph(id="graph-viz1b", figure=fig1b, config={"displayModeBar": True}),
]))

viz2_section = viz_section(
    "viz2",
    "Visualisation 2 — Heatmap calendrier",
    [
        "Les relations entre météo et consommation sont-elles stables selon les saisons ?",
        "La consommation diffère-t-elle entre jours ouvrables, jour férié et fin de semaine ?",
    ],
    "Cette visualisation est une carte de chaleur calendrier. Pour chaque mois de l'année "
    "et pour chaque jour de la semaine, une cellule représente la consommation électrique moyenne en kWh. "
    "L'intensité de la couleur varie selon une rampe commune à l'ensemble du graphique. "
    "Sous les sept lignes de jours, trois lignes de résumé sont ajoutées : la moyenne des jours ouvrables, "
    "la moyenne des fins de semaine, la moyenne des jours fériés, et la moyenne mensuelle globale.",
    "graph-viz2",
    fig2,
    "Les mois d'hiver (décembre, janvier, février) affichent une consommation nettement "
    "supérieure aux mois d'été, traduisant la forte dépendance au chauffage électrique dans la "
    "région de Montréal. Les journées de fin de semaine en février présentent les valeurs les plus "
    "élevées (19,7 MWh), reflétant la présence accrue à domicile par grand froid. "
    "La ligne des jours fériés révèle une consommation particulièrement élevée en décembre, "
    "cohérente avec les fêtes de fin d'année.",
)

viz3_section = viz_section(
    "viz3",
    "Visualisation 3 — Profils horaires par saison",
    [
        "Comment les profils horaires de consommation varient-ils selon la saison ?",
    ],
    "Cette visualisation est composée de quatre graphiques polaires en rose chart, un pour "
    "chaque saison (Hiver, Printemps, Été, Automne), disposés en grille 2\u00d72. Chaque graphique "
    "est divisé en 24 segments radiaux correspondant aux 24 heures de la journée. "
    "La longueur de chaque segment est proportionnelle à la consommation électrique moyenne. "
    "Les quatre graphiques partagent la même échelle radiale (iso-échelle).",
    "graph-viz3",
    fig3,
    "Deux pics de consommation sont communs à toutes les saisons : un le matin autour de "
    "7h\u20139h et un en soirée autour de 17h\u201319h. Ces créneaux coïncident avec les heures de "
    "pointe ciblées par les défis Hilo (6h\u201310h et 17h\u201321h). "
    "En hiver, ces pics sont nettement plus prononcés. La différence d'amplitude entre l'hiver "
    "(230 kWh/h en moyenne) et l'été (85 kWh/h) illustre clairement l'impact du chauffage "
    "électrique sur la demande.",
    "Au survol d'un segment, une info-bulle affiche l'heure, la saison et la consommation "
    "électrique moyenne en kWh.",
)

viz4_section = viz_section(
    "viz4",
    "Visualisation 4 — Événements GLD",
    [
        "La consommation diminue-t-elle pendant les événements GLD ?",
        "Existe-t-il un effet rebond immédiatement après un événement GLD ?",
    ],
    "Ce graphique linéaire temporel présente deux courbes sur une fenêtre de \u22124h à +6h autour "
    "du début d'un événement GLD. La courbe bleue représente la consommation réelle des clients "
    "Hilo lors des événements GLD. La courbe grise représente la consommation de référence. "
    "La période de préchauffage optionnel est mise en évidence par un fond ambré, "
    "et la période de défi actif par un fond rouge pâle.",
    "graph-viz4",
    fig4,
    "La chute de consommation est clairement visible dès le début du défi et se maintient sur "
    "toute la durée de la phase de réduction, avec une baisse moyenne d'environ 33% par "
    "rapport à la référence. Le préchauffage optionnel se traduit par une hausse notable avant le "
    "défi. Après la fin du défi, un effet rebond marqué est observé (environ +53% par rapport "
    "à la référence), inévitable puisque les logements doivent retrouver leur température nominale.",
    "Au survol d'un point, une info-bulle affiche l'heure relative, la consommation réelle et la "
    "consommation de référence.",
)

viz5_section = viz_section(
    "viz5",
    "Visualisation 5 — Efficacité GLD selon température et heure",
    [
        "L'efficacité des événements GLD varie-t-elle selon la température extérieure et le moment de la journée ?",
    ],
    "Ce nuage de points a pour axe des abscisses la température extérieure en \u00b0C et pour "
    "axe des ordonnées l'heure du défi GLD. Chaque point correspond à une heure d'un événement "
    "GLD. La couleur encode le pourcentage de réduction de consommation, selon une rampe "
    "allant du rouge (réduction négative) au vert (forte réduction).",
    "graph-viz5",
    fig5,
    "La visualisation met en évidence une relation entre la température et l'efficacité du "
    "programme : les points verts se concentrent dans les plages de températures modérées "
    "(\u221215\u00b0C à 0\u00b0C), tandis que les points rouges apparaissent lors des grands froids "
    "(en dessous de \u221220\u00b0C). La pointe matinale semble légèrement plus favorable à "
    "l'efficacité du programme que la pointe en soirée.",
    "Au survol d'un point, une info-bulle affiche la date, l'heure du défi, la température "
    "extérieure et le pourcentage de réduction.",
)

viz6_section = viz_section(
    "viz6",
    "Visualisation 6 — Comportement des thermostats",
    [
        "Les participants réduisent-ils leur température de consigne pendant un défi ?",
        "La température intérieure diminue-t-elle pendant la phase de réduction ?",
    ],
    "Ce graphique linéaire temporel présente, sur une fenêtre de \u22123h à +5h autour du début "
    "du défi, la température de consigne moyenne (courbe rouge) et la température intérieure "
    "mesurée moyenne (courbe bleue en pointillé). Les données sont agrégées sur les 15 premiers "
    "événements GLD.",
    "graph-viz6",
    fig6,
    "La température de consigne chute brusquement dès le début du défi, de près de 4\u00b0C "
    "en moyenne, témoignant de la réactivité des thermostats intelligents Hilo. La température "
    "intérieure mesurée suit avec un retard, reflétant l'inertie thermique naturelle des "
    "bâtiments résidentiels. Après +4h, la consigne remonte progressivement. "
    "Ces courbes confirment que les thermostats Hilo répondent efficacement tout en maintenant "
    "un confort thermique acceptable pour les participants.",
    "Au survol d'un point, une info-bulle affiche l'heure relative, la température de consigne "
    "et la température intérieure mesurée.",
)

viz7_section = viz_section(
    "viz7",
    "Visualisation 7 — Clients connectés et réduction GLD",
    [
        "Le nombre de clients connectés influence-t-il l'ampleur de la réduction observée ?",
    ],
    "Cette visualisation est composée de deux nuages de points côte à côte. L'axe des "
    "ordonnées représente le pourcentage de réduction de consommation par événement GLD. "
    "L'axe des abscisses représente respectivement le nombre moyen de clients connectés "
    "(panneau gauche) et le nombre moyen de thermostats connectés (panneau droit). "
    "Une droite de tendance est ajoutée sur chacun des panneaux.",
    "graph-viz7",
    fig7,
    "Le nombre de thermostats connectés présente une corrélation modérément positive avec "
    "l'efficacité du programme (r = 0,57) : les événements où davantage de thermostats sont "
    "actifs tendent à produire une réduction plus importante. Le nombre de clients présente une "
    "corrélation plus faible (r = 0,34). Les points négatifs correspondent aux événements "
    "survenus lors des grands froids, où le programme perd son efficacité.",
    "Au survol d'un point, une info-bulle affiche la date de l'événement, le nombre de clients "
    "et de thermostats connectés et le pourcentage de réduction.",
)

viz8_section = viz_section(
    "viz8",
    "Visualisation 8 — Profils par poste",
    [
        "Les profils de consommation varient-ils selon les postes A, B et C ?",
    ],
    "Ce graphique à barres groupées présente, pour chaque saison, trois barres côte à côte "
    "représentant la consommation électrique horaire moyenne de chaque poste "
    "(A en bleu, B en vert, C en bleu clair). La valeur exacte en kWh est affichée au-dessus "
    "de chaque barre. Les données sont agrégées sur la période 2022\u20132024.",
    "graph-viz8",
    fig8,
    "Le Poste C présente une consommation nettement supérieure aux deux autres, environ "
    "2,3 fois celle des postes A et B, ce qui suggère qu'il regroupe un nombre plus élevé de "
    "clients ou une clientèle à plus forte consommation individuelle. Les postes A et B affichent "
    "des niveaux comparables. Malgré ces écarts, les trois postes suivent la même saisonnalité : "
    "la consommation est maximale en hiver et atteint son minimum en été, confirmant que "
    "le chauffage électrique est le principal déterminant de la demande.",
)

# ── Team Section ──
equipe = html.Section(id="equipe", className="content-section team-section", children=[
    html.H2("Équipe 25"),
    html.P("INF8808 — Visualisation de données — Hiver 2026",
           className="team-subtitle"),
    html.Div(className="team-grid", children=[
        html.Div(className="team-card", children=[html.P("Ayat Wissem")]),
        html.Div(className="team-card", children=[html.P("Boutera Hamza")]),
        html.Div(className="team-card", children=[html.P("Diarra Halima Sadia")]),
        html.Div(className="team-card", children=[html.P("Letieu Tchemeni Axelle Stévia")]),
        html.Div(className="team-card", children=[html.P("Nguemegne Temena Loïc")]),
    ]),
    html.Footer(children=[
        html.P("Données : Hydro-Québec — Programme Hilo (GLD) — CC BY-NC 4.0"),
        html.P("Polytechnique Montréal — INF8808 — Hiver 2026"),
    ]),
])

# ── Main Layout ──
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
        equipe,
    ]),
])
