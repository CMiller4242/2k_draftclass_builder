"""
Export utilities for JSON and CSV output.

CSV column order:
  1. Identity / summary  — pick, name, position, height, archetype, build_name,
                           tier, potential (top-level), role, bust, outlook, scouting
  2. Attributes          — grouped in 2K order (Misc ex-Potential, Offensive,
                           Defensive, Athleticism, Durability, Mental)
                           Potential is NOT repeated here.
  3. Tendencies          — grouped in 2K order
  4. Badges              — grouped by category
"""

import json
import csv
import io
from typing import List

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
    "archetype",
    "build_name",
    "tier",
    "potential",          # pulled from attributes["Potential"] — not repeated later
    "tier_label",
    "projected_role",
    "bust_risk",
    "development_outlook",
    "is_bust",
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
