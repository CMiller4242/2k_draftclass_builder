"""
Sleeper prospect assignment and legendary profile enhancement.

Sleeper subtypes (mutually exclusive, per eligible player):
  legendary_sleeper  — extremely rare hidden franchise talent (~0.2% per eligible)
  star_sleeper       — rare hidden all-star talent
  starter_sleeper    — uncommon hidden starter talent
  role_sleeper       — common hidden solid-rotation player
  None               — no sleeper designation

Eligibility: Tier 3 or Tier 4, is_bust=False.

Non-legendary sleepers use COUNT-BASED scaling (guaranteed target range per
class size). Legendary sleepers remain probabilistic (~0.2% per eligible
player) and are assigned from the remaining pool after count-based sleepers.
"""

import random
from typing import Optional

from data.archetypes import ARCHETYPES
from utils.random_utils import clamp

# ---------------------------------------------------------------------------
# LEGENDARY SLEEPER OUTLOOK LABELS
# Intentionally understated — no "Franchise Cornerstone" here.
# ---------------------------------------------------------------------------

LEGENDARY_OUTLOOKS = [
    "Late Bloomer",
    "Hidden Star Upside",
    "Undervalued Skill Package",
    "Outlier Development Candidate",
]

# ---------------------------------------------------------------------------
# COUNT-BASED TARGET RANGES (non-legendary sleepers)
# (player_count_lo, player_count_hi, target_min, target_max)
# ---------------------------------------------------------------------------

_COUNT_TARGETS = [
    (1,  14,  0, 0),
    (15, 24,  1, 1),
    (25, 39,  1, 2),
    (40, 54,  2, 4),
    (55, 60,  3, 5),
]

# Non-legendary subtype weights: role (common) → star (rare)
_NON_LEGENDARY_WEIGHTS = {
    "role_sleeper":    60,
    "starter_sleeper": 28,
    "star_sleeper":    12,
}

# Legendary modifier by class type (probabilistic, applied to remaining pool)
_CLASS_TYPE_LEGENDARY_MULT = {
    "Generational":           1.5,
    "Strong":                 1.4,
    "Average":                1.0,
    "Weak":                   0.5,
    "Bust-heavy":             0.4,
    "Top-heavy":              0.8,
    "Deep role-player class": 1.2,
}

_BASE_LEGENDARY_PROB = 0.002   # ~0.2% per eligible player

# Badge level upgrade path
_BADGE_UPGRADE = {"Bronze": "Silver", "Silver": "Gold"}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def _target_sleeper_count(player_count: int, class_flavor: str) -> int:
    """Determine how many non-legendary sleepers this class should have."""
    mn, mx = 0, 0
    for lo, hi, t_min, t_max in _COUNT_TARGETS:
        if lo <= player_count <= hi:
            mn, mx = t_min, t_max
            break

    count = random.randint(mn, mx)
    if class_flavor == "High variance":
        count = min(mx + 1, count + random.randint(0, 1))
    elif class_flavor == "Low variance":
        count = max(0, count - 1)
    return count


def _legendary_prob(class_type: str, class_flavor: str, player_count: int) -> float:
    """Per-eligible-player legendary probability for this class context."""
    type_mult = _CLASS_TYPE_LEGENDARY_MULT.get(class_type, 1.0)
    is_hv     = (class_flavor == "High variance")

    if player_count < 40:
        count_mult = 0.15 if is_hv else 0.0
    else:
        count_mult = 1.5 if is_hv else 1.0

    return _BASE_LEGENDARY_PROB * type_mult * count_mult


def sleeper_pass(
    players: list,
    class_type: str,
    class_flavor: str,
    player_count: int,
) -> None:
    """
    Assign sleeper subtypes in-place across all players.

    Stage 1 — Count-based: pick a target number of non-legendary sleepers,
    randomly select eligible players, assign subtypes (role/starter/star).

    Stage 2 — Probabilistic: from REMAINING eligible players, each rolls
    independently for legendary_sleeper at ~0.2% base.

    Eligibility: Tier 3 or Tier 4, is_bust=False.
    """
    eligible = [p for p in players if p["tier"] in (3, 4) and not p["is_bust"]]

    # Stage 1: count-based non-legendary sleepers
    target = _target_sleeper_count(player_count, class_flavor)
    chosen = random.sample(eligible, min(target, len(eligible)))

    subtypes      = list(_NON_LEGENDARY_WEIGHTS.keys())
    subtype_wts   = list(_NON_LEGENDARY_WEIGHTS.values())

    for p in chosen:
        subtype = random.choices(subtypes, weights=subtype_wts, k=1)[0]
        p["sleeper_subtype"] = subtype
        if subtype == "star_sleeper":
            _apply_star_profile(p)
        elif subtype == "starter_sleeper":
            _apply_starter_profile(p)

    # Stage 2: legendary check on remaining eligible pool
    leg_prob    = _legendary_prob(class_type, class_flavor, player_count)
    chosen_set  = set(id(p) for p in chosen)
    remaining   = [p for p in eligible if id(p) not in chosen_set]

    for p in remaining:
        if random.random() < leg_prob:
            p["sleeper_subtype"] = "legendary_sleeper"
            _apply_legendary_profile(p)

    # Ensure every player has the field set
    for p in players:
        p.setdefault("sleeper_subtype", None)


# ---------------------------------------------------------------------------
# PROFILE ENHANCEMENT
# ---------------------------------------------------------------------------

def _apply_legendary_profile(player: dict) -> None:
    """
    Enhance a player in-place with a legendary sleeper hidden profile.

    The player still resembles a Tier 3/4 pick overall, but carries:
    - High potential (85–95)
    - One elite archetype-signature attribute (87–94)
    - Boosted IQ / consistency attributes (75–88)
    - Tendencies tightened toward archetype profile
    - One priority badge upgraded one level
    - Understated hidden-star development outlook
    """
    archetype     = ARCHETYPES.get(player["archetype"], {})
    priorities    = archetype.get("attribute_priorities", {})
    tendency_prof = archetype.get("tendency_profile", {})
    badge_prios   = archetype.get("badge_priorities", {})

    attrs  = player["attributes"]
    tends  = player["tendencies"]
    badges = player["badges"]

    # 1. Elevate potential into hidden-star range
    attrs["Potential"] = random.randint(85, 95)

    # 2. One elite signature attribute from archetype's top priorities
    # (guard against priority keys that are tendency names, not attributes)
    priority_attrs_in_dict = [a for a in priorities if a in attrs]
    if priority_attrs_in_dict:
        top_attr = priority_attrs_in_dict[0]
        attrs[top_attr] = clamp(random.randint(87, 94))

    # 3. Boost IQ / feel attributes — the hidden "basketball sense" tells
    iq_attrs = [
        "Shot IQ", "Pass IQ", "Pass Perception",
        "Offensive Consistency", "Defensive Consistency",
        "Help Defense IQ", "Intangibles",
    ]
    for attr in iq_attrs:
        if attr in attrs:
            attrs[attr] = clamp(max(attrs[attr], random.randint(75, 88)))

    # 4. Tighten tendencies toward archetype profile (without perfect alignment)
    for tend, target in tendency_prof.items():
        if tend in tends:
            nudged = int((tends[tend] + target) / 2) + random.randint(-5, 5)
            tends[tend] = clamp(nudged, lo=1, hi=99)

    # 5. Upgrade one priority badge by one level
    priority_badge_names: list = []
    for cat_badges in badge_prios.values():
        priority_badge_names.extend(cat_badges)

    upgradeable = [
        b for b in priority_badge_names
        if b in badges and badges[b] in _BADGE_UPGRADE
    ]
    if upgradeable:
        pick = random.choice(upgradeable)
        badges[pick] = _BADGE_UPGRADE[badges[pick]]

    # 6. Understated development language — no "Franchise Cornerstone"
    player["development_outlook"] = random.choice(LEGENDARY_OUTLOOKS)


def _apply_star_profile(player: dict) -> None:
    """Mild hidden-star treatment: elevated potential and a secondary attribute bump."""
    archetype  = ARCHETYPES.get(player["archetype"], {})
    priorities = archetype.get("attribute_priorities", {})
    attrs      = player["attributes"]

    # Potential into upper-role / borderline-star range
    attrs["Potential"] = clamp(max(attrs["Potential"], random.randint(78, 90)))

    # One secondary priority attribute lifted into solid-starter range
    # (guard against priority names that are tendencies, not attributes)
    priority_attrs_in_dict = [a for a in priorities if a in attrs]
    if len(priority_attrs_in_dict) >= 2:
        second_attr = priority_attrs_in_dict[1]
        attrs[second_attr] = clamp(max(attrs[second_attr], random.randint(78, 87)))

    # Light IQ nudge
    for attr in ("Shot IQ", "Offensive Consistency", "Intangibles"):
        if attr in attrs:
            attrs[attr] = clamp(max(attrs[attr], random.randint(70, 82)))


def _apply_starter_profile(player: dict) -> None:
    """Minimal treatment: potential leans toward upper end of normal range."""
    attrs = player["attributes"]
    # Nudge potential to the upper portion of Tier 3/4 normal range
    attrs["Potential"] = clamp(max(attrs["Potential"], random.randint(73, 83)))
