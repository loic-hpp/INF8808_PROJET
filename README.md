# Gestion de la demande électrique lors des pics hivernaux

**Tableau de bord interactif — Programme Hilo / Gestion locale de la demande (GLD) d'Hydro-Québec**

Projet INF8808 — Visualisation de données · Polytechnique Montréal · Hiver 2026 · Équipe 25

---

## Contexte

Chaque hiver, les périodes de grand froid entraînent une forte hausse de la consommation d'électricité au Québec. Hydro-Québec a mis en place le programme **Hilo** (gestion locale de la demande, GLD) : des clients volontaires équipés de thermostats intelligents acceptent que leur chauffage soit légèrement ajusté pendant les heures de pointe critiques (matin 6h–10h, soir 17h–21h). Répartis sur des milliers de foyers, ces micro-ajustements aident à stabiliser le réseau et à éviter les surcharges.

Ce tableau de bord analyse les données horaires de consommation (2022–2024, région de Montréal, trois postes électriques A/B/C) pour répondre à la question suivante :

> **Quel est l'impact des conditions météorologiques sur la consommation électrique des participants Hilo, et comment leur comportement évolue-t-il avant, pendant et après les événements de pointe hivernaux ?**

**Public cible :** gestionnaires et analystes d'Hydro-Québec impliqués dans le programme GLD.

---

## Architecture

```
project/
├── app.py                       # Application Dash (storytelling fluide, 7 callbacks)
├── server.py                    # Point d'entrée (gunicorn / flask_failsafe)
├── data_utils.py                # Couche de données partagée (source unique de vérité)
├── requirements.txt
├── assets/
│   ├── css/
│   │   └── main.css             # Feuille de style complète (palette 100% bleue)
│   └── data/
│       └── consommation-clients-evenements-pointe.csv
└── graphiques/
    ├── __init__.py
    ├── viz1a.py    # Lollipop — corrélations météo
    ├── viz1b.py    # Scatter 2×2 par saison
    ├── viz2.py     # Heatmap calendrier (jour × mois)
    ├── viz3.py     # Roses polaires par saison
    ├── viz4.py     # Profil pré / pendant / post défi
    ├── viz5.py     # Scatter efficacité × température × heure
    ├── viz6.py     # Consigne vs température intérieure
    ├── viz7.py     # Participation vs réduction
    └── viz8.py     # Profils par poste A/B/C
```

L'application repose entièrement sur Python et Dash. **Aucun JavaScript personnalisé** n'est requis : toute l'interactivité est gérée par des callbacks Dash et la navigation latérale fonctionne avec des ancres CSS pures.

### Couche de données (`data_utils.py`)

Une seule source de vérité, chargée en mémoire au démarrage via `lru_cache` :

| Fonction | Rôle |
|---|---|
| `load_data()` | Charge le CSV et l'enrichit (saison, indicateur d'hiver, jour de la semaine) |
| `winter_baseline()` | Baseline de référence : moyenne hiver hors événement, par (poste, heure) |
| `event_table()` | Un défi GLD par ligne (matin/soir séparés via détection de runs consécutifs) |
| `event_profile(event_id)` | Profil temporel −4h à +6h autour du défi |
| `global_kpis()` | KPIs globaux injectés dans l'en-tête |
| `daily_weather()` | Agrégats journaliers pour les visualisations météo |
| `base_layout()` | Helper de layout partagé (palette, fond, typographie) |

Les visualisations importent **uniquement** cette couche, jamais le CSV directement.

---

## Narratif

L'application présente une narration **fluide et continue** : pas de chapitres numérotés, mais des transitions douces qui relient les sections les unes aux autres. Le défilement guide naturellement le lecteur d'une question à la suivante.

| Section | Visualisation | Questions ciblées |
|---|---|---|
| Contexte | — | Mise en situation, question centrale |
| Météo vs consommation | viz1a (lollipop) + viz1b (scatter 2×2) | Q1, Q2, Q3 |
| Vue calendrier | viz2 (heatmap) | Q4, Q6 |
| Profils horaires | viz3 (4 roses polaires) | Q5 |
| L'impact du programme | viz4 (courbes pré/pendant/post) | Q8, Q9 |
| Quand le programme fonctionne | viz5 (scatter T°×heure) | Q10 |
| Le mécanisme | viz6 (consigne vs intérieure) | Q11, Q12 |
| Rôle de l'échelle | viz7 (participation) | Q13 |
| Hétérogénéité des postes | viz8 (barres groupées) | Q7 |
| Synthèse | 4 cartes de conclusion | — |

---

## Interactivité

Toute l'interactivité est implémentée en Python pur via des callbacks Dash :

- **Filtrage saisonnier** (viz1a / viz1b) — boutons radio Toutes / Hiver / Printemps / Été / Automne
- **Toggle d'affichage** (viz2) — MWh absolus ou pourcentage d'écart à la moyenne annuelle
- **Filtre par poste** (viz3) — Tous / A / B / C
- **Sélection d'événement** (viz4 et viz6 liés) — menu déroulant avec 59 défis, triés par performance, avec étiquettes scannables (statut, période, date, heure, température, réduction)
- **Cross-linking viz5 → viz4 et viz6** — un clic sur un point du scatter d'efficacité charge automatiquement le défi correspondant dans le profil de consommation et le graphique des thermostats
- **Toggle absolu / normalisé** (viz8) — consommation brute ou par client connecté
- **Navigation latérale** — barre fixe à gauche avec liens d'ancrage (défilement fluide CSS pur)

---

## Démarrage

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement (mode développement, port 8050)
python app.py

# Ou via server.py (mode production / failsafe)
python server.py
```

Le fichier CSV `consommation-clients-evenements-pointe.csv` doit être placé à `assets/data/`.

Ouvrir `http://localhost:8050` dans un navigateur moderne (testé sur Chrome).

---

## Dépendances

Voir `requirements.txt`. Versions minimales :

```
dash>=2.17
plotly>=5.20
pandas>=2.2
numpy>=1.26
flask-failsafe>=0.2
```

---

## Source des données

- **Fournisseur** : Hydro-Québec (portail de données ouvertes)
- **Licence** : CC BY-NC 4.0 (usage non commercial avec attribution)
- **Période** : 2022-01-01 à 2024-06-30
- **Fréquence** : horaire
- **Taille** : 64 605 observations (3 postes × horodatages)
- **Variables clés** : consommation énergétique, météo (Weatherbit API), thermostats intelligents Hilo, indicateurs d'événements GLD

---

## Équipe 25

- Ayat Wissem
- Boutera Hamza
- Diarra Halima Sadia
- Letieu Tchemeni Axelle Stévia
- Nguemegne Temena Loïc

---

## Licence

Projet académique — INF8808 Hiver 2026. Données sous licence CC BY-NC 4.0 (Hydro-Québec).