"""
Sleeper prospect assignment and legendary profile enhancement.

Sleeper subtypes (mutually exclusive, per eligible player):
  legendary_sleeper  — extremely rare hidden franchise talent (~0.2% base)
  star_sleeper       — rare hidden all-star talent (~1.5% base)
  starter_sleeper    — uncommon hidden starter talent (~6% base)
  role_sleeper       — common hidden solid-rotation player (~18% base)
  None               — no sleeper designation

Eligibility: Tier 3 or Tier 4, is_bust=False.

Class-level context (class_type, class_flavor, player_count) modulates
the legendary probability only; the other tiers use a flat flavor multiplier.
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
# BASE PROBABILITIES (per eligible player)
# ---------------------------------------------------------------------------

_BASE_PROBS = {
    "legendary_sleeper": 0.002,   # ~0.2%
    "star_sleeper":      0.015,   # ~1.5%
    "starter_sleeper":   0.060,   # ~6.0%
    "role_sleeper":      0.180,   # ~18.0%
}

# Legendary modifier by class type
_CLASS_TYPE_LEGENDARY_MULT = {
    "Generational":           1.5,
    "Strong":                 1.4,
    "Average":                1.0,
    "Weak":                   0.5,
    "Bust-heavy":             0.4,
    "Top-heavy":              0.8,
    "Deep role-player class": 1.2,
}

# All-sleeper multiplier by class flavor
_FLAVOR_MULT = {
    "High variance": 1.5,
    "Low variance":  0.6,
}

# Badge level upgrade path
_BADGE_UPGRADE = {"Bronze": "Silver", "Silver": "Gold"}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def compute_sleeper_probs(
    class_type: str,
    class_flavor: str,
    player_count: int,
) -> dict:
    """
    Return per-eligible-player probabilities for this class context.

    Legendary probability is gated by player_count unless High Variance is
    active; other tiers receive a flat flavor multiplier.
    """
    is_high_variance = (class_flavor == "High variance")
    type_mult   = _CLASS_TYPE_LEGENDARY_MULT.get(class_type, 1.0)
    flavor_mult = _FLAVOR_MULT.get(class_flavor, 1.0)

    if player_count < 40:
        count_mult = 0.15 if is_high_variance else 0.0
    else:
        count_mult = 1.0

    legendary_prob = (
        _BASE_PROBS["legendary_sleeper"]
        * type_mult
        * flavor_mult
        * count_mult
    )

    return {
        "legendary_sleeper": legendary_prob,
        "star_sleeper":      _BASE_PROBS["star_sleeper"]    * flavor_mult,
        "starter_sleeper":   _BASE_PROBS["starter_sleeper"] * flavor_mult,
        "role_sleeper":      _BASE_PROBS["role_sleeper"]    * flavor_mult,
    }


def assign_sleeper_subtype(probs: dict) -> Optional[str]:
    """
    Single roll against cumulative thresholds — highest-tier hit wins.
    Returns the subtype string or None.
    """
    roll = random.random()
    threshold = 0.0
    for subtype in ("legendary_sleeper", "star_sleeper", "starter_sleeper", "role_sleeper"):
        threshold += probs[subtype]
        if roll < threshold:
            return subtype
    return None


def sleeper_pass(
    players: list,
    class_type: str,
    class_flavor: str,
    player_count: int,
) -> None:
    """
    Assign sleeper subtypes in-place across all players.
    Only Tier 3/4 non-bust players are eligible.
    Legendary sleepers also receive an enhanced hidden profile.
    """
    probs = compute_sleeper_probs(class_type, class_flavor, player_count)

    for player in players:
        if player["tier"] not in (3, 4) or player["is_bust"]:
            player["sleeper_subtype"] = None
            continue

        subtype = assign_sleeper_subtype(probs)
        player["sleeper_subtype"] = subtype

        if subtype == "legendary_sleeper":
            _apply_legendary_profile(player)
        elif subtype == "star_sleeper":
            _apply_star_profile(player)
        elif subtype == "starter_sleeper":
            _apply_starter_profile(player)
        # role_sleeper: label only, no stat change


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
