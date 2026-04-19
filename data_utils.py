# -*- coding: utf-8 -*-
"""
data_utils.py — Single source of truth for data loading & derived metrics.
Loaded ONCE at app startup, shared across all visualisations.
"""

from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd

# ───────────────────────────────────────────────────────────────
# Canonical palette (Hydro-Québec inspired)
# ───────────────────────────────────────────────────────────────
PALETTE = {
    "primary":   "#00557F",   # HQ deep blue
    "accent":    "#009FE3",   # HQ light blue
    "warm":      "#F28C28",   # pointe / warning orange
    "hot":       "#DC2626",   # défi rouge
    "cool":      "#16A34A",   # succès vert
    "muted":     "#6B7280",   # référence gris
    "bg_soft":   "#FAFBFC",
    "grid":      "rgba(200,200,200,0.4)",
    "poste_A":   "#00557F",
    "poste_B":   "#78BE20",
    "poste_C":   "#009FE3",
    "season_winter":  "#1E40AF",
    "season_spring":  "#16A34A",
    "season_summer":  "#F59E0B",
    "season_autumn":  "#B45309",
}

SEASONS_ORD = ["Hiver", "Printemps", "Été", "Automne"]
MONTHS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
             "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
DAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

WINTER_MONTHS = {12, 1, 2, 3}
DATA_PATH = Path("assets/data/consommation-clients-evenements-pointe.csv")


# ───────────────────────────────────────────────────────────────
# Season helper
# ───────────────────────────────────────────────────────────────
def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "Hiver"
    if month in (3, 4, 5):
        return "Printemps"
    if month in (6, 7, 8):
        return "Été"
    return "Automne"


# ───────────────────────────────────────────────────────────────
# Core loader — called ONCE
# ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["dow"] = df["date"].dt.dayofweek
    df["saison"] = df["month"].map(_season)
    df["is_winter"] = df["month"].isin(WINTER_MONTHS)
    # normalise boolean columns coming as strings
    for c in ("indicateur_weekend", "indicateur_jour_ferie", "indicateur_weekend_ferie"):
        if c in df.columns and df[c].dtype == object:
            df[c] = df[c].astype(str).str.upper().eq("TRUE")
    return df


# ───────────────────────────────────────────────────────────────
# Baseline (winter, non-event, non pre/post) per (poste, hour)
# ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def winter_baseline() -> pd.Series:
    df = load_data()
    ref = df[(df["indicateur_evenement"] == 0)
             & (df["pre_post_indicateur_evenement"] == 0)
             & df["is_winter"]]
    return ref.groupby(["poste", "heure_locale"])["energie_totale_consommee"].mean()


# ───────────────────────────────────────────────────────────────
# Per-event aggregates (one row per GLD event)
# ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def event_table() -> pd.DataFrame:
    """
    One row per *distinct* GLD defi event.
    A calendar day can contain two defis (morning AND evening) — we split them
    using consecutive-hour runs so each defi becomes its own row.

    Returns columns: date, event_id, heure_debut, heure_fin, temperature_ext,
    reduction_pct, conso_gld_kwh, conso_ref_kwh, clients_moy, tstats_moy,
    periode_jour, saison.
    """
    df = load_data()
    ref_base = winter_baseline()
    event_rows = df[df["indicateur_evenement"] == 1]
    out = []

    for date, g in event_rows.groupby("date"):
        hours = sorted(g["heure_locale"].unique())
        # Group consecutive hours into runs: [6,7,8] [16,17,18,19] → 2 defis
        runs, current = [], [hours[0]]
        for h in hours[1:]:
            if h - current[-1] == 1:
                current.append(h)
            else:
                runs.append(current); current = [h]
        runs.append(current)

        # Keep only runs that look like real defis (≥2 consecutive hours)
        real_runs = [r for r in runs if len(r) >= 2]
        if not real_runs:
            continue

        for idx, hrs in enumerate(real_runs):
            sub = g[g["heure_locale"].isin(hrs)]
            conso_gld = sub["energie_totale_consommee"].sum()
            conso_ref = sum(ref_base.get((p, h), 0)
                            for p in ("A", "B", "C") for h in hrs)
            if conso_ref <= 0:
                continue
            reduction = (conso_ref - conso_gld) / conso_ref * 100
            clients = sub.groupby("heure_locale")["clients_connectes"].sum().mean()
            tstats = sub.groupby("heure_locale")["tstats_intelligents_connectes"].sum().mean()

            periode = "matin" if min(hrs) < 13 else "soir"
            # ID distinguishes morning vs evening of same date
            suffix = "" if len(real_runs) == 1 else f"-{periode}"
            out.append({
                "date": date,
                "date_str": f"{str(date)[:10]}{suffix}",
                "event_id": f"{str(date)[:10]}{suffix}",
                "heure_debut": min(hrs),
                "heure_fin": max(hrs),
                "duree_h": len(hrs),
                "temperature_ext": round(sub["temperature_exterieure_moyenne"].mean(), 1),
                "conso_gld_kwh": round(conso_gld, 1),
                "conso_ref_kwh": round(conso_ref, 1),
                "reduction_pct": round(reduction, 1),
                "clients_moy": int(round(clients)),
                "tstats_moy": int(round(tstats)),
                "periode_jour": periode,
                "saison": _season(date.month),
            })

    ev = pd.DataFrame(out).sort_values(["date", "heure_debut"]).reset_index(drop=True)
    return ev


# ───────────────────────────────────────────────────────────────
# Global KPIs (used in hero header)
# ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def global_kpis() -> dict:
    df = load_data()
    ev = event_table()
    return {
        "n_events": len(ev),
        "mean_reduction_pct": round(ev["reduction_pct"].mean(), 1),
        "best_reduction_pct": round(ev["reduction_pct"].max(), 1),
        "n_clients_max": int(df["clients_connectes"].max()),
        "n_tstats_max": int(df["tstats_intelligents_connectes"].max()),
        "n_obs": len(df),
        "date_min": str(df["date"].min())[:10],
        "date_max": str(df["date"].max())[:10],
        "pct_events_positive": round((ev["reduction_pct"] > 0).mean() * 100, 1),
        "worst_reduction_pct": round(ev["reduction_pct"].min(), 1),
    }


# ───────────────────────────────────────────────────────────────
# Pre/during/post event profile for ONE event (or aggregated)
# Used by viz4 (consumption) and viz6 (thermostats)
# ───────────────────────────────────────────────────────────────
def event_profile(event_id=None, offsets=range(-4, 7)):
    """
    If event_id is None → average across ALL defi events (each split into matin/soir).
    event_id format: "YYYY-MM-DD" or "YYYY-MM-DD-matin" / "YYYY-MM-DD-soir".
    Returns DataFrame with columns: offset, conso_hilo, conso_ref,
    temp_consigne, temp_interieure.
    """
    df = load_data()
    ref_base = winter_baseline()
    df_ref = df[(df["indicateur_evenement"] == 0)
                & (df["pre_post_indicateur_evenement"] == 0)
                & df["is_winter"]]

    ev_table = event_table()
    if event_id is None:
        # Iterate all defis (matin + soir counted separately via event_id)
        event_selector = [(row["date"], row["heure_debut"], row["heure_fin"])
                          for _, row in ev_table.iterrows()]
    else:
        row = ev_table[ev_table["event_id"] == event_id]
        if row.empty:
            # Fallback: try matching by date only (user may pass bare date)
            row = ev_table[ev_table["date_str"].str.startswith(event_id)]
        if row.empty:
            return pd.DataFrame({"offset": list(offsets), "conso_hilo": [np.nan]*len(list(offsets)),
                                  "conso_ref": [np.nan]*len(list(offsets)),
                                  "temp_consigne": [np.nan]*len(list(offsets)),
                                  "temp_interieure": [np.nan]*len(list(offsets))})
        r = row.iloc[0]
        event_selector = [(r["date"], r["heure_debut"], r["heure_fin"])]

    hilo_rows, ref_rows, therm_rows = [], [], []
    for ed, start_h, _end_h in event_selector:
        # Focus on the defi anchored at start_h (so we get correct offsets per defi)
        for off in offsets:
            target_h = (start_h + off) % 24
            target_date = ed if off >= 0 else pd.Timestamp(ed) - pd.Timedelta(days=1)
            # Also for positive offsets past midnight, advance the date
            if off >= 0 and (start_h + off) >= 24:
                target_date = pd.Timestamp(ed) + pd.Timedelta(days=1)

            subset = df[(df["date"] == target_date) & (df["heure_locale"] == target_h)]
            if not subset.empty:
                hilo_rows.append({
                    "offset": off,
                    "conso": subset["energie_totale_consommee"].sum(),
                })
                therm_rows.append({
                    "offset": off,
                    "consigne": subset["temperature_consigne_moyenne"].mean(),
                    "interieure": subset["temperature_interieure_moyenne"].mean(),
                })
            ref_h = df_ref[df_ref["heure_locale"] == target_h]
            by_d = ref_h.groupby("date")["energie_totale_consommee"].sum()
            if len(by_d) > 0:
                ref_rows.append({"offset": off, "conso": by_d.mean()})

    hilo = pd.DataFrame(hilo_rows).groupby("offset")["conso"].mean() if hilo_rows else pd.Series(dtype=float)
    refc = pd.DataFrame(ref_rows).groupby("offset")["conso"].mean() if ref_rows else pd.Series(dtype=float)
    thrm = pd.DataFrame(therm_rows).groupby("offset").mean() if therm_rows else pd.DataFrame()

    out = pd.DataFrame({"offset": list(offsets)})
    out["conso_hilo"] = out["offset"].map(hilo)
    out["conso_ref"] = out["offset"].map(refc)
    out["temp_consigne"] = out["offset"].map(thrm["consigne"] if "consigne" in thrm else pd.Series(dtype=float))
    out["temp_interieure"] = out["offset"].map(thrm["interieure"] if "interieure" in thrm else pd.Series(dtype=float))
    return out


# ───────────────────────────────────────────────────────────────
# Daily weather × consumption (for viz1)
# ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def daily_weather() -> pd.DataFrame:
    df = load_data()
    daily = df.groupby("date").agg(
        conso=("energie_totale_consommee", "sum"),
        temp=("temperature_exterieure_moyenne", "mean"),
        vent=("vitesse_vent_moyenne", "mean"),
        neige=("precipitations_neige_moyenne", "mean"),
        humidite=("humidite_relative_moyenne", "mean"),
        irradiance=("irradiance_solaire_moyenne", "mean"),
    ).reset_index()
    daily["conso_mwh"] = daily["conso"] / 1000
    daily["month"] = daily["date"].dt.month
    daily["saison"] = daily["month"].map(_season)
    daily["dow"] = daily["date"].dt.dayofweek
    return daily


# ───────────────────────────────────────────────────────────────
# Shared layout helper
# ───────────────────────────────────────────────────────────────
def base_layout(title: str, subtitle: str = "", height: int = 500) -> dict:
    """
    Returns a layout kwargs dict WITHOUT touching annotations.
    The subtitle is encoded in the title as a <sub> line so we never clobber
    per-viz annotations (vrects, arrows, peak labels, etc).
    """
    title_html = f"{title}<br><sub style='font-size:11px;color:#888'>{subtitle}</sub>" if subtitle else title
    return dict(
        title=dict(text=title_html, font=dict(size=16, color=PALETTE["primary"]),
                   x=0.5, xanchor="center"),
        paper_bgcolor="white",
        plot_bgcolor=PALETTE["bg_soft"],
        font=dict(family="Inter, Arial, sans-serif", size=13, color="#333"),
        margin=dict(t=100, b=70, l=80, r=30),
        height=height,
        hoverlabel=dict(bgcolor="white", bordercolor=PALETTE["primary"],
                        font=dict(family="Inter, Arial", size=12)),
    )
