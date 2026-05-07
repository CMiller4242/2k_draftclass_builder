"""
Post-generation realism enforcement and class validation.

Functions operate on the player list (in-place) or on the assignments list
(before player generation) to fix structural problems that arise from
independent per-player random rolls.

Stages:
  enforce_top_pick_diversity()  — swap archetypes within same tier to spread
                                  position groups across top 5 picks
  enforce_height_distribution() — cap extreme heights, adjust weight
  validate_class()              — return human-readable warning strings
"""

import random
from collections import Counter
from typing import List, Tuple

from data.archetypes import ARCHETYPES
from data.class_rules import TIER1_CAPS

# ---------------------------------------------------------------------------
# POSITION GROUP CLASSIFICATION
# ---------------------------------------------------------------------------

# Maps archetype name → positional group used for diversity checks
_ARCH_GROUP = {
    # Guards
    "Movement Shooter":    "guard",
    "Iso Creator":         "guard",
    "Lockdown Guard":      "guard",
    "Shot Hunter":         "guard",
    # Wings
    "Two-Way Wing":        "wing",
    "Slashing Forward":    "wing",
    "Defensive Connector": "wing",
    "3-Level Scorer":      "wing",
    "Mid-Range Specialist":"wing",
    "High Flyer":          "wing",
    "Inside-Out Scorer":   "wing",
    # Bigs
    "Rim Running Big":     "big",
    "Playmaking Big":      "big",
    "Stretch Big":         "big",
    "Paint Bully":         "big",
    "Glass Cleaner":       "big",
    "Break Starter":       "big",
    "Putback Finisher":    "big",
}


def arch_pos_group(archetype_name: str) -> str:
    """Return 'guard', 'wing', or 'big' for an archetype name."""
    return _ARCH_GROUP.get(archetype_name, "wing")


# ---------------------------------------------------------------------------
# TOP-PICK POSITIONAL DIVERSITY (operates on assignments list, pre-generation)
# ---------------------------------------------------------------------------

def enforce_top_pick_diversity(
    assignments: List[Tuple[int, str]],
    class_flavor: str,
) -> List[Tuple[int, str]]:
    """
    Reorder assignments (within same tier only) so the top 5 picks include
    at least one guard, one wing, and one big when the pool allows it.

    Big-heavy flavor skips this check.
    Returns a new list with the same elements.
    """
    if class_flavor == "Big-heavy" or len(assignments) < 3:
        return list(assignments)

    assignments = list(assignments)
    top5_end = min(5, len(assignments))

    for attempt in range(3):  # up to 3 passes to converge
        top_groups = [arch_pos_group(a[1]) for a in assignments[:top5_end]]
        missing    = set(("guard", "wing", "big")) - set(top_groups)
        if not missing:
            break

        for need_group in list(missing):
            # Find a candidate from picks 6–15 with the needed group
            cand_idx = None
            for i in range(top5_end, min(15, len(assignments))):
                if arch_pos_group(assignments[i][1]) == need_group:
                    cand_idx = i
                    break
            if cand_idx is None:
                continue

            # Find the most over-represented group in top 5
            counts     = Counter(top_groups)
            overrep    = counts.most_common(1)[0][0]
            cand_tier  = assignments[cand_idx][0]

            # Swap with a same-tier pick in top 5 that is over-represented
            for i in range(top5_end):
                t_i, a_i = assignments[i]
                if t_i == cand_tier and arch_pos_group(a_i) == overrep:
                    assignments[i], assignments[cand_idx] = (
                        assignments[cand_idx], assignments[i]
                    )
                    break

    return assignments


# ---------------------------------------------------------------------------
# ARCHETYPE SPACING (operates on final player list, post-generation)
# ---------------------------------------------------------------------------

def enforce_archetype_spacing(players: list, min_gap: int = 3) -> None:
    """
    Swap players within the same tier to avoid same-archetype clustering
    in the top 15 picks. Does not reorder across tier boundaries.
    """
    if len(players) < 2:
        return

    top_n = min(15, len(players))

    for i in range(1, top_n):
        arch_i = players[i]["archetype"]
        tier_i = players[i]["tier"]

        # Check if same archetype appeared within min_gap picks
        window_start = max(0, i - min_gap)
        recent_archs = [players[j]["archetype"] for j in range(window_start, i)]
        if arch_i not in recent_archs:
            continue

        # Find a swap candidate further out (same tier, different archetype)
        for j in range(i + 1, min(top_n + min_gap, len(players))):
            if players[j]["tier"] == tier_i and players[j]["archetype"] != arch_i:
                players[i], players[j] = players[j], players[i]
                break


# ---------------------------------------------------------------------------
# HEIGHT DISTRIBUTION (operates on player list, post-generation)
# ---------------------------------------------------------------------------

# (player_count_lo, player_count_hi): (max_7ft2_plus, max_7ft0_plus)
_HEIGHT_CAPS_TABLE = [
    (1,  15,  1, 2),
    (16, 30,  1, 4),
    (31, 45,  2, 6),
    (46, 60,  3, 7),
]

_INCHES_7FT2 = 86   # 7'2"
_INCHES_7FT0 = 84   # 7'0"


def _get_height_caps(player_count: int, class_flavor: str) -> Tuple[int, int]:
    cap2, cap0 = 3, 7
    for lo, hi, c2, c0 in _HEIGHT_CAPS_TABLE:
        if lo <= player_count <= hi:
            cap2, cap0 = c2, c0
            break
    if class_flavor == "Big-heavy":
        cap2 += 1
        cap0 += 2
    return cap2, cap0


def enforce_height_distribution(
    players: list,
    player_count: int,
    class_flavor: str,
) -> None:
    """Reduce extreme heights in-place if caps are exceeded."""
    cap2, cap0 = _get_height_caps(player_count, class_flavor)

    # Process tallest-first
    bigs = sorted(
        [p for p in players if p["height_inches"] >= _INCHES_7FT0],
        key=lambda p: p["height_inches"],
        reverse=True,
    )

    for p in bigs:
        c2 = sum(1 for pl in players if pl["height_inches"] >= _INCHES_7FT2)
        c0 = sum(1 for pl in players if pl["height_inches"] >= _INCHES_7FT0)

        if c2 > cap2 and p["height_inches"] >= _INCHES_7FT2:
            _reduce_height(p, _INCHES_7FT2 - 1)
        elif c0 > cap0 and p["height_inches"] >= _INCHES_7FT0:
            _reduce_height(p, _INCHES_7FT0 - 1)
        else:
            break   # both caps satisfied


def _reduce_height(player: dict, target_max: int) -> None:
    old_h = player["height_inches"]
    if old_h <= target_max:
        return
    new_h = random.randint(max(72, target_max - 2), target_max)
    ratio = new_h / old_h
    player["height_inches"]  = new_h
    player["height_display"] = _to_ft(new_h)
    player["weight_lbs"]     = max(180, min(330, int(player["weight_lbs"] * ratio)))


def _to_ft(inches: int) -> str:
    return f"{inches // 12}'{inches % 12}\""


# ---------------------------------------------------------------------------
# GLOBAL VALIDATION
# ---------------------------------------------------------------------------

_STAR_ROLES = frozenset({
    "Franchise Player", "Perennial All-Star",
    "First-Option Scorer", "Defensive Anchor / All-Star",
    "All-Star Caliber", "Second-Option Star",
})

_STAR_OUTLOOKS = frozenset({
    "Franchise Cornerstone", "Perennial All-Star",
    "All-Star Caliber", "Future All-Star",
    "Immediate Contributor",
})


def get_tier1_cap(class_type: str, player_count: int) -> int:
    caps = TIER1_CAPS.get(class_type, (1, 2))
    return caps[0] if player_count <= 30 else caps[1]


def validate_class(
    players: list,
    class_type: str,
    player_count: int,
    class_flavor: str,
) -> List[str]:
    """
    Return a list of human-readable warning strings for any realism violations.
    Empty list = clean class.
    """
    warnings: List[str] = []

    # 1. Tier 1 inflation
    t1 = sum(1 for p in players if p["tier"] == 1)
    cap = get_tier1_cap(class_type, player_count)
    if t1 > cap:
        warnings.append(
            f"Tier 1 inflation: {t1} Tier 1 players "
            f"(cap for {class_type}, {'≤30' if player_count <= 30 else '31–60'} players: {cap})"
        )

    # 2. Top-3 positional clustering
    if class_flavor != "Big-heavy" and len(players) >= 3:
        top3_groups = [arch_pos_group(p["archetype"]) for p in players[:3]]
        if top3_groups.count("big") == 3:
            warnings.append("Top 3 picks are all bigs (PF/C) — add positional variety.")
        if top3_groups.count("guard") == 0 and player_count >= 10:
            warnings.append("No guard in top 3 picks.")

    # 3. Extreme height count
    cap2, cap0 = _get_height_caps(player_count, class_flavor)
    c2 = sum(1 for p in players if p["height_inches"] >= _INCHES_7FT2)
    if c2 > cap2:
        warnings.append(
            f"Height distribution: {c2} players at 7'2\"+ "
            f"(recommended max for {player_count} players: {cap2})"
        )

    # 4. Role / potential mismatches
    for p in players:
        pot  = p["attributes"].get("Potential", 0)
        role = p.get("projected_role", "")
        out  = p.get("development_outlook", "")
        if not p["is_bust"] and pot < 70 and role in _STAR_ROLES:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Potential {pot} but projected role is '{role}'"
            )
        if not p["is_bust"] and pot < 70 and out in _STAR_OUTLOOKS:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Potential {pot} but development outlook is '{out}'"
            )

    # 5. Back-to-back archetype clusters in top 15
    for i in range(1, min(15, len(players))):
        if players[i]["archetype"] == players[i - 1]["archetype"]:
            warnings.append(
                f"Archetype cluster: back-to-back {players[i]['archetype']} "
                f"at picks {players[i-1]['pick_number']} & {players[i]['pick_number']}"
            )

    # 6. Tier 4 with star labels (should not happen post-outlook fix)
    for p in players:
        if p["tier"] == 4 and not p["is_bust"]:
            out = p.get("development_outlook", "")
            if out in _STAR_OUTLOOKS:
                warnings.append(
                    f"#{p['pick_number']} {p['name']}: "
                    f"Tier 4 player has star outlook '{out}'"
                )

    # 7. Boom/Bust % integrity — should sum to 100
    for p in players:
        boom = p.get("boom_pct", 0)
        avg  = p.get("average_pct", 0)
        bust = p.get("bust_pct", 0)
        if boom + avg + bust != 100:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Boom/Avg/Bust % sums to {boom + avg + bust} (expected 100)"
            )

    # 8. Peak age window sanity — start < end, plausible range
    for p in players:
        start = p.get("peak_age_start", 0)
        end   = p.get("peak_age_end", 0)
        if start >= end:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Peak age window invalid ({start}–{end})"
            )
        elif start < 21 or end > 40:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Peak age window out of range ({start}–{end})"
            )

    # 9. Wingspan sanity (should be within ±8 inches of height)
    for p in players:
        h = p.get("height_inches", 0)
        w = p.get("wingspan_inches", 0)
        if w and h and abs(w - h) > 8:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Wingspan {w}\" unusual vs height {h}\""
            )

    # 10. Illegal rookie badge levels (HOF/Legend must never appear)
    _ILLEGAL_LEVELS = frozenset({"Hall of Fame", "Legend"})
    for p in players:
        illegal = [
            f"{badge}={level}"
            for badge, level in p.get("badges", {}).items()
            if level in _ILLEGAL_LEVELS
        ]
        if illegal:
            warnings.append(
                f"#{p['pick_number']} {p['name']}: "
                f"Illegal rookie badge level(s): {', '.join(illegal)}"
            )

    return warnings
