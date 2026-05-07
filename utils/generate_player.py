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
from data.class_rules import BUST_RISK_BY_TIER, PROJECTED_ROLES, TRUE_BUST_ROLES
from utils.outlook import assign_player_outlook
from utils.random_utils import (
    clamp, rand_in_range, jitter, scale_range, generate_name,
    weighted_choice, pick_weighted_from_dict,
)
from utils.vitals import (
    generate_wingspan, normalize_rookie_attribute_strength,
    enforce_attribute_specialization,
    generate_boom_avg_bust_percentages, generate_peak_age_window,
    _wingspan_feet_str,
)
from utils.badge_gen import generate_badges_for_archetype, enforce_rookie_badge_caps
from data.archetype_identity import (
    get_tendency_identity, IDENTITY_BANDS,
)


def generate_player(
    tier: int,
    archetype_name: str,
    bust_modifier: float = 0.0,
    player_number: int = 0,
    build_name: str = "",
    outcome_tag: str = "normal",
    class_type: str = "Average",
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
    potential = _generate_potential(tier, is_bust, outcome_tag, class_type)
    attributes["Potential"] = potential

    # Generate tendencies (archetype-driven with outcome_tag variance)
    tendencies = generate_tendencies_for_archetype(
        archetype, tier, outcome_tag, archetype_name=archetype_name,
    )

    # Generate badges (archetype-driven + attribute-eligibility-gated)
    badges = generate_badges_for_archetype(
        archetype, tier, outcome_tag, "Average",
        attributes=attributes, height_inches=height_in,
        archetype_name=archetype_name,
    )

    # Pick projected role (tier-gated). true_bust draws from a separate
    # risk-laden pool so a confirmed underperformer never reads as
    # "Solid Starter" / "Defensive Starter" / "All-Star Caliber".
    if outcome_tag == "true_bust":
        projected_role = random.choice(TRUE_BUST_ROLES[tier])
    else:
        projected_role = random.choice(PROJECTED_ROLES[tier])

    # Physical vitals
    wingspan_in = generate_wingspan(height_in, archetype_name)

    # Build the initial player dict
    player = {
        "name": generate_name(),
        "pick_number": player_number,
        "position": primary_pos,
        "secondary_position": secondary_pos,
        "height_inches": height_in,
        "height_display": _inches_to_feetinches(height_in),
        "weight_lbs": weight_lb,
        "wingspan_inches": wingspan_in,
        "wingspan_display": _wingspan_feet_str(wingspan_in),
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
        "playstyles": [],           # placeholder for future playstyle system
        "attributes": attributes,
        "tendencies": tendencies,
        "badges": badges,
    }

    # Assign coherent outlook labels (tier + potential + bust-gated)
    player.update(assign_player_outlook(player))

    # Cap attribute inflation for rookies
    normalize_rookie_attribute_strength(player)

    # Tighten off-identity attribute spread for non-elite class types so a
    # Slashing Forward doesn't end up elite at 8 unrelated attributes.
    enforce_attribute_specialization(player, class_type)

    # Cap badge counts to realistic rookie levels
    enforce_rookie_badge_caps(player)

    # Projection fields (depend on final attributes after normalization)
    player.update(generate_boom_avg_bust_percentages(player))
    player.update(generate_peak_age_window(player))

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

def _generate_potential(
    tier: int,
    is_bust: bool,
    outcome_tag: str = "normal",
    class_type: str = "Average",
) -> int:
    """
    Potential represents the ceiling — it's NOT current ability.

    Ranges overlap slightly between tiers to allow natural variance:
      Tier 1: 88–98  |  Tier 2: 80–90  |  Tier 3: 72–84  |  Tier 4: 55–75
    Outcome tag modifiers add further volatility so classes feel uneven.

    Class-type aware caps tighten the upper end for non-elite classes — an
    Average/Balanced class shouldn't put 98–99 potentials on Tier 2 or
    upper Tier 3 picks except as an extremely rare sleeper exception.
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
    val = clamp(base + noise)

    # Class-type aware soft caps. Generational/Strong/Top-heavy classes
    # are allowed to break these. Average/Weak/Bust-heavy/Deep role-player
    # tighten the ceiling per tier, with a small "rare exception" allowance.
    val = _apply_class_potential_caps(val, tier, outcome_tag, class_type)
    return val


# Per-tier (typical_max, rare_cap). Anything above typical_max requires a
# coin flip; anything above rare_cap is hard-clipped to rare_cap.
_AVG_CLASS_TIER_CAPS = {
    1: (94, 96),
    2: (88, 91),
    3: (82, 86),
    4: (72, 78),
}

_TIGHTENED_CLASS_TYPES = frozenset({
    "Average", "Weak", "Bust-heavy", "Deep role-player class"
})


def _apply_class_potential_caps(
    val: int, tier: int, outcome_tag: str, class_type: str
) -> int:
    """
    Tighten Average-class potential ceilings per tier.

    Stars/superstars-leaning classes (Generational, Strong, Top-heavy) are
    untouched. For tightened classes, values above the typical_max are kept
    only ~25% of the time (rare exception) and then hard-clipped to rare_cap.
    bust_risk on Tier 2 should not freely sit at 98–99 — clip to typical_max.
    """
    if class_type not in _TIGHTENED_CLASS_TYPES:
        return val

    typical_max, rare_cap = _AVG_CLASS_TIER_CAPS[tier]

    # bust_risk in tightened classes should generally not produce 95+ paper
    # prospects — clamp them to the typical band.
    if outcome_tag == "bust_risk" and tier <= 2:
        return min(val, typical_max)

    # Sleeper-style exceptions only allowed for guaranteed_good / sleeper-eligible
    # tiers. Otherwise enforce typical_max with a rare-exception coin flip.
    if val > typical_max:
        allow_exception = (
            outcome_tag == "guaranteed_good"
            or (tier in (3, 4) and random.random() < 0.25)
            or (tier in (1, 2) and random.random() < 0.20)
        )
        if not allow_exception:
            val = random.randint(max(typical_max - 4, 55), typical_max)
        else:
            val = min(val, rare_cap)

    return val


# ---------------------------------------------------------------------------
# TENDENCY GENERATION
# ---------------------------------------------------------------------------

def generate_tendencies_for_archetype(
    archetype: dict,
    tier: int,
    outcome_tag: str = "normal",
    archetype_name: str = "",
) -> dict:
    """
    Build a full tendency dict driven 80–90% by archetype identity.

    Three layers (in priority order):
      1. Explicit tendency_profile values from the archetype dict — used as-is
         with light noise (always wins).
      2. Identity-tagged tendencies (core/support/neutral/suppress/hard_off)
         from data.archetype_identity — keeps off-archetype behavior LOW so
         shooters don't post up, bigs don't pull-up three, etc.
      3. Anything that isn't tagged falls back to a low-neutral default.

    Outcome tag tweaks the variance (busts get wider noise, guaranteed_good
    players get tighter alignment) but does NOT undo the suppression of
    off-archetype tendencies — a guaranteed_good Glass Cleaner is still
    ~10 on Shot Three, never 60.
    """
    profile = archetype.get("tendency_profile", {})
    tendencies: dict = {}

    # Variance bands tighten/loosen based on outcome tag.
    if outcome_tag in ("true_bust", "bust_risk"):
        profile_noise = (-12, 12)
        identity_jitter = 6
    elif outcome_tag == "guaranteed_good":
        profile_noise = (-4, 4)
        identity_jitter = 3
    else:
        profile_noise = (-7, 7)
        identity_jitter = 4

    # A Tier 1 player tends to lean harder into identity; Tier 4 noisier.
    tier_lean = {1: 4, 2: 2, 3: 0, 4: -3}.get(tier, 0)

    for tendency in ALL_TENDENCIES:
        if tendency in profile:
            base = profile[tendency]
            val = clamp(
                base + random.randint(*profile_noise) + tier_lean // 2,
                lo=1, hi=99,
            )
        else:
            tag = get_tendency_identity(archetype_name, tendency)
            lo, hi = IDENTITY_BANDS[tag]
            base = random.randint(lo, hi)
            jit  = random.randint(-identity_jitter, identity_jitter)
            # Hard-off stays hard-off regardless of jitter spike.
            extra_lean = tier_lean if tag in ("core", "support") else -tier_lean
            val = clamp(base + jit + extra_lean // 2, lo=1, hi=99)
            # Hard ceilings to enforce identity even after jitter:
            if tag == "hard_off":
                val = min(val, 18)
            elif tag == "suppress":
                val = min(val, 32)
        tendencies[tendency] = val

    return tendencies




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
