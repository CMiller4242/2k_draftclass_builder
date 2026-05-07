"""
Archetype-driven badge generation and rookie badge cap enforcement.

Generated draft class rookies are hard-capped at Gold badges.
Hall of Fame and Legend are reserved for MyNBA/MyEras badge progression
and must never appear in a generated rookie profile.

Valid rookie badge levels: None | Bronze | Silver | Gold
"""

import random
from typing import Set

from data.fields import ALL_BADGES

# ---------------------------------------------------------------------------
# BADGE LEVEL WEIGHTS: priority vs. non-priority, per tier
# Gold is the maximum — Hall of Fame and Legend intentionally absent.
# ---------------------------------------------------------------------------

_PRIORITY_WEIGHTS: dict = {
    1: {"None": 0,  "Bronze": 5,  "Silver": 25, "Gold": 70},
    2: {"None": 5,  "Bronze": 15, "Silver": 35, "Gold": 45},
    3: {"None": 18, "Bronze": 37, "Silver": 32, "Gold": 13},
    4: {"None": 35, "Bronze": 42, "Silver": 18, "Gold": 5},
}

_NON_PRIORITY_WEIGHTS: dict = {
    1: {"None": 38, "Bronze": 38, "Silver": 20, "Gold": 4},
    2: {"None": 52, "Bronze": 35, "Silver": 12, "Gold": 1},
    3: {"None": 66, "Bronze": 28, "Silver": 6,  "Gold": 0},
    4: {"None": 75, "Bronze": 22, "Silver": 3,  "Gold": 0},
}

# All tiers: maximum level is Gold
_AVAILABLE_LEVELS: list = ["None", "Bronze", "Silver", "Gold"]

# ---------------------------------------------------------------------------
# ROOKIE GOLD CAPS (max Gold badges per tier)
# ---------------------------------------------------------------------------

_GOLD_CAPS: dict = {
    1: 10,
    2: 6,
    3: 3,
    4: 1,
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
    Generate a badge dict for one player. Gold is the maximum level.

    Priority badges (from archetype's badge_priorities) receive elevated
    distributions. Outcome tag modifiers add slight variance.
    """
    priority_badges = _get_priority_badges(archetype)

    # Outcome tag tweaks to priority weights (copy to avoid mutating constant)
    priority_w = dict(_PRIORITY_WEIGHTS.get(tier, _PRIORITY_WEIGHTS[4]))
    if outcome_tag == "guaranteed_good":
        _shift_weights_up(priority_w)
    elif outcome_tag in ("true_bust", "bust_risk"):
        _shift_weights_down(priority_w)
    elif outcome_tag == "limited_role_player" and tier >= 3:
        _shift_weights_down(priority_w)

    badges: dict = {}
    for _category, badge_list in ALL_BADGES.items():
        for badge in badge_list:
            is_priority = badge in priority_badges
            w_table = priority_w if is_priority else _NON_PRIORITY_WEIGHTS.get(
                tier, _NON_PRIORITY_WEIGHTS[4]
            )
            levels  = [lv for lv in _AVAILABLE_LEVELS if w_table.get(lv, 0) > 0]
            weights = [w_table[lv] for lv in levels]
            badges[badge] = random.choices(levels, weights=weights, k=1)[0]

    return badges


def enforce_rookie_badge_caps(player: dict, class_type: str = "Average") -> None:
    """
    Safety net applied after generation.

    Step 1 — Hard cap: any Hall of Fame or Legend badge is downgraded to Gold
    if it belongs to the archetype's priority badges, or removed (→ None) if
    it is not archetype-appropriate.

    Step 2 — Gold cap: if the total Gold count still exceeds the tier limit,
    demote the lowest-priority excess to Silver (priority badges kept first).
    """
    badges   = player["badges"]
    tier     = player["tier"]

    # Resolve archetype priority badges for this player
    from data.archetypes import ARCHETYPES
    archetype_def   = ARCHETYPES.get(player.get("archetype", ""), {})
    priority_badges = _get_priority_badges(archetype_def)

    # Step 1: Eliminate Hall of Fame and Legend — hard rule for rookies
    for badge in list(badges):
        if badges[badge] in ("Hall of Fame", "Legend"):
            badges[badge] = "Gold" if badge in priority_badges else "None"

    # Step 2: Enforce Gold count cap
    gold_cap  = _GOLD_CAPS.get(tier, 0)
    gold_list = [b for b, lv in badges.items() if lv == "Gold"]

    if len(gold_list) > gold_cap:
        excess = len(gold_list) - gold_cap
        # Demote non-priority Gold first, then priority if still over
        non_pri = [b for b in gold_list if b not in priority_badges]
        pri     = [b for b in gold_list if b in priority_badges]
        to_demote = (non_pri + pri)[:excess]
        for b in to_demote:
            badges[b] = "Silver"


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
    """Shift probability mass toward Gold/Silver (guaranteed_good boost)."""
    w["Gold"]   = int(w.get("Gold",   0) * 1.35)
    w["Silver"] = int(w.get("Silver", 0) * 1.15)
    for lv in ("None", "Bronze"):
        w[lv] = max(0, int(w.get(lv, 0) * 0.8))


def _shift_weights_down(w: dict) -> None:
    """Shift probability mass toward None/Bronze (bust/bust_risk reduction)."""
    for lv in ("Gold", "Silver"):
        w[lv] = max(0, int(w.get(lv, 0) * 0.55))
    w["None"]   = int(w.get("None",   0) * 1.4)
    w["Bronze"] = int(w.get("Bronze", 0) * 1.2)
