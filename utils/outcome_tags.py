"""
Pre-generation outcome tag assignment.

assign_outcome_tags() is called BEFORE player profile generation so that
bust status, guaranteed quality, and role constraints can influence
attribute ranges and potential during generation.

Outcome tags (mutually exclusive per player slot):
  guaranteed_good    — top-tier prospect, bust suppressed, boosted potential
  normal             — standard player for their tier
  bust_risk          — elevated risk flagged in scouting; stats not penalized
  true_bust          — confirmed underperformer; maps to is_bust=True
  limited_role_player — fringe Tier 4 player; makes a roster but never stars

Sleeper tags (role/starter/star/legendary) are assigned AFTER generation
by sleeper.py and stored in a separate player['sleeper_subtype'] field.
"""

import random
from typing import List, Tuple

from data.class_rules import (
    BUST_RISK_BY_TIER,
    BUST_RISK_CLASS_MODIFIERS,
    BUST_RISK_FLAVOR_MODIFIERS,
)

# Probability a Tier 1 pick in a strong class is pre-determined "guaranteed good"
_GUARANTEED_GOOD_RATES = {
    "Generational": 0.55,
    "Strong":       0.40,
    "Top-heavy":    0.45,
}


def assign_outcome_tags(
    tier_archetype_pairs: List[Tuple[int, str]],
    class_type: str,
    class_flavor: str,
) -> List[str]:
    """
    Return one outcome tag per player slot (same order as tier_archetype_pairs).
    """
    class_mod  = BUST_RISK_CLASS_MODIFIERS.get(class_type, 0.0)
    flavor_mod = BUST_RISK_FLAVOR_MODIFIERS.get(class_flavor, 0.0)
    gg_rate    = _GUARANTEED_GOOD_RATES.get(class_type, 0.0)
    softening  = _TRUE_BUST_SOFTENING.get(class_type, 0.0)

    return [
        _assign_one(tier, class_mod, flavor_mod, gg_rate, softening)
        for tier, _arch in tier_archetype_pairs
    ]


# Probability that a Tier 3/4 true_bust outcome is downgraded to
# limited_role_player. Bust-heavy / High-variance classes preserve the heavy
# bust feel; Average / Strong / Generational soften it so the class doesn't
# read as half-failures. Tier 1/2 bust_risk is unaffected.
_TRUE_BUST_SOFTENING = {
    "Generational":           0.55,
    "Strong":                 0.45,
    "Average":                0.35,
    "Top-heavy":              0.30,
    "Deep role-player class": 0.45,
    "Weak":                   0.15,
    "Bust-heavy":             0.0,
}


def _assign_one(
    tier: int,
    class_mod: float,
    flavor_mod: float,
    gg_rate: float,
    softening: float = 0.0,
) -> str:
    # Guaranteed good applies only to Tier 1 picks
    if tier == 1 and random.random() < gg_rate:
        return "guaranteed_good"

    bust_prob = max(0.0, min(0.92, BUST_RISK_BY_TIER[tier] + class_mod + flavor_mod))

    if random.random() < bust_prob:
        # Tier 1/2 busts are high-ceiling paper prospects (not failures)
        if tier <= 2:
            return "bust_risk"
        # Tier 3/4 → true_bust by default, but soften some into limited role
        # players for non-bust-heavy classes so the class doesn't feel
        # uniformly broken. Tier 4 softens to limited_role_player; Tier 3
        # softens to "normal" (fringe rotation contributor).
        if softening > 0.0 and random.random() < softening:
            return "limited_role_player" if tier == 4 else "normal"
        return "true_bust"

    # Non-bust Tier 4 → limited role player (makes a roster, just not a star)
    if tier == 4:
        return "limited_role_player"

    return "normal"
