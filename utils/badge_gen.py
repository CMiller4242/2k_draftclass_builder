"""
Archetype-driven badge generation and rookie badge cap enforcement.

2K26 has 56 badges across 7 categories. Priority badges get elevated levels;
non-priority badges default to None/Bronze. Rookie caps prevent unrealistic
badge counts for a first-year player.
"""

import random
from typing import Set

from data.fields import ALL_BADGES

# ---------------------------------------------------------------------------
# BADGE LEVEL WEIGHTS: priority vs. non-priority, per tier
# ---------------------------------------------------------------------------

_PRIORITY_WEIGHTS: dict = {
    1: {"None": 0,  "Bronze": 8,  "Silver": 22, "Gold": 35, "Hall of Fame": 28, "Legend": 7},
    2: {"None": 5,  "Bronze": 15, "Silver": 30, "Gold": 32, "Hall of Fame": 16, "Legend": 0},
    3: {"None": 15, "Bronze": 35, "Silver": 32, "Gold": 15, "Hall of Fame": 3,  "Legend": 0},
    4: {"None": 30, "Bronze": 42, "Silver": 22, "Gold": 6,  "Hall of Fame": 0,  "Legend": 0},
}

_NON_PRIORITY_WEIGHTS: dict = {
    1: {"None": 35, "Bronze": 38, "Silver": 18, "Gold": 7,  "Hall of Fame": 2, "Legend": 0},
    2: {"None": 50, "Bronze": 34, "Silver": 12, "Gold": 4,  "Hall of Fame": 0, "Legend": 0},
    3: {"None": 65, "Bronze": 26, "Silver": 8,  "Gold": 1,  "Hall of Fame": 0, "Legend": 0},
    4: {"None": 75, "Bronze": 20, "Silver": 5,  "Gold": 0,  "Hall of Fame": 0, "Legend": 0},
}

# Levels available per tier (Legend only for Tier 1)
_AVAILABLE_LEVELS: dict = {
    1: ["None", "Bronze", "Silver", "Gold", "Hall of Fame", "Legend"],
    2: ["None", "Bronze", "Silver", "Gold", "Hall of Fame"],
    3: ["None", "Bronze", "Silver", "Gold", "Hall of Fame"],
    4: ["None", "Bronze", "Silver", "Gold"],
}

# ---------------------------------------------------------------------------
# ROOKIE BADGE CAPS (max count per level per tier)
# ---------------------------------------------------------------------------

_ROOKIE_CAPS: dict = {
    1: {"Legend": 2, "Hall of Fame": 4, "Gold": 8},
    2: {"Legend": 0, "Hall of Fame": 2, "Gold": 5},
    3: {"Legend": 0, "Hall of Fame": 0, "Gold": 2},
    4: {"Legend": 0, "Hall of Fame": 0, "Gold": 0},
}

_DEMOTE: dict = {
    "Legend":       "Hall of Fame",
    "Hall of Fame": "Gold",
    "Gold":         "Silver",
    "Silver":       "Bronze",
}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def generate_badges_for_archetype(
    archetype: dict,
    tier: int,
    outcome_tag: str = "normal",
    class_type: str = "Average",
) -> dict:
    """
    Generate a badge dict for one player.

    Priority badges (from archetype's badge_priorities) receive elevated
    level distributions. Outcome tag modifiers add slight variance.
    """
    priority_badges = _get_priority_badges(archetype)
    available = _AVAILABLE_LEVELS.get(tier, _AVAILABLE_LEVELS[4])

    # Outcome tag tweaks to priority weights
    priority_w = {k: v for k, v in _PRIORITY_WEIGHTS.get(tier, _PRIORITY_WEIGHTS[4]).items()}
    if outcome_tag == "guaranteed_good":
        _shift_weights_up(priority_w)
    elif outcome_tag in ("true_bust", "bust_risk"):
        _shift_weights_down(priority_w)
    elif outcome_tag == "limited_role_player" and tier >= 3:
        _shift_weights_down(priority_w)

    badges: dict = {}
    for category, badge_list in ALL_BADGES.items():
        for badge in badge_list:
            is_priority = badge in priority_badges
            w_table = priority_w if is_priority else _NON_PRIORITY_WEIGHTS.get(tier, _NON_PRIORITY_WEIGHTS[4])
            levels = [l for l in available if w_table.get(l, 0) > 0]
            weights = [w_table[l] for l in levels]
            badges[badge] = random.choices(levels, weights=weights, k=1)[0]

    return badges


def enforce_rookie_badge_caps(player: dict, class_type: str = "Average") -> None:
    """
    Demote excess badges in-place so total counts stay within rookie caps.

    Processes Legend → Hall of Fame → Gold in order so cascading demotions
    from one level don't push the next level over its cap.
    """
    badges = player["badges"]
    tier   = player["tier"]
    caps   = _ROOKIE_CAPS.get(tier, {})

    for level in ("Legend", "Hall of Fame", "Gold"):
        max_count = caps.get(level, 0)
        at_level = [b for b, lv in badges.items() if lv == level]
        if len(at_level) > max_count:
            # Demote the extras (random selection — no preference for priority)
            excess = random.sample(at_level, len(at_level) - max_count)
            next_lv = _DEMOTE[level]
            for b in excess:
                badges[b] = next_lv


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _get_priority_badges(archetype: dict) -> Set[str]:
    priority_map = archetype.get("badge_priorities", {})
    result: Set[str] = set()
    for badge_list in priority_map.values():
        result.update(badge_list)
    return result


def _shift_weights_up(w: dict) -> None:
    """Move probability mass toward higher levels (guaranteed_good boost)."""
    for level in ("Hall of Fame", "Gold"):
        w[level] = int(w.get(level, 0) * 1.3)
    for level in ("None", "Bronze"):
        w[level] = max(0, int(w.get(level, 0) * 0.8))


def _shift_weights_down(w: dict) -> None:
    """Move probability mass toward lower levels (bust/bust_risk reduction)."""
    for level in ("Hall of Fame", "Gold", "Silver"):
        w[level] = max(0, int(w.get(level, 0) * 0.6))
    w["None"]   = int(w.get("None",   0) * 1.4)
    w["Bronze"] = int(w.get("Bronze", 0) * 1.2)
