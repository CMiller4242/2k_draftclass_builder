"""
Export utilities for JSON, CSV, and XLSX output.

CSV column order:
  1. Identity / summary  — pick, name, position, height, archetype, build_name,
                           tier, potential (top-level), role, bust, outlook, scouting
  2. Attributes          — grouped in 2K order (Misc ex-Potential, Offensive,
                           Defensive, Athleticism, Durability, Mental)
                           Potential is NOT repeated here.
  3. Tendencies          — grouped in 2K order
  4. Badges              — grouped by category

XLSX workbook sheets:
  1. Player Profiles — identity + scouting fields
  2. Attributes      — pick identity + all attributes (Potential first)
  3. Tendencies      — pick identity + all tendencies
  4. Badges          — pick identity + all badges by category
  5. Class Summary   — aggregate stats
"""

import json
import csv
import io
from io import BytesIO
from typing import List, Optional

import pandas as pd

from data.fields import ATTRIBUTE_CATEGORIES, TENDENCY_CATEGORIES, ALL_BADGES
from utils.scouting import generate_scouting_summary

# Attribute fields emitted under attr_* — Potential is excluded because it
# appears as a standalone top-level column near the front.
_ATTR_EXPORT_ORDER = [
    attr
    for category in ATTRIBUTE_CATEGORIES.values()
    for attr in category
    if attr != "Potential"
]

# Tendency fields in category order
_TEND_EXPORT_ORDER = [
    tend
    for category in TENDENCY_CATEGORIES.values()
    for tend in category
]

# Badge fields in category order
_BADGE_EXPORT_ORDER = [
    badge
    for category in ALL_BADGES.values()
    for badge in category
]

# Front-matter columns (order matters — Potential at position 10)
_BASE_COLS = [
    "pick_number",
    "name",
    "position",
    "secondary_position",
    "height_display",
    "weight_lbs",
    "wingspan_display",
    "archetype",
    "build_name",
    "tier",
    "potential",          # pulled from attributes["Potential"] — not repeated later
    "tier_label",
    "projected_role",
    "bust_risk",
    "development_outlook",
    "is_bust",
    "boom_pct",
    "average_pct",
    "bust_pct",
    "peak_age_start",
    "peak_age_end",
    "scouting_summary",   # generated on export; not stored on player dict
]

# Full ordered fieldname list used for every CSV write
_ALL_FIELDNAMES = (
    _BASE_COLS
    + [f"attr_{a}" for a in _ATTR_EXPORT_ORDER]
    + [f"tend_{t}" for t in _TEND_EXPORT_ORDER]
    + [f"badge_{b}" for b in _BADGE_EXPORT_ORDER]
)


def players_to_json(players: List[dict]) -> str:
    """Serialize a list of player dicts to a JSON string."""
    return json.dumps(players, indent=2)


def players_to_csv(players: List[dict]) -> str:
    """
    Flatten player dicts into CSV rows with a fixed, readable column order.

    Column layout:
      - Identity / summary fields (pick, name, pos, archetype, build_name,
        tier, Potential, role, bust, outlook) — first ~15 cols
      - attr_* for every attribute except Potential (2K category order)
      - tend_* for every tendency (2K category order)
      - badge_* for every badge (category order)

    Potential is emitted once as the top-level 'potential' column (col 10)
    and is NOT repeated inside the attr_* block.
    """
    if not players:
        return ""

    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=_ALL_FIELDNAMES, extrasaction="ignore"
    )
    writer.writeheader()

    for player in players:
        attrs   = player.get("attributes", {})
        tends   = player.get("tendencies", {})
        badges  = player.get("badges", {})

        row: dict = {}

        # Base / identity columns
        for col in _BASE_COLS:
            if col == "potential":
                row["potential"] = attrs.get("Potential", "")
            elif col == "scouting_summary":
                row["scouting_summary"] = generate_scouting_summary(player)
            else:
                row[col] = player.get(col, "")

        # Attributes (Potential excluded — already in row["potential"])
        for attr in _ATTR_EXPORT_ORDER:
            row[f"attr_{attr}"] = attrs.get(attr, "")

        # Tendencies
        for tend in _TEND_EXPORT_ORDER:
            row[f"tend_{tend}"] = tends.get(tend, "")

        # Badges
        for badge in _BADGE_EXPORT_ORDER:
            row[f"badge_{badge}"] = badges.get(badge, "")

        writer.writerow(row)

    return output.getvalue()


def single_player_to_csv(player: dict) -> str:
    """Export a single player to CSV (same format as bulk)."""
    return players_to_csv([player])


def class_summary_to_json(summary: dict) -> str:
    """Export class summary dict to JSON."""
    # top_picks contains full player dicts — omit for a clean summary export
    clean = {k: v for k, v in summary.items() if k != "top_picks"}
    return json.dumps(clean, indent=2)


# ---------------------------------------------------------------------------
# XLSX EXPORT
# ---------------------------------------------------------------------------

def players_to_xlsx(
    players: List[dict],
    class_summary: Optional[dict] = None,
    class_config: Optional[dict] = None,
) -> bytes:
    """
    Export players to an Excel workbook with 5 sheets.

    Sheets:
      1. Player Profiles — identity + scouting fields
      2. Attributes      — identity stub + all attributes (Potential first)
      3. Tendencies      — identity stub + all tendencies in 2K order
      4. Badges          — identity stub + all badges grouped by category
      5. Class Summary   — aggregate stats

    Returns raw XLSX bytes suitable for st.download_button(data=...).
    """
    if not players:
        return b""

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        _write_profiles_sheet(writer, players)
        _write_attributes_sheet(writer, players)
        _write_tendencies_sheet(writer, players)
        _write_badges_sheet(writer, players)
        _write_summary_sheet(writer, players, class_summary, class_config)

    return buf.getvalue()


# -- identity stub shared across attribute/tendency/badge sheets -------------

def _id_stub(player: dict) -> dict:
    return {
        "Pick":      player["pick_number"],
        "Name":      player["name"],
        "Position":  player["position"],
        "Archetype": player["archetype"],
    }


# -- Sheet 1: Player Profiles ------------------------------------------------

def _write_profiles_sheet(writer: pd.ExcelWriter, players: List[dict]) -> None:
    rows = []
    for p in players:
        attrs = p.get("attributes", {})
        rows.append({
            "Pick":               p["pick_number"],
            "Name":               p["name"],
            "Position":           p["position"],
            "Secondary Position": p.get("secondary_position") or "",
            "Height":             p["height_display"],
            "Weight (lbs)":       p["weight_lbs"],
            "Wingspan":           p.get("wingspan_display") or "",
            "Archetype":          p["archetype"],
            "Build Name":         p.get("build_name") or "",
            "Tier":               p["tier"],
            "Tier Label":         p["tier_label"],
            "Potential":          attrs.get("Potential", ""),
            "Projected Role":     p.get("projected_role", ""),
            "Bust Risk":          p.get("bust_risk", ""),
            "Is Bust":            p.get("is_bust", False),
            "Outcome Tag":        p.get("outcome_tag", ""),
            "Sleeper Subtype":    p.get("sleeper_subtype") or "",
            "Development Outlook": p.get("development_outlook", ""),
            "Boom %":             p.get("boom_pct", ""),
            "Average %":          p.get("average_pct", ""),
            "Bust %":             p.get("bust_pct", ""),
            "Peak Age Start":     p.get("peak_age_start", ""),
            "Peak Age End":       p.get("peak_age_end", ""),
            "Scouting Summary":   generate_scouting_summary(p),
        })
    pd.DataFrame(rows).to_excel(writer, sheet_name="Player Profiles", index=False)


# -- Sheet 2: Attributes -----------------------------------------------------

_ATTR_ORDER = [
    attr
    for category in ATTRIBUTE_CATEGORIES.values()
    for attr in category
    if attr != "Potential"
]


def _write_attributes_sheet(writer: pd.ExcelWriter, players: List[dict]) -> None:
    rows = []
    for p in players:
        attrs = p.get("attributes", {})
        row = _id_stub(p)
        row["Potential"] = attrs.get("Potential", "")   # Potential first
        for attr in _ATTR_ORDER:
            row[attr] = attrs.get(attr, "")
        rows.append(row)
    pd.DataFrame(rows).to_excel(writer, sheet_name="Attributes", index=False)


# -- Sheet 3: Tendencies -----------------------------------------------------

_TEND_ORDER = [
    tend
    for category in TENDENCY_CATEGORIES.values()
    for tend in category
]


def _write_tendencies_sheet(writer: pd.ExcelWriter, players: List[dict]) -> None:
    rows = []
    for p in players:
        tends = p.get("tendencies", {})
        row = _id_stub(p)
        for tend in _TEND_ORDER:
            row[tend] = tends.get(tend, "")
        rows.append(row)
    pd.DataFrame(rows).to_excel(writer, sheet_name="Tendencies", index=False)


# -- Sheet 4: Badges ---------------------------------------------------------

def _write_badges_sheet(writer: pd.ExcelWriter, players: List[dict]) -> None:
    # Deduplicate badge names while preserving category order
    seen: set = set()
    badge_order: List[str] = []
    for badge_list in ALL_BADGES.values():
        for badge in badge_list:
            if badge not in seen:
                badge_order.append(badge)
                seen.add(badge)

    rows = []
    for p in players:
        badges = p.get("badges", {})
        row = _id_stub(p)
        for badge in badge_order:
            row[badge] = badges.get(badge, "None")
        rows.append(row)
    pd.DataFrame(rows).to_excel(writer, sheet_name="Badges", index=False)


# -- Sheet 5: Class Summary --------------------------------------------------

def _write_summary_sheet(
    writer: pd.ExcelWriter,
    players: List[dict],
    summary: Optional[dict],
    config: Optional[dict],
) -> None:
    s = summary or {}
    cfg = config or {}

    tier_breakdown = s.get("tier_breakdown", {t: sum(1 for p in players if p["tier"] == t) for t in range(1, 5)})
    sleeper_counts = s.get("sleeper_counts", {})
    outcome_tags   = s.get("outcome_tag_counts", {})
    warnings       = s.get("validation_warnings", [])

    rows = [
        ("Class Type",              cfg.get("class_type", "")),
        ("Class Flavor",            cfg.get("class_flavor", "")),
        ("Player Count",            len(players)),
        ("", ""),
        ("Tier 1 (Superstar)",      tier_breakdown.get(1, 0)),
        ("Tier 2 (All-Star)",       tier_breakdown.get(2, 0)),
        ("Tier 3 (Starter)",        tier_breakdown.get(3, 0)),
        ("Tier 4 (Role Player)",    tier_breakdown.get(4, 0)),
        ("", ""),
        ("Bust Count",              s.get("bust_count", sum(1 for p in players if p.get("is_bust")))),
        ("Bust %",                  s.get("bust_percentage", "")),
        ("Avg Potential",           s.get("avg_potential", "")),
        ("", ""),
        ("Unique Archetypes",       s.get("unique_archetypes", "")),
        ("Diversity Score",         s.get("diversity_score", "")),
        ("Most Repeated Archetype", s.get("most_repeated_archetype", "")),
        ("Most Repeated Count",     s.get("most_repeated_count", "")),
        ("", ""),
        ("Role Sleepers",           sleeper_counts.get("role_sleeper", 0)),
        ("Starter Sleepers",        sleeper_counts.get("starter_sleeper", 0)),
        ("Star Sleepers",           sleeper_counts.get("star_sleeper", 0)),
        ("Legendary Sleepers",      sleeper_counts.get("legendary_sleeper", 0)),
        ("", ""),
        ("Guaranteed Good",         outcome_tags.get("guaranteed_good", 0)),
        ("Bust Risk",               outcome_tags.get("bust_risk", 0)),
        ("True Busts",              outcome_tags.get("true_bust", 0)),
        ("Limited Role Players",    outcome_tags.get("limited_role_player", 0)),
    ]

    if warnings:
        rows.append(("", ""))
        rows.append(("Realism Warnings", ""))
        for w in warnings:
            rows.append(("", w))

    df = pd.DataFrame(rows, columns=["Metric", "Value"])
    df.to_excel(writer, sheet_name="Class Summary", index=False)
