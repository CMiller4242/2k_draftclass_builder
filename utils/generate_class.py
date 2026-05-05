"""
Draft class generation orchestrator.

generate_draft_class() ties together:
- Tier distribution (scaling.py)
- Archetype selection (weighted by flavor)
- Player generation (generate_player.py)

Returns a list of player dicts sorted by tier (best players first).
"""

import random
from typing import Optional

from data.archetypes import ARCHETYPES, POSITION_ARCHETYPE_MAP
from data.class_rules import CLASS_FLAVORS, BUST_RISK_BY_TIER
from utils.scaling import scale_tier_distribution
from utils.generate_player import generate_player


def generate_draft_class(
    class_type: str,
    player_count: int,
    class_flavor: str = "Balanced",
    seed: Optional[int] = None,
) -> list:
    """
    Generate a complete draft class.

    Args:
        class_type: e.g. "Generational", "Strong", "Weak"
        player_count: 1–60
        class_flavor: e.g. "Guard-heavy", "Balanced"
        seed: Optional random seed for reproducibility

    Returns:
        List of player dicts, ordered by pick (best → worst).
    """
    if seed is not None:
        random.seed(seed)

    player_count = max(1, min(60, player_count))

    # Get tier distribution
    tier_counts = scale_tier_distribution(class_type, player_count)

    # Build archetype weight map from flavor
    archetype_weights = _build_archetype_weights(class_flavor)

    # Bust modifier from flavor
    flavor_rules = CLASS_FLAVORS.get(class_flavor, {})
    bust_modifier = flavor_rules.get("extra_bust_weight", 0.0)

    # Build flat list of (tier, archetype) assignments
    assignments = _build_assignments(tier_counts, archetype_weights)

    # Generate each player
    players = []
    for pick_num, (tier, archetype_name) in enumerate(assignments, start=1):
        player = generate_player(
            tier=tier,
            archetype_name=archetype_name,
            bust_modifier=bust_modifier,
            player_number=pick_num,
        )
        players.append(player)

    return players


def _build_archetype_weights(class_flavor: str) -> dict:
    """
    Build a dict of {archetype_name: weight} for archetype selection.
    Applies flavor multipliers on top of default equal weights.
    """
    flavor_rules = CLASS_FLAVORS.get(class_flavor, {})
    flavor_weights = flavor_rules.get("archetype_weights", {})

    base_weight = 1.0
    weights = {}
    for arch in ARCHETYPES:
        weights[arch] = flavor_weights.get(arch, base_weight)

    return weights


def _build_assignments(tier_counts: dict, archetype_weights: dict) -> list:
    """
    Build an ordered list of (tier, archetype) tuples.
    Players are ordered Tier 1 → 4, simulating a real draft order.

    Within each tier, picks are randomized for variety.
    """
    assignments = []
    for tier in sorted(tier_counts.keys()):
        count = tier_counts[tier]
        for _ in range(count):
            archetype = _pick_archetype_for_tier(tier, archetype_weights)
            assignments.append((tier, archetype))

    # Shuffle within each tier group to randomize player order slightly,
    # but keep the overall tier ordering intact
    result = []
    tier_groups = {t: [] for t in range(1, 5)}
    for tier, arch in assignments:
        tier_groups[tier].append((tier, arch))

    for tier in [1, 2, 3, 4]:
        group = tier_groups[tier]
        random.shuffle(group)
        result.extend(group)

    return result


def _pick_archetype_for_tier(tier: int, archetype_weights: dict) -> str:
    """
    Pick an archetype appropriate for a given tier.
    All archetypes are valid for all tiers — tier affects stats, not type.
    """
    archetypes = list(archetype_weights.keys())
    weights = [archetype_weights[a] for a in archetypes]
    return random.choices(archetypes, weights=weights, k=1)[0]


def get_class_summary(players: list) -> dict:
    """
    Compute summary statistics for a generated draft class.
    Used in the Generated Class Review tab.
    """
    from collections import Counter

    tier_counts = Counter(p["tier"] for p in players)
    archetype_counts = Counter(p["archetype"] for p in players)
    position_counts = Counter(p["position"] for p in players)
    bust_count = sum(1 for p in players if p["is_bust"])

    return {
        "total_players": len(players),
        "tier_breakdown": dict(tier_counts),
        "archetype_distribution": dict(archetype_counts),
        "position_distribution": dict(position_counts),
        "bust_count": bust_count,
        "bust_percentage": round(bust_count / len(players) * 100, 1) if players else 0,
        "avg_potential": (
            round(sum(p["attributes"]["Potential"] for p in players) / len(players), 1)
            if players else 0
        ),
        "top_picks": [p for p in players if p["tier"] <= 2],
    }
