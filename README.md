# Gestion de la demande électrique lors des pics hivernaux

**Tableau de bord interactif — Programme Hilo / Gestion locale de la demande (GLD) d'Hydro-Québec**

Projet INF8808 — Visualisation de données · Polytechnique Montréal · Hiver 2026 · Équipe 25

---

## 📖 Contexte

Chaque hiver, les périodes de grand froid entraînent une forte hausse de la consommation d'électricité au Québec. Hydro-Québec a mis en place le programme **Hilo** (gestion locale de la demande, GLD) : des clients volontaires équipés de thermostats intelligents acceptent que leur chauffage soit légèrement ajusté pendant les heures de pointe critiques (matin 6h–10h, soir 17h–21h). Répartis sur des milliers de foyers, ces micro-ajustements aident à stabiliser le réseau et à éviter les surcharges.

Ce tableau de bord analyse les données horaires de consommation (2022–2024, région de Montréal, trois postes électriques A/B/C) pour répondre à la question :

> **Quel est l'impact des conditions météorologiques sur la consommation électrique des participants Hilo, et comment leur comportement évolue-t-il avant, pendant et après les événements de pointe hivernaux ?**

**Public cible :** gestionnaires et analystes d'Hydro-Québec impliqués dans le programme GLD.

---

## 🏗️ Architecture

```
project/
├── app.py                       # Dash app · scrollytelling + 7 callbacks
├── server.py                    # Entry point (gunicorn / flask_failsafe)
├── data_utils.py                # ★ Couche de données partagée
├── requirements.txt
├── assets/
│   ├── logo.svg                 # Logo SVG custom (circle + bolt)
│   ├── scrollspy.js             # Scroll-spy sidebar (IntersectionObserver)
│   ├── css/main.css             # Styles complets (palette HQ)
│   └── data/
│       └── consommation-clients-evenements-pointe.csv
└── graphiques/
    ├── __init__.py
    ├── viz1a.py    # Lollipop corrélations météo
    ├── viz1b.py    # Scatter 2×2 par saison
    ├── viz2.py     # Heatmap calendrier (jour × mois)
    ├── viz3.py     # Roses polaires par saison
    ├── viz4.py     # Profil pré/pendant/post défi
    ├── viz5.py     # Scatter efficacité × température × heure
    ├── viz6.py     # Consigne vs température intérieure
    ├── viz7.py     # Participation vs réduction
    └── viz8.py     # Profils par poste A/B/C
```

### Couche de données (`data_utils.py`)

Une seule source de vérité, chargée en mémoire au démarrage via `lru_cache`, exposant :

| Fonction | Rôle |
|---|---|
| `load_data()` | Charge le CSV, ajoute saison/is_winter/dow |
| `winter_baseline()` | Baseline de référence : moyenne hiver hors événement, par (poste, heure) |
| `event_table()` | Un défi par ligne (matin/soir séparés), avec KPIs par événement |
| `event_profile(event_id)` | Profil temporel −4h à +6h autour du défi |
| `global_kpis()` | KPIs globaux injectés dans le hero (46 → 59 événements, etc.) |
| `daily_weather()` | Agrégats journaliers pour viz1a/1b |
| `base_layout()` | Helper de layout partagé (palette, fond, typo) |

Les visualisations importent **uniquement** cette couche, jamais le CSV directement.

---

## 🎬 Narratif (10 chapitres scrollytelling)

| # | Chapitre | Visualisation | Questions ciblées |
|---|---|---|---|
| 01 | **Contexte** | — | Mise en situation, question centrale |
| 02 | **Météo vs consommation** | viz1a (lollipop) + viz1b (4 scatters) | Q1, Q2, Q3 |
| 03 | **Vue calendrier** | viz2 (heatmap) | Q4, Q6 |
| 04 | **Profils horaires** | viz3 (4 roses polaires) | Q5 |
| 05 | **L'impact du programme** | viz4 (courbes pré/pendant/post) | Q8, Q9 |
| 06 | **Quand ça marche ?** | viz5 (scatter T°×heure) | Q10 |
| 07 | **Le mécanisme** | viz6 (consigne vs intérieure) | Q11, Q12 |
| 08 | **Rôle de l'échelle** | viz7 (participation) | Q13 |
| 09 | **Hétérogénéité des postes** | viz8 (barres groupées) | Q7 |
| 10 | **Synthèse** | 4 cartes de conclusion | — |

---

## 🔄 Interactivité

- **Filtrage saisonnier** (viz1a/1b) — radio pills Toutes/Hiver/Printemps/Été/Automne
- **Toggle de mode** (viz2) — MWh absolus ↔ écart % vs moyenne annuelle
- **Filtre par poste** (viz3) — Tous/A/B/C
- **Sélection d'événement** (viz4 + viz6 liés) — dropdown avec 59 défis triés par performance (✅/🟡/❌ + 🌅/🌙)
- **Cross-linking viz5 → viz4/viz6** — un clic sur un point du scatter charge le défi correspondant dans les deux autres vues
- **Toggle absolu/normalisé** (viz8) — consommation brute vs par client connecté
- **Scroll-spy sidebar** — la section courante s'illumine pendant le défilement

---

## 🚀 Démarrage

```bash
# Installation
pip install -r requirements.txt

# Lancement (dev, port 8050)
python app.py

# Ou via server.py (production / failsafe)
python server.py
```

Le fichier CSV `consommation-clients-evenements-pointe.csv` doit être placé à `assets/data/`.

Ouvrir http://localhost:8050 dans un navigateur moderne (testé sur Chrome).

---

## 📦 Dépendances

Voir `requirements.txt`. Versions minimales :

```
dash>=2.17
plotly>=5.20
pandas>=2.2
numpy>=1.26
flask-failsafe>=0.2
```

---

## 📊 Source des données

- **Fournisseur** : Hydro-Québec (portail de données ouvertes)
- **Licence** : CC BY-NC 4.0 (usage non commercial avec attribution)
- **Période** : 2022-01-01 à 2024-06-30
- **Fréquence** : horaire
- **Taille** : 64 605 observations (3 postes × horodatages)
- **Variables clés** : consommation énergétique, météo (Weatherbit API), thermostats intelligents Hilo, indicateurs d'événements GLD

---

## 👥 Équipe 25

- Ayat Wissem
- Boutera Hamza
- Diarra Halima Sadia
- Letieu Tchemeni Axelle Stévia
- Nguemegne Temena Loïc

---

## 📝 Licence

Projet académique — INF8808 Hiver 2026. Données sous licence CC BY-NC 4.0 (Hydro-Québec).
