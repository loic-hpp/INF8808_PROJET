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
        html.Li(html.A("Météo & Consommation", href="#viz1")),
        html.Li(html.A("Saisonnalité", href="#viz2")),
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
            "habitudes changent avant, pendant et après les événements de pointe. Ce travail se concentre donc sur la question suivante :"
        ),
        html.Blockquote(
            "Quel est l'impact des conditions météorologiques sur la consommation électrique de la "
            "clientèle participant au programme de gestion locale de la demande de puissance "
            "d'Hydro-Québec, et comment ce comportement évolue-t-il avant, pendant et après les "
            "événements de pointe hivernaux ?"
        ),
    ]),
])


# ── Visualization Sections ──

viz1_section = html.Section(id="viz1", className="content-section", children=[
    html.H2("Quelle est la corrélation entre la météo et la consommation générale ?"),
    html.Div(className="section-body", children=[
        html.P(
            "Le graphique en lollipop révèle que la température extérieure est la variable la plus corrélée "
            "avec la consommation électrique, une corrélation forte et négative (r = \u22120,72) : plus la "
            "température baisse, plus la consommation électrique augmente. La vitesse du vent et "
            "l'humidité relative présentent des corrélations positives mais faibles "
            "(respectivement +0,08 et +0,1)."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz1a", figure=fig1a, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "Les nuages de points confirment et détaillent ces relations. La température extérieure "
            "montre une relation non-linéaire nette : en dessous de 0\u00b0C, la consommation est "
            "systématiquement élevée, tandis qu'au-dessus de 10\u00b0C elle se stabilise à des niveaux bas. "
            "La vitesse du vent montre une tendance à la hausse de consommation avec l'intensité des "
            "rafales, suggérant que le facteur éolien amplifie la perception du froid. Les précipitations "
            "de neige sont associées à des consommations généralement supérieures à la moyenne des "
            "journées sans neige, en raison de la coïncidence fréquente neige\u2013grand froid. L'humidité "
            "relative présente une relation plus diffuse et moins directe avec la consommation."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz1b", figure=fig1b, config={"displayModeBar": True}),
    ]),
])

viz2_section = html.Section(id="viz2", className="content-section", children=[
    html.H2("Les relations entre météo et consommation sont-elles stables selon les saisons ?"),
    html.Div(className="section-body", children=[
        html.P(
            "Les mois d'hiver (décembre, janvier, février) affichent une consommation nettement "
            "supérieure aux mois d'été, traduisant la forte dépendance au chauffage électrique dans la "
            "région de Montréal. Les journées de fin de semaine en février présentent les valeurs les plus "
            "élevées (19,7 MWh), reflétant la présence accrue à domicile par grand froid."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz2", figure=fig2, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "La ligne des jours fériés révèle une consommation particulièrement élevée en décembre, "
            "cohérente avec les fêtes de fin d'année. La différence entre jours ouvrables et fins de "
            "semaine est faible en été mais s'accentue légèrement en hiver, où la présence à domicile "
            "amplifie la demande résidentielle."
        ),
    ]),
])

viz3_section = html.Section(id="viz3", className="content-section", children=[
    html.H2("Comment les profils horaires de consommation varient-ils selon la saison ?"),
    html.Div(className="section-body", children=[
        html.P(
            "Deux pics de consommation sont communs à toutes les saisons : un le matin autour de "
            "7h\u20139h et un en soirée autour de 17h\u201319h. Ces créneaux coïncident avec les heures de "
            "pointe ciblées par les défis Hilo (6h\u201310h et 17h\u201321h), confirmant la pertinence de cette "
            "fenêtre d'intervention."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz3", figure=fig3, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "En hiver, ces pics sont nettement plus prononcés. La différence d'amplitude entre l'hiver "
            "(230 kWh/h en moyenne) et l'été (85 kWh/h) illustre clairement l'impact du chauffage "
            "électrique sur la demande et justifie la concentration des événements GLD en période "
            "hivernale."
        ),
    ]),
])

viz4_section = html.Section(id="viz4", className="content-section", children=[
    html.H2("La consommation diminue-t-elle pendant les événements GLD ?"),
    html.Div(className="section-body", children=[
        html.P(
            "La chute de consommation est clairement visible dès le début du défi et se maintient sur "
            "toute la durée de la phase de réduction, avec une baisse moyenne d'environ 33% par "
            "rapport à la référence. Ce résultat confirme l'efficacité du programme Hilo pour atténuer les "
            "pointes hivernales."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz4", figure=fig4, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "Le préchauffage optionnel (\u22122h à 0h) se traduit par une hausse notable de la consommation "
            "avant le défi, cohérente avec la stratégie de stockage thermique. Après la fin du défi (+4h), "
            "un effet rebond marqué est observé (environ +53% par rapport à la référence), inévitable "
            "puisque les logements doivent retrouver leur température nominale."
        ),
    ]),
])

viz5_section = html.Section(id="viz5", className="content-section", children=[
    html.H2("L'efficacité des événements GLD varie-t-elle selon la température extérieure "
            "et le moment de la journée ?"),
    html.Div(className="section-body", children=[
        html.P(
            "La visualisation met en évidence une relation entre la température et l'efficacité du "
            "programme : les points verts se concentrent dans les plages de températures modérées "
            "(\u221215\u00b0C à 0\u00b0C), tandis que les points rouges apparaissent lors des grands froids "
            "(en dessous de \u221220\u00b0C). En dessous de \u221220\u00b0C, les bâtiments peinent à maintenir "
            "leur température même en mode réduit, ce qui entraîne un effort de chauffage compensatoire."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz5", figure=fig5, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "La pointe matinale semble légèrement plus favorable à l'efficacité du programme que la "
            "pointe en soirée, bien que les données sur les défis du soir soient moins nombreuses."
        ),
    ]),
])

viz6_section = html.Section(id="viz6", className="content-section", children=[
    html.H2("Les participants réduisent-ils leur température de consigne pendant un défi ?"),
    html.Div(className="section-body", children=[
        html.P(
            "La température de consigne (rouge) chute brusquement dès le début du défi, de près de 4\u00b0C "
            "en moyenne, témoignant de la réactivité des thermostats intelligents Hilo. La température "
            "intérieure mesurée (bleue) suit avec un retard, reflétant l'inertie thermique naturelle des "
            "bâtiments résidentiels, et la demande est bien réduite sur l'ensemble de la fenêtre de défi."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz6", figure=fig6, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "Après +4h, la consigne remonte progressivement, entraînant une récupération graduelle de "
            "la température intérieure. Ces courbes confirment que les thermostats Hilo répondent "
            "efficacement tout en maintenant un confort thermique acceptable pour les participants."
        ),
    ]),
])

viz7_section = html.Section(id="viz7", className="content-section", children=[
    html.H2("Le nombre de clients connectés influence-t-il l'ampleur de la réduction observée ?"),
    html.Div(className="section-body", children=[
        html.P(
            "Le nombre de thermostats connectés présente une corrélation modérément positive avec "
            "l'efficacité du programme (r = 0,57) : les événements où davantage de thermostats sont "
            "actifs tendent à produire une réduction plus importante. Le nombre de clients présente une "
            "corrélation plus faible (r = 0,34), suggérant que c'est le nombre de points de contrôle qui "
            "importe."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz7", figure=fig7, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "La connectivité n'est pas un facteur limitant lors des défis : la quasi-totalité des clients "
            "inscrits sont connectés lors des événements GLD. Les points négatifs (réduction < 0%) "
            "correspondent aux événements survenus lors des grands froids, où le programme perd son "
            "efficacité indépendamment du nombre de participants."
        ),
    ]),
])

viz8_section = html.Section(id="viz8", className="content-section", children=[
    html.H2("Les profils de consommation varient-ils selon les postes A, B et C ?"),
    html.Div(className="section-body", children=[
        html.P(
            "Le Poste C présente une consommation nettement supérieure aux deux autres, environ "
            "2,3 fois celle des postes A et B, ce qui suggère qu'il regroupe un nombre plus élevé de "
            "clients ou une clientèle à plus forte consommation individuelle. Les postes A et B affichent "
            "des niveaux comparables, B étant systématiquement légèrement inférieur à A."
        ),
    ]),
    html.Div(className="graph-container", children=[
        dcc.Graph(id="graph-viz8", figure=fig8, config={"displayModeBar": True}),
    ]),
    html.Div(className="section-body", children=[
        html.P(
            "Malgré ces écarts de niveaux absolus, les trois postes suivent la même saisonnalité : "
            "la consommation est maximale en hiver, chute significativement au printemps et en automne, "
            "et atteint son minimum en été. Cette convergence de comportement saisonnier confirme que "
            "le chauffage électrique est le principal déterminant de la demande pour l'ensemble des "
            "participants Hilo, indépendamment du poste d'appartenance."
        ),
    ]),
])

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
