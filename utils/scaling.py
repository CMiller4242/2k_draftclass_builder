"""
Tier distribution scaling logic.

scale_tier_distribution() is the primary public API. It accepts a class_type
and player_count, then returns a dict of {tier: count} that respects the
class rules while adding natural randomness.

Key design decisions:
- Small classes (1–5) apply special edge-case logic so you never get
  unrealistic fractional tiers (e.g. 0.3 of a player).
- Large classes use proportional distribution with floor/ceiling enforcement.
- Randomness is intentional — two Generational classes of 30 will differ.
"""

import random
import math
from data.class_rules import CLASS_TYPES, TIER1_CAPS


def scale_tier_distribution(class_type: str, player_count: int) -> dict:
    """
    Returns {1: n, 2: n, 3: n, 4: n} tier counts that sum to player_count.

    Args:
        class_type: One of the CLASS_TYPES keys.
        player_count: Total players to generate (1–60).

    Returns:
        Dict mapping tier number to player count.
    """
    rules = CLASS_TYPES[class_type]
    dist = rules["base_distribution"]  # [T1_frac, T2_frac, T3_frac, T4_frac]
    guaranteed_t1 = rules.get("tier1_guaranteed", 0)
    star_floor = rules.get("star_floor", 0)

    if player_count == 1:
        return _single_player_distribution(class_type)

    if player_count <= 5:
        return _small_class_distribution(class_type, player_count)

    return _full_distribution(dist, player_count, guaranteed_t1, star_floor, class_type)


def get_tier1_cap(class_type: str, player_count: int) -> int:
    """Return the maximum allowed Tier 1 players for this class context."""
    caps = TIER1_CAPS.get(class_type, (1, 2))
    return caps[0] if player_count <= 30 else caps[1]


def _apply_tier_caps(tiers: dict, class_type: str, player_count: int) -> None:
    """Demote excess Tier 1 players to Tier 2 until the hard cap is met."""
    cap = get_tier1_cap(class_type, player_count)
    while tiers[1] > cap:
        tiers[1] -= 1
        tiers[2] += 1


def _single_player_distribution(class_type: str) -> dict:
    """
    For a single player, decide tier based on class_type character.
    Generational → almost certainly Tier 1.
    Weak → almost certainly Tier 3/4.
    """
    weights_by_type = {
        "Generational":          [75, 20,  4,  1],
        "Strong":                [30, 40, 25,  5],
        "Average":               [10, 25, 45, 20],
        "Weak":                  [ 2, 10, 45, 43],
        "Bust-heavy":            [ 3,  8, 28, 61],
        "Top-heavy":             [40, 25, 20, 15],
        "Deep role-player class":[ 2, 10, 60, 28],
    }
    weights = weights_by_type.get(class_type, [10, 20, 40, 30])
    tier = random.choices([1, 2, 3, 4], weights=weights, k=1)[0]
    result = {1: int(tier == 1), 2: int(tier == 2), 3: int(tier == 3), 4: int(tier == 4)}
    _apply_tier_caps(result, class_type, 1)
    return result


def _small_class_distribution(class_type: str, player_count: int) -> dict:
    """
    For 2–5 players, generate each player's tier individually to avoid
    fractional rounding issues.
    """
    weights_by_type = {
        "Generational":          [30, 35, 25, 10],
        "Strong":                [15, 30, 35, 20],
        "Average":               [ 5, 15, 45, 35],
        "Weak":                  [ 2,  8, 38, 52],
        "Bust-heavy":            [ 3,  8, 24, 65],
        "Top-heavy":             [20, 20, 25, 35],
        "Deep role-player class":[ 1,  8, 56, 35],
    }
    weights = weights_by_type.get(class_type, [8, 18, 42, 32])
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for _ in range(player_count):
        tier = random.choices([1, 2, 3, 4], weights=weights, k=1)[0]
        counts[tier] += 1
    _apply_tier_caps(counts, class_type, player_count)
    return counts


def _full_distribution(dist: list, player_count: int,
                       guaranteed_t1: int, star_floor: int,
                       class_type: str = "Average") -> dict:
    """
    For 6+ players, use fractional distribution with randomness.
    Adds ±variance to each fractional target before rounding.
    """
    # Add slight variance to each fraction (makes each class feel unique)
    variance = 0.04
    adjusted = []
    for frac in dist:
        noise = random.uniform(-variance, variance)
        adjusted.append(max(0.0, frac + noise))

    # Normalize so fractions sum to 1
    total = sum(adjusted)
    normalized = [f / total for f in adjusted]

    # Convert to raw counts (may not sum to player_count yet)
    raw = [n * player_count for n in normalized]

    # Floor everything, track remainder
    counts = [math.floor(n) for n in raw]
    remainders = [(raw[i] - counts[i], i) for i in range(4)]

    # Distribute remaining slots to highest remainders
    remaining = player_count - sum(counts)
    remainders.sort(key=lambda x: x[0], reverse=True)
    for i in range(remaining):
        counts[remainders[i][1]] += 1

    tiers = {1: counts[0], 2: counts[1], 3: counts[2], 4: counts[3]}

    # Enforce guaranteed minimums first, then hard caps (caps win over minimums)
    _enforce_guaranteed(tiers, guaranteed_t1, star_floor, player_count)
    _apply_tier_caps(tiers, class_type, player_count)

    return tiers


def _enforce_guaranteed(tiers: dict, guaranteed_t1: int, star_floor: int,
                        player_count: int) -> None:
    """
    Mutates tiers in-place to enforce minimum guarantees.
    Steals from Tier 4 first, then Tier 3.
    """
    # Enforce Tier 1 minimum
    while tiers[1] < guaranteed_t1 and player_count >= 5:
        if tiers[4] > 0:
            tiers[4] -= 1
        elif tiers[3] > 0:
            tiers[3] -= 1
        else:
            break
        tiers[1] += 1

    # Enforce combined Tier 1+2 minimum
    combined_stars = tiers[1] + tiers[2]
    while combined_stars < star_floor and player_count >= 3:
        if tiers[4] > 0:
            tiers[4] -= 1
        elif tiers[3] > 0:
            tiers[3] -= 1
        else:
            break
        tiers[2] += 1
        combined_stars += 1
