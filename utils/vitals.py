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

# Total-elite caps for tightened classes — even priority attrs are capped so
# a Tier 1 prospect doesn't end up with 7+ attributes ≥90 or 12+ attributes
# ≥85. (max_count_at_90, max_count_at_85). Demotes lowest-valued priorities
# above the cap. Star/elite classes (Generational, Strong, Top-heavy) are
# left alone so top-end profiles aren't flattened.
_TIGHTENED_TOTAL_ELITE_CAPS = {
    1: (4, 8),
    2: (3, 6),
    3: (1, 4),
    4: (0, 2),
}

_TIGHTENED_CLASSES = frozenset({
    "Average", "Weak", "Bust-heavy", "Deep role-player class"
})

# Attributes outside DURABILITY that should still count toward the elite cap.
# Mental/consistency attrs and a couple of "support" offensive attrs were
# previously exempt and quietly let top picks reach 10–12 attrs ≥85. Now
# included so the cap reflects total relevant-attribute breadth.
_ELITE_INCLUDE_EXTRAS = frozenset({
    # Mental
    "Pass Perception", "Defensive Consistency",
    "Help Defense IQ", "Offensive Consistency",
    # Offensive support attrs that were previously exempt as "mental"
    "Shot IQ",
    # Athleticism support
    "Hustle",
    # Free-throw / draw-foul should not freely spike either
    "Free Throw", "Draw Foul",
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


# Archetype "primary identity" attributes — the small set of priority attrs
# that define what the archetype is. A single 99 may live here for the
# tightened-class one-99 allowance; everything else clamps down.
_ARCH_PRIMARY_IDENTITY = {
    "Movement Shooter":     {"Three Point Shot", "Mid Range Shot"},
    "Iso Creator":          {"Ball Handle", "Mid Range Shot", "Driving Layup"},
    "Lockdown Guard":       {"Perimeter Defense", "Steal"},
    "Shot Hunter":          {"Three Point Shot", "Mid Range Shot"},
    "Two-Way Wing":         {"Perimeter Defense", "Three Point Shot"},
    "Slashing Forward":     {"Driving Dunk", "Driving Layup"},
    "Defensive Connector":  {"Perimeter Defense", "Help Defense IQ"},
    "3-Level Scorer":       {"Three Point Shot", "Mid Range Shot", "Driving Layup"},
    "Mid-Range Specialist": {"Mid Range Shot"},
    "High Flyer":           {"Driving Dunk", "Vertical"},
    "Inside-Out Scorer":    {"Three Point Shot", "Driving Layup"},
    "Rim Running Big":      {"Standing Dunk", "Vertical"},
    "Playmaking Big":       {"Pass Vision", "Pass IQ", "Pass Accuracy"},
    "Stretch Big":          {"Three Point Shot"},
    "Paint Bully":          {"Post Control", "Post Hook", "Strength"},
    "Glass Cleaner":        {"Offensive Rebound", "Defensive Rebound"},
    "Break Starter":        {"Pass Vision", "Pass Accuracy"},
    "Putback Finisher":     {"Offensive Rebound", "Standing Dunk"},
}

# Mental/consistency attrs that should almost never be 99 in tightened classes.
_NEVER_99_IN_TIGHTENED = frozenset({
    "Pass Perception", "Defensive Consistency",
    "Help Defense IQ", "Offensive Consistency",
    "Shot IQ", "Hustle",
    "Free Throw", "Draw Foul",
    "Stamina", "Agility",
})


def clamp_extreme_99s(player: dict, class_type: str) -> None:
    """
    Make 99 ratings very rare in tightened classes (Average / Weak / etc.).

    - Mental/consistency/support attrs in _NEVER_99_IN_TIGHTENED never hit 99.
    - At most ONE 99 is allowed across non-durability attrs, and only when it
      sits on a primary archetype-identity attribute.
    - Excess 99s are clamped to 94–96 (still elite, not max).
    - Durability is left alone (always near-max by design).
    - Star/Generational classes are untouched.
    """
    if class_type not in _TIGHTENED_CLASSES:
        return

    arch = player.get("archetype", "")
    primary_identity = _ARCH_PRIMARY_IDENTITY.get(arch, set())

    attrs = player["attributes"]

    # Step 1: never-99 attrs — clamp regardless of role
    for k in list(attrs.keys()):
        if k in _NEVER_99_IN_TIGHTENED and attrs.get(k, 0) >= 99:
            attrs[k] = random.randint(92, 95)

    # Step 2: at most one 99 total, must be primary identity
    nondur_99s = [
        (k, v) for k, v in attrs.items()
        if k not in _SKIP_ATTRS
        and k not in DURABILITY_ATTRIBUTES
        and v >= 99
    ]
    if not nondur_99s:
        return

    # Pick the 99 to keep: prefer one in primary identity, else demote all.
    keeper = None
    for k, _v in nondur_99s:
        if k in primary_identity:
            keeper = k
            break

    for k, _v in nondur_99s:
        if k == keeper:
            continue
        attrs[k] = random.randint(94, 96)


# ---------------------------------------------------------------------------
# ARCHETYPE-SPECIFIC POST-GENERATION CLEANUP
# ---------------------------------------------------------------------------

def enforce_archetype_attr_separation(player: dict, class_type: str) -> None:
    """
    Prevent specific archetype overlaps that erode archetype identity.

    Currently:
      - Paint Bully should not have BOTH Offensive Rebound AND Defensive
        Rebound elite (≥90) at the same time. Glass Cleaner owns extreme
        rebounding. For Paint Bully in tightened classes, if both rebounds
        sit ≥85, demote the smaller one (or Offensive Rebound by default,
        since Glass Cleaner owns OREB) to 78–84. Allows good rebounding,
        avoids dual-elite rebounding.
    """
    if class_type not in _TIGHTENED_CLASSES:
        return
    arch = player.get("archetype", "")
    attrs = player["attributes"]

    if arch == "Paint Bully":
        oreb = attrs.get("Offensive Rebound", 0)
        dreb = attrs.get("Defensive Rebound", 0)
        # If both simultaneously elite (≥85), demote the lower one. If both
        # are equal/very high, prefer demoting OREB (Glass Cleaner identity).
        if oreb >= 85 and dreb >= 85:
            if oreb >= dreb:
                attrs["Offensive Rebound"] = random.randint(72, 80)
            else:
                attrs["Defensive Rebound"] = random.randint(76, 84)
        # Hard ceiling: neither rebound stat hits 90+ on a Paint Bully in
        # tightened classes — that lane belongs to Glass Cleaner.
        if attrs.get("Offensive Rebound", 0) >= 90:
            attrs["Offensive Rebound"] = random.randint(80, 86)
        if attrs.get("Defensive Rebound", 0) >= 90:
            attrs["Defensive Rebound"] = random.randint(82, 88)


def enforce_total_elite_caps(player: dict, class_type: str) -> None:
    """
    For tightened classes (Average / Weak / Bust-heavy / Deep role-player),
    cap how many attributes can be ≥90 and ≥85 in total — including
    priority attributes AND mental/consistency/support attributes. Keeps
    top picks from reading "elite at everything", and prevents the leak
    where Pass Perception / Defensive Consistency / Help Defense IQ /
    Offensive Consistency / Shot IQ / Hustle pile on at 85–95 because
    they weren't previously counted.

    Demotion preserves archetype identity by demoting the LOWEST-valued
    over-threshold attributes first. Mental/Hustle/etc. are demoted before
    archetype priority attrs at equal value (the priority list defines
    identity). Durability stays exempt.
    """
    if class_type not in _TIGHTENED_CLASSES:
        return
    tier = player["tier"]
    cap90, cap85 = _TIGHTENED_TOTAL_ELITE_CAPS[tier]

    attrs = player["attributes"]

    # Look up archetype priorities so we demote off-priority attrs first.
    from data.archetypes import ARCHETYPES
    arch = ARCHETYPES.get(player.get("archetype", ""), {})
    priority_keys = set(arch.get("attribute_priorities", {}).keys())

    def _eligible(k: str) -> bool:
        if k in _SKIP_ATTRS:
            return False
        if k in DURABILITY_ATTRIBUTES:
            return False
        # Include mental/consistency only when they appear in the explicit
        # extras list; otherwise still skip MENTAL_ATTRIBUTES if any future
        # entry shouldn't count.
        if k in MENTAL_ATTRIBUTES and k not in _ELITE_INCLUDE_EXTRAS:
            return False
        return True

    # Sort key: (value asc, off-priority first, mental/extras first).
    # Demote lowest-value first; at equal value prefer off-priority extras
    # so primary archetype identity (e.g. Post Hook on Paint Bully) survives.
    def _demote_priority(k: str, v: int) -> tuple:
        is_priority = k in priority_keys
        is_extra = k in _ELITE_INCLUDE_EXTRAS
        # Lower tuple sorts earlier → demoted first
        # value asc, then off-priority before priority, then extras before others
        return (v, 0 if not is_priority else 1, 0 if is_extra else 1)

    # Cap ≥90 first, then ≥85 (descending threshold ordering).
    over_90 = sorted(
        [(k, v) for k, v in attrs.items() if _eligible(k) and v >= 90],
        key=lambda kv: _demote_priority(*kv),
    )
    excess = max(0, len(over_90) - cap90)
    for k, _v in over_90[:excess]:
        attrs[k] = random.randint(85, 89)

    over_85 = sorted(
        [(k, v) for k, v in attrs.items() if _eligible(k) and v >= 85],
        key=lambda kv: _demote_priority(*kv),
    )
    excess = max(0, len(over_85) - cap85)
    for k, _v in over_85[:excess]:
        attrs[k] = random.randint(78, 84)


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
