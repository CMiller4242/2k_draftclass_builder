"""
Core player generation logic.

generate_player() is the main entry point. It:
1. Selects physical attributes (height, weight)
2. Builds full attribute set from archetype priorities + tier modifiers
3. Generates tendencies based on archetype tendency profile
4. Assigns badges based on tier budget and archetype priorities
5. Applies bust logic for players who underperform
"""

import random
from typing import Optional

from data.archetypes import ARCHETYPES, TIER_ATTRIBUTE_MODIFIERS
from data.fields import (
    ALL_ATTRIBUTES, ALL_TENDENCIES, ALL_BADGES,
    ATTRIBUTE_CATEGORIES, TENDENCY_CATEGORIES,
    MISC_ATTRIBUTES, OFFENSIVE_ATTRIBUTES, DEFENSIVE_ATTRIBUTES,
    ATHLETICISM_ATTRIBUTES, DURABILITY_ATTRIBUTES, MENTAL_ATTRIBUTES,
    JUMP_SHOOTING_TENDENCIES, LAYUP_DUNK_TENDENCIES,
    DRIVE_SETUP_TENDENCIES, DRIVING_TENDENCIES, PASSING_TENDENCIES,
    POST_GAME_TENDENCIES, FREELANCE_TENDENCIES, DEFENSE_TENDENCIES,
)
from data.badge_data import BADGE_BUDGET
from data.class_rules import BUST_RISK_BY_TIER, PROJECTED_ROLES
from utils.outlook import assign_player_outlook
from utils.random_utils import (
    clamp, rand_in_range, jitter, scale_range, generate_name,
    weighted_choice, pick_weighted_from_dict,
)


def generate_player(
    tier: int,
    archetype_name: str,
    bust_modifier: float = 0.0,
    player_number: int = 0,
    build_name: str = "",
    outcome_tag: str = "normal",
) -> dict:
    """
    Generate a complete 2K player profile.

    Args:
        tier:           1–4 (Superstar → Role Player/Bust)
        archetype_name: Key from ARCHETYPES dict
        bust_modifier:  Kept for backwards compat; ignored when outcome_tag is set
        player_number:  Draft pick number (for ordering)
        build_name:     Optional 2K Labs build alias (used in CSV / display)
        outcome_tag:    Pre-assigned outcome from outcome_tags.py

    Returns:
        Full player dict ready for display/export.
    """
    archetype = ARCHETYPES[archetype_name]
    tier_mod = TIER_ATTRIBUTE_MODIFIERS[tier]

    # Bust determination driven by outcome_tag when provided
    if outcome_tag == "true_bust":
        is_bust = True
    elif outcome_tag in ("guaranteed_good", "bust_risk", "limited_role_player", "normal"):
        is_bust = False
    else:
        # Fallback for callers that skip outcome_tag
        base_bust_prob = BUST_RISK_BY_TIER[tier]
        is_bust = random.random() < (base_bust_prob + bust_modifier)

    # Physical attributes
    height_in = random.randint(*archetype["height_range_inches"])
    weight_lb = random.randint(*archetype["weight_range_lbs"])

    # Position — pick primary from valid positions for archetype
    valid_positions = archetype["valid_positions"]
    position_str = random.choice(valid_positions)
    if "/" in position_str:
        primary_pos, secondary_pos = position_str.split("/")
    else:
        primary_pos = position_str
        secondary_pos = None

    # Generate attributes
    attributes = _generate_attributes(archetype, tier_mod, is_bust)

    # Potential: ceiling attribute, influenced by outcome tag for volatility
    potential = _generate_potential(tier, is_bust, outcome_tag)
    attributes["Potential"] = potential

    # Generate tendencies
    tendencies = _generate_tendencies(archetype, tier)

    # Generate badges
    badges = _generate_badges(archetype, tier)

    # Pick projected role (tier-gated)
    projected_role = random.choice(PROJECTED_ROLES[tier])

    # Build the initial player dict
    player = {
        "name": generate_name(),
        "pick_number": player_number,
        "position": primary_pos,
        "secondary_position": secondary_pos,
        "height_inches": height_in,
        "height_display": _inches_to_feetinches(height_in),
        "weight_lbs": weight_lb,
        "archetype": archetype_name,
        # build_name: a 2K Labs build alias when available (empty string otherwise)
        "build_name": build_name,
        "tier": tier,
        "tier_label": _tier_label(tier),
        "is_bust": is_bust,
        "outcome_tag": outcome_tag,
        "sleeper_subtype": None,    # filled by sleeper_pass in generate_class
        "projected_role": projected_role,
        "development_outlook": "",  # filled by assign_player_outlook below
        "bust_risk": "",            # filled by assign_player_outlook below
        "attributes": attributes,
        "tendencies": tendencies,
        "badges": badges,
    }

    # Assign coherent outlook labels (tier + potential + bust-gated)
    player.update(assign_player_outlook(player))

    return player


# ---------------------------------------------------------------------------
# ATTRIBUTE GENERATION
# ---------------------------------------------------------------------------

def _generate_attributes(archetype: dict, tier_mod: int, is_bust: bool) -> dict:
    """Build a full attribute dict from archetype priority ranges + tier modifier."""
    priorities = archetype["attribute_priorities"]
    bust_profile = archetype.get("bust_profile", {})
    attrs = {}

    # Priority attributes — use defined ranges with tier scaling
    for attr, base_range in priorities.items():
        if attr in ALL_ATTRIBUTES:
            scaled = scale_range(base_range, tier_mod)
            val = rand_in_range(scaled)
            # Apply bust penalty if applicable
            if is_bust and attr in bust_profile:
                penalty_range = bust_profile[attr]
                penalty = random.randint(*penalty_range)
                val = clamp(val + penalty)
            attrs[attr] = val

    # Non-priority attributes — generate baseline values scaled by tier
    for attr in ALL_ATTRIBUTES:
        if attr in attrs or attr == "Potential":
            continue

        # Default baseline depends on attribute category
        baseline = _default_baseline(attr)
        scaled = scale_range(baseline, tier_mod)
        val = rand_in_range(scaled)

        # Busts get additional random penalties on non-priority stats
        if is_bust:
            bust_penalty = random.randint(-12, -3)
            val = clamp(val + bust_penalty)

        attrs[attr] = val

    return attrs


def _default_baseline(attr: str) -> tuple:
    """Return the default (min, max) baseline for a non-priority attribute."""
    # Durability is always near-max to avoid excessive injuries by default
    if attr in DURABILITY_ATTRIBUTES:
        return (75, 90)
    # Intangibles
    if attr == "Intangibles":
        return (55, 72)
    # Mental attributes
    if attr in MENTAL_ATTRIBUTES:
        return (55, 72)
    # Most offensive/defensive/athleticism attributes default to average
    return (42, 60)


# ---------------------------------------------------------------------------
# POTENTIAL
# ---------------------------------------------------------------------------

def _generate_potential(tier: int, is_bust: bool, outcome_tag: str = "normal") -> int:
    """
    Potential represents the ceiling — it's NOT current ability.

    Ranges overlap slightly between tiers to allow natural variance:
      Tier 1: 88–98  |  Tier 2: 80–90  |  Tier 3: 72–84  |  Tier 4: 55–75
    Outcome tag modifiers add further volatility so classes feel uneven.
    """
    base_ranges = {1: (88, 98), 2: (80, 90), 3: (72, 84), 4: (55, 75)}
    base = rand_in_range(base_ranges[tier])

    # Paper prospects: high ceiling scouts love, real-world outcome disappoints
    if outcome_tag in ("true_bust", "bust_risk") and tier <= 2:
        base = clamp(base + random.randint(5, 12))
    elif outcome_tag == "guaranteed_good":
        base = clamp(base + random.randint(2, 6))
    elif is_bust and tier <= 2:
        # Fallback for legacy callers
        base = clamp(base + random.randint(3, 8))

    # Inter-tier volatility: rare spike/dip (±3 random noise)
    noise = random.choices(
        [0, random.randint(-4, -1), random.randint(1, 5)],
        weights=[70, 15, 15], k=1
    )[0]
    return clamp(base + noise)


# ---------------------------------------------------------------------------
# TENDENCY GENERATION
# ---------------------------------------------------------------------------

def _generate_tendencies(archetype: dict, tier: int) -> dict:
    """
    Build a full tendency dict. Archetype tendency_profile provides target
    values for key tendencies; all others get neutral values with noise.
    """
    profile = archetype.get("tendency_profile", {})
    tendencies = {}

    for tendency in ALL_TENDENCIES:
        if tendency in profile:
            # Archetype-defined tendency: use the target with ±10 noise
            base = profile[tendency]
            val = clamp(base + random.randint(-10, 10), lo=1, hi=99)
        else:
            # Default neutral tendency
            val = clamp(random.randint(35, 65), lo=1, hi=99)
        tendencies[tendency] = val

    return tendencies


# ---------------------------------------------------------------------------
# BADGE GENERATION
# ---------------------------------------------------------------------------

def _generate_badges(archetype: dict, tier: int) -> dict:
    """
    Assign badge levels based on tier budget and archetype priorities.
    Priority badges have a higher chance of receiving elevated levels.
    """
    budget = BADGE_BUDGET[tier]
    priority_map = archetype.get("badge_priorities", {})

    # Flatten priority badge names with their category
    priority_badges = set()
    for cat_badges in priority_map.values():
        priority_badges.update(cat_badges)

    badges = {}

    for category, badge_list in ALL_BADGES.items():
        for badge in badge_list:
            level = _pick_badge_level(badge, tier, budget, priority_badges)
            badges[badge] = level

    return badges


def _pick_badge_level(badge: str, tier: int, budget: dict,
                      priority_badges: set) -> str:
    """Pick a badge level for one badge, respecting tier constraints."""
    is_priority = badge in priority_badges

    # Available levels for this tier
    available_levels = ["None", "Bronze", "Silver", "Gold", "Hall of Fame"]
    if tier == 1:
        available_levels.append("Legend")

    # Build weight distribution
    # Base weights favor lower levels heavily; priority badges shift upward
    if is_priority and tier <= 2:
        weights = {
            "None":        5,
            "Bronze":      15,
            "Silver":      25,
            "Gold":        30,
            "Hall of Fame": 20,
            "Legend":      5 if tier == 1 else 0,
        }
    elif is_priority and tier == 3:
        weights = {
            "None":        15,
            "Bronze":      30,
            "Silver":      30,
            "Gold":        20,
            "Hall of Fame": 5,
            "Legend":      0,
        }
    elif is_priority and tier == 4:
        weights = {
            "None":        25,
            "Bronze":      40,
            "Silver":      25,
            "Gold":        10,
            "Hall of Fame": 0,
            "Legend":      0,
        }
    else:
        # Non-priority: mostly None/Bronze, rare Silver
        weights = {
            "None":        55,
            "Bronze":      28,
            "Silver":      12,
            "Gold":        4,
            "Hall of Fame": 1,
            "Legend":      0,
        }

    levels = [l for l in available_levels if weights.get(l, 0) > 0]
    w = [weights[l] for l in levels]
    return random.choices(levels, weights=w, k=1)[0]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _tier_label(tier: int) -> str:
    labels = {
        1: "Superstar",
        2: "All-Star / High-End Starter",
        3: "Starter / Rotation",
        4: "Role Player / Bust",
    }
    return labels.get(tier, "Unknown")


def _inches_to_feetinches(inches: int) -> str:
    feet = inches // 12
    remaining = inches % 12
    return f"{feet}'{remaining}\""
