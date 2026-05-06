"""
Draft class generation orchestrator.

generate_draft_class() ties together:
- Tier distribution (scaling.py)
- Archetype selection (select_archetypes_for_class)
- Player generation (generate_player.py)

Returns a list of player dicts ordered by pick (best → worst).
"""

import random
from typing import Optional

from data.archetypes import ARCHETYPES
from data.class_rules import CLASS_FLAVORS
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
        class_type:   e.g. "Generational", "Strong", "Weak"
        player_count: 1–60
        class_flavor: e.g. "Guard-heavy", "High variance"
        seed:         Optional random seed for reproducibility

    Returns:
        List of player dicts, ordered by pick (best → worst).
    """
    if seed is not None:
        random.seed(seed)

    player_count = max(1, min(60, player_count))

    tier_counts = scale_tier_distribution(class_type, player_count)

    archetype_weights = _build_archetype_weights(class_flavor)

    flavor_rules = CLASS_FLAVORS.get(class_flavor, {})
    bust_modifier = flavor_rules.get("extra_bust_weight", 0.0)

    # Select all archetype assignments up front so High Variance can see the
    # full picture and ensure spread across picks.
    archetype_sequence = select_archetypes_for_class(
        player_count, class_flavor, archetype_weights
    )

    # Build build-name lookup (optional; only loaded when mapper + file exist)
    build_name_pool = _load_build_name_pool()

    assignments = _build_assignments(tier_counts, archetype_sequence)

    players = []
    for pick_num, (tier, archetype_name) in enumerate(assignments, start=1):
        build_name = _pick_build_name(archetype_name, build_name_pool, class_flavor)
        player = generate_player(
            tier=tier,
            archetype_name=archetype_name,
            bust_modifier=bust_modifier,
            player_number=pick_num,
            build_name=build_name,
        )
        players.append(player)

    return players


# ---------------------------------------------------------------------------
# ARCHETYPE SELECTION
# ---------------------------------------------------------------------------

def select_archetypes_for_class(
    player_count: int,
    class_flavor: str,
    archetype_weights: dict,
) -> list:
    """
    Return a list of archetype names, one per player.

    High Variance:
        Unique-first round-robin.  Shuffle all available archetypes, deal
        them one at a time.  Only begin a new round (and potentially repeat)
        after every archetype has been used at least once.  Back-to-back
        duplicates between rounds are avoided.

    Low Variance:
        Weighted selection with a bias toward a smaller subset — fewer unique
        archetypes, higher repetition is expected and acceptable.

    Balanced / all other flavors:
        Standard per-pick weighted random selection (original behavior).
    """
    archetypes = list(archetype_weights.keys())
    weights    = [archetype_weights[a] for a in archetypes]

    if class_flavor == "High variance":
        return _select_high_variance(player_count, archetypes)
    elif class_flavor == "Low variance":
        return _select_low_variance(player_count, archetypes, weights)
    else:
        return [random.choices(archetypes, weights=weights, k=1)[0]
                for _ in range(player_count)]


def _select_high_variance(player_count: int, archetypes: list) -> list:
    """
    Unique-first deck-based selection.

    Each "round" is a freshly shuffled copy of all available archetypes.
    Back-to-back duplicates at round boundaries are resolved by swapping
    the first card of the new deck with a random non-first position.
    """
    result = []
    deck: list = []

    for _ in range(player_count):
        # Refill deck when empty
        if not deck:
            new_deck = archetypes[:]
            random.shuffle(new_deck)

            # Prevent back-to-back duplicate at the round boundary
            if result and new_deck[0] == result[-1] and len(new_deck) > 1:
                swap_idx = random.randint(1, len(new_deck) - 1)
                new_deck[0], new_deck[swap_idx] = new_deck[swap_idx], new_deck[0]

            deck = new_deck

        result.append(deck.pop(0))

    return result


def _select_low_variance(
    player_count: int, archetypes: list, weights: list
) -> list:
    """
    Weighted selection biased toward a smaller subset.

    We pick a "core" of roughly half the archetypes (weighted) and then
    sample heavily from that core, giving the class a tighter identity.
    """
    # Pick a core set (~40–60% of archetypes) with weighted probability
    core_size = max(3, len(archetypes) // 2 + random.randint(-2, 2))
    core_size = min(core_size, len(archetypes))

    # Build a weighted population and sample core without replacement
    core = random.choices(archetypes, weights=weights, k=core_size * 3)
    # Deduplicate while preserving weighted bias in frequency
    seen: set = set()
    core_set = []
    for a in core:
        if a not in seen:
            core_set.append(a)
            seen.add(a)
        if len(core_set) >= core_size:
            break

    # Weight the core archetypes more heavily (3× vs rest)
    boosted_weights = []
    for arch, w in zip(archetypes, weights):
        boosted_weights.append(w * 3.0 if arch in core_set else w)

    return [random.choices(archetypes, weights=boosted_weights, k=1)[0]
            for _ in range(player_count)]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _build_archetype_weights(class_flavor: str) -> dict:
    """Build {archetype_name: weight} applying flavor multipliers."""
    flavor_rules  = CLASS_FLAVORS.get(class_flavor, {})
    flavor_weights = flavor_rules.get("archetype_weights", {})
    return {arch: flavor_weights.get(arch, 1.0) for arch in ARCHETYPES}


def _build_assignments(tier_counts: dict, archetype_sequence: list) -> list:
    """
    Pair each archetype from the pre-selected sequence with a tier drawn
    from tier_counts, then sort Tier 1 → 4 (best picks first).
    """
    # Build a flat list of tiers matching tier_counts
    tiers_flat = []
    for tier in sorted(tier_counts.keys()):
        tiers_flat.extend([tier] * tier_counts[tier])

    # Zip tiers with the archetype sequence
    pairs = list(zip(tiers_flat, archetype_sequence))

    # Re-sort by tier so the class reads Tier 1 → 4, but shuffle within tier
    tier_groups: dict = {t: [] for t in range(1, 5)}
    for tier, arch in pairs:
        tier_groups[tier].append((tier, arch))

    result = []
    for tier in [1, 2, 3, 4]:
        group = tier_groups[tier]
        random.shuffle(group)
        result.extend(group)

    return result


def _load_build_name_pool() -> dict:
    """
    Optionally load a dict of {archetype_name: [build_name, ...]} from
    the Excel mapper.  Returns an empty dict if the file isn't present.
    """
    try:
        from utils.build_mapper import find_excel_path, load_build_names, map_build_name
        path = find_excel_path()
        if not path:
            return {}
        build_names = load_build_names(path)
        pool: dict = {}
        for name in build_names:
            for arch in map_build_name(name):
                pool.setdefault(arch, []).append(name)
        return pool
    except Exception:
        return {}


def _pick_build_name(
    archetype_name: str,
    build_name_pool: dict,
    class_flavor: str,
) -> str:
    """
    For High Variance, pick a random build-name alias from the pool.
    For other flavors, return an empty string (archetype name is used instead).
    """
    if class_flavor != "High variance":
        return ""
    candidates = build_name_pool.get(archetype_name, [])
    return random.choice(candidates) if candidates else ""


# ---------------------------------------------------------------------------
# CLASS SUMMARY
# ---------------------------------------------------------------------------

def get_class_summary(players: list) -> dict:
    """
    Compute summary statistics for a generated draft class.
    Includes archetype diversity metrics for display in the Class Review tab.
    """
    from collections import Counter

    tier_counts      = Counter(p["tier"] for p in players)
    archetype_counts = Counter(p["archetype"] for p in players)
    position_counts  = Counter(p["position"] for p in players)
    bust_count       = sum(1 for p in players if p["is_bust"])

    total = len(players)
    unique_archetypes  = len(archetype_counts)
    most_repeated_arch = archetype_counts.most_common(1)[0] if archetype_counts else ("—", 0)
    # Diversity score: ratio of unique archetypes to total players (0–1, capped at 1)
    diversity_score = round(min(1.0, unique_archetypes / total), 3) if total else 0.0

    return {
        "total_players":         total,
        "tier_breakdown":        dict(tier_counts),
        "archetype_distribution": dict(archetype_counts),
        "position_distribution": dict(position_counts),
        "bust_count":            bust_count,
        "bust_percentage":       round(bust_count / total * 100, 1) if total else 0,
        "avg_potential": (
            round(sum(p["attributes"]["Potential"] for p in players) / total, 1)
            if total else 0
        ),
        # Diversity metrics
        "unique_archetypes":     unique_archetypes,
        "most_repeated_archetype": most_repeated_arch[0],
        "most_repeated_count":   most_repeated_arch[1],
        "diversity_score":       diversity_score,
        # Used by dashboard / export
        "top_picks": [p for p in players if p["tier"] <= 2],
    }
