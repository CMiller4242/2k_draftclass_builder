"""
Physical vitals and projection fields for generated players.

Provides:
  - generate_wingspan(height_inches, archetype_name)      → int (inches)
  - normalize_rookie_attribute_strength(player)           → None (in-place)
  - generate_boom_avg_bust_percentages(player)            → {"boom_pct", "average_pct", "bust_pct"}
  - generate_peak_age_window(player)                      → {"peak_age_start", "peak_age_end"}
"""

import random

# ---------------------------------------------------------------------------
# WINGSPAN
# ---------------------------------------------------------------------------

_WING_OFFSET = {
    "guard": (-2,  3),
    "wing":  (-1,  4),
    "big":   ( 0,  5),
}

_ARCH_GROUP = {
    "Movement Shooter":    "guard",
    "Iso Creator":         "guard",
    "Shot Hunter":         "guard",
    "Lockdown Guard":      "guard",
    "Two-Way Wing":        "wing",
    "Slashing Forward":    "wing",
    "Defensive Connector": "wing",
    "3-Level Scorer":      "wing",
    "Mid-Range Specialist":"wing",
    "High Flyer":          "wing",
    "Inside-Out Scorer":   "wing",
    "Stretch Big":         "big",
    "Rim Running Big":     "big",
    "Playmaking Big":      "big",
    "Glass Cleaner":       "big",
    "Paint Bully":         "big",
    "Break Starter":       "big",
    "Putback Finisher":    "big",
}


def _wingspan_feet_str(inches: int) -> str:
    return f"{inches // 12}'{inches % 12}\""


def generate_wingspan(height_inches: int, archetype_name: str) -> int:
    """Return wingspan in inches (height ± archetype-adjusted offset)."""
    group = _ARCH_GROUP.get(archetype_name, "wing")
    lo, hi = _WING_OFFSET[group]
    return height_inches + random.randint(lo, hi)


# ---------------------------------------------------------------------------
# ROOKIE ATTRIBUTE NORMALIZATION
# ---------------------------------------------------------------------------

# (threshold, max_attrs_above_threshold)
_ATTR_CAPS = {
    1: (93, 4),
    2: (88, 6),
    3: (85, 3),
    4: (80, 1),
}

_SKIP_ATTRS = {"Potential"}

# Attribute categories considered "off-identity skill spread" — count
# limits below apply to non-priority attributes so an archetype's signature
# tools stay intact.
from data.fields import DURABILITY_ATTRIBUTES, MENTAL_ATTRIBUTES

# Average/Balanced specialization caps. (threshold, max_off_identity_above)
# Off-identity = attribute is NOT in the archetype's attribute_priorities.
# Ensures top picks don't randomly become elite at 6+ unrelated attributes.
_SPECIALIZATION_CAPS = {
    1: (85, 2),
    2: (85, 2),
    3: (82, 1),
    4: (80, 0),
}

_TIGHTENED_CLASSES = frozenset({
    "Average", "Weak", "Bust-heavy", "Deep role-player class"
})

# Athleticism (Speed/Vertical/Strength/Agility) is treated as identity for
# wing/big archetypes by default — even non-priority athleticism on a
# Slashing Forward shouldn't be clipped just because it isn't in the priority
# dict. Excluded from the off-identity counter.
_ATHLETICISM_TOLERANT = frozenset({
    "Speed", "Acceleration", "Vertical", "Strength", "Stamina", "Hustle",
})


def normalize_rookie_attribute_strength(player: dict) -> None:
    """
    Cap attribute inflation in-place. Rookies can't have too many elite-level
    attributes regardless of tier — demotes the lowest-priority excess ones.
    """
    tier = player["tier"]
    attrs = player["attributes"]
    threshold, max_above = _ATTR_CAPS[tier]

    over = sorted(
        [(k, v) for k, v in attrs.items() if k not in _SKIP_ATTRS and v > threshold],
        key=lambda x: x[1],
    )

    excess_count = max(0, len(over) - max_above)
    # Demote the lowest-valued ones first (weakest excess attributes)
    for attr, _ in over[:excess_count]:
        attrs[attr] = random.randint(threshold - 5, threshold)


def enforce_attribute_specialization(player: dict, class_type: str) -> None:
    """
    For Average / Weak / Bust-heavy / Deep role-player classes: limit how
    many off-identity attributes can sit above the elite threshold.

    Identity = archetype's attribute_priorities + tolerant athleticism set.
    Off-identity attrs above the threshold get demoted to good-but-not-elite
    so a Slashing Forward isn't simultaneously elite at handle, defense,
    interior + perimeter D, strength, agility AND vertical.

    Durability + mental attributes are exempt — those are baseline.
    """
    if class_type not in _TIGHTENED_CLASSES:
        return
    tier = player["tier"]
    threshold, max_off = _SPECIALIZATION_CAPS[tier]

    # Look up archetype priorities
    from data.archetypes import ARCHETYPES
    arch = ARCHETYPES.get(player.get("archetype", ""), {})
    priority_keys = set(arch.get("attribute_priorities", {}).keys())

    attrs = player["attributes"]
    off_identity_high = []
    for k, v in attrs.items():
        if k in _SKIP_ATTRS or k in priority_keys:
            continue
        if k in DURABILITY_ATTRIBUTES or k in MENTAL_ATTRIBUTES:
            continue
        if k in _ATHLETICISM_TOLERANT:
            continue
        if v >= threshold:
            off_identity_high.append((k, v))

    excess = len(off_identity_high) - max_off
    if excess <= 0:
        return

    # Demote the lowest-valued excess off-identity attrs first.
    off_identity_high.sort(key=lambda x: x[1])
    for k, _v in off_identity_high[:excess]:
        attrs[k] = random.randint(max(60, threshold - 8), threshold - 2)


# ---------------------------------------------------------------------------
# BOOM / AVERAGE / BUST PERCENTAGES
# ---------------------------------------------------------------------------

def generate_boom_avg_bust_percentages(player: dict) -> dict:
    """
    Return {"boom_pct": int, "average_pct": int, "bust_pct": int} summing to 100.

    High boom = high potential + positive outcome tag.
    High bust = is_bust=True or bust outcome tags.
    """
    tier        = player["tier"]
    potential   = player["attributes"].get("Potential", 75)
    is_bust     = player.get("is_bust", False)
    outcome_tag = player.get("outcome_tag", "normal")

    # Tier-based starting points
    if tier == 1:
        boom = 55 + (potential - 90) * 2
        bust = 10
    elif tier == 2:
        boom = 38 + (potential - 82) * 2
        bust = 15
    elif tier == 3:
        boom = 20 + (potential - 74) * 2
        bust = 25
    else:
        boom = 10 + max(0, (potential - 60) // 2)
        bust = 38

    # Outcome tag adjustments
    if outcome_tag == "guaranteed_good":
        boom += 15
        bust -= 10
    elif outcome_tag == "bust_risk":
        boom -= 10
        bust += 15
    elif outcome_tag == "true_bust":
        boom -= 20
        bust += 25
    elif outcome_tag == "limited_role_player":
        boom -= 8
        bust += 5

    # is_bust override
    if is_bust:
        boom = max(5, boom - 15)
        bust = min(70, bust + 20)

    # Clamp and normalize to exactly 100
    boom = max(5, min(85, boom))
    bust = max(5, min(70, bust))
    avg  = max(5, 100 - boom - bust)

    total = boom + avg + bust
    boom  = round(boom / total * 100)
    bust  = round(bust / total * 100)
    avg   = 100 - boom - bust

    return {"boom_pct": boom, "average_pct": avg, "bust_pct": bust}


# ---------------------------------------------------------------------------
# PEAK AGE WINDOW
# ---------------------------------------------------------------------------

def generate_peak_age_window(player: dict) -> dict:
    """Return {"peak_age_start": int, "peak_age_end": int}."""
    tier      = player["tier"]
    potential = player["attributes"].get("Potential", 75)

    if tier == 1:
        start    = random.randint(24, 27)
        duration = random.randint(5, 7) + (1 if potential >= 95 else 0)
    elif tier == 2:
        start    = random.randint(24, 27)
        duration = random.randint(4, 6)
    elif tier == 3:
        start    = random.randint(23, 26)
        duration = random.randint(3, 5)
    else:
        start    = random.randint(23, 26)
        duration = random.randint(2, 4)

    return {"peak_age_start": start, "peak_age_end": start + duration}
