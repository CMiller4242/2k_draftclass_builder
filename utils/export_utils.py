"""
Export utilities for JSON and CSV output.
Converts player/class data to downloadable formats.
"""

import json
import csv
import io
from typing import List


def players_to_json(players: List[dict]) -> str:
    """Serialize a list of player dicts to a JSON string."""
    return json.dumps(players, indent=2)


def players_to_csv(players: List[dict]) -> str:
    """
    Flatten player dicts into CSV rows.
    Attributes and tendencies become individual columns.
    Badges are collapsed to a summary column for readability.
    """
    if not players:
        return ""

    output = io.StringIO()

    # Build column headers from first player
    sample = players[0]
    base_cols = [
        "pick_number", "name", "position", "secondary_position",
        "height_display", "weight_lbs", "archetype", "tier", "tier_label",
        "projected_role", "development_outlook", "bust_risk", "is_bust",
    ]
    attr_cols = [f"attr_{k}" for k in sample.get("attributes", {}).keys()]
    tendency_cols = [f"tend_{k}" for k in sample.get("tendencies", {}).keys()]
    badge_cols = [f"badge_{k}" for k in sample.get("badges", {}).keys()]

    fieldnames = base_cols + attr_cols + tendency_cols + badge_cols

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for player in players:
        row = {col: player.get(col, "") for col in base_cols}

        for attr, val in player.get("attributes", {}).items():
            row[f"attr_{attr}"] = val

        for tend, val in player.get("tendencies", {}).items():
            row[f"tend_{tend}"] = val

        for badge, level in player.get("badges", {}).items():
            row[f"badge_{badge}"] = level

        writer.writerow(row)

    return output.getvalue()


def single_player_to_csv(player: dict) -> str:
    """Export a single player to CSV (same format as bulk)."""
    return players_to_csv([player])


def class_summary_to_json(summary: dict) -> str:
    """Export class summary dict to JSON."""
    return json.dumps(summary, indent=2)
