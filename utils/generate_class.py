"""
Draft class generation orchestrator.

Pipeline stages:
  1. scale_tier_distribution()       → tier counts WITH hard caps
  2. select_archetypes_for_class()   → archetype sequence WITH spacing
  3. _build_assignments()            → sorted (tier, arch) pairs
  4. enforce_top_pick_diversity()    → positional variety in top 5
  5. assign_outcome_tags()           → pre-determine bust/quality outcomes
  6. generate_player() × N          → full player profiles
  7. enforce_height_distribution()   → cap extreme heights
  8. sleeper_pass()                  → count-based sleeper assignment
  9. validate_class()                → collect realism warnings

Returns (players, warnings) — a list of player dicts and a list of strings.
"""

import random
from typing import List, Optional, Tuple

from data.archetypes import ARCHETYPES
from data.class_rules import CLASS_FLAVORS
from utils.scaling import scale_tier_distribution
from utils.generate_player import generate_player
from utils.sleeper import sleeper_pass
from utils.outcome_tags import assign_outcome_tags
from utils.realism import (
    enforce_top_pick_diversity,
    enforce_height_distribution,
    enforce_archetype_spacing,
    coerce_off_identity_outliers,
    validate_class,
)


def generate_draft_class(
    class_type: str,
    player_count: int,
    class_flavor: str = "Balanced",
    seed: Optional[int] = None,
) -> Tuple[list, List[str]]:
    """
    Generate a complete draft class.

    Args:
        class_type:   e.g. "Generational", "Strong", "Weak"
        player_count: 1–60
        class_flavor: e.g. "Guard-heavy", "High variance"
        seed:         Optional random seed for reproducibility

    Returns:
        (players, warnings) — ordered list of player dicts + realism warnings.
    """
    if seed is not None:
        random.seed(seed)

    player_count = max(1, min(60, player_count))

    # Stage 1: Tier distribution (caps enforced inside scale_tier_distribution)
    tier_counts = scale_tier_distribution(class_type, player_count)

    archetype_weights = _build_archetype_weights(class_flavor)

    # Stage 2: Archetype selection
    archetype_sequence = select_archetypes_for_class(
        player_count, class_flavor, archetype_weights
    )

    # Stage 3: Build sorted (tier, arch) assignment list
    assignments = _build_assignments(tier_counts, archetype_sequence)

    # Stage 4: Top-pick positional diversity (pre-generation reorder)
    assignments = enforce_top_pick_diversity(assignments, class_flavor)

    # Stage 5: Pre-assign outcome tags (bust, guaranteed_good, etc.)
    outcome_tags = assign_outcome_tags(assignments, class_type, class_flavor)

    # Build build-name lookup (optional)
    build_name_pool = _load_build_name_pool()

    # Stage 6: Generate player profiles
    players = []
    for pick_num, ((tier, archetype_name), outcome_tag) in enumerate(
        zip(assignments, outcome_tags), start=1
    ):
        build_name = _pick_build_name(archetype_name, build_name_pool, class_flavor)
        player = generate_player(
            tier=tier,
            archetype_name=archetype_name,
            player_number=pick_num,
            build_name=build_name,
            outcome_tag=outcome_tag,
            class_type=class_type,
        )
        players.append(player)

    # Stage 7: Height distribution enforcement
    enforce_height_distribution(players, player_count, class_flavor)

    # Stage 8: Sleeper assignment (count-based + legendary probabilistic)
    sleeper_pass(players, class_type, class_flavor, player_count)

    # Post-sleeper: enforce archetype spacing in top 15
    enforce_archetype_spacing(players)

    # Stage 8.5: Soft cleanup of off-identity tendency/badge outliers
    coerce_off_identity_outliers(players)

    # Final sort by pick number so display/export are always in pick order.
    # Spacing/diversity passes above may reorder same-tier players but pick
    # numbers stay attached, so sort by pick_number rather than re-numbering.
    players.sort(key=lambda p: p.get("pick_number", 0))

    # Stage 9: Validate class for realism warnings
    warnings = validate_class(players, class_type, player_count, class_flavor)

    return players, warnings


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

def get_class_summary(players: list, warnings: Optional[List[str]] = None) -> dict:
    """
    Compute summary statistics for a generated draft class.
    Includes archetype diversity metrics and sleeper breakdown.
    """
    from collections import Counter

    tier_counts      = Counter(p["tier"] for p in players)
    archetype_counts = Counter(p["archetype"] for p in players)
    position_counts  = Counter(p["position"] for p in players)
    bust_count       = sum(1 for p in players if p["is_bust"])

    total = len(players)
    unique_archetypes  = len(archetype_counts)
    most_repeated_arch = archetype_counts.most_common(1)[0] if archetype_counts else ("—", 0)
    diversity_score = round(min(1.0, unique_archetypes / total), 3) if total else 0.0

    # Sleeper breakdown
    sleeper_subtypes = [
        "role_sleeper", "starter_sleeper", "star_sleeper", "legendary_sleeper"
    ]
    sleeper_counts = {
        st: sum(1 for p in players if p.get("sleeper_subtype") == st)
        for st in sleeper_subtypes
    }
    legendary_sleepers = [p for p in players if p.get("sleeper_subtype") == "legendary_sleeper"]

    return {
        "total_players":           total,
        "tier_breakdown":          dict(tier_counts),
        "archetype_distribution":  dict(archetype_counts),
        "position_distribution":   dict(position_counts),
        "bust_count":              bust_count,
        "bust_percentage":         round(bust_count / total * 100, 1) if total else 0,
        "avg_potential": (
            round(sum(p["attributes"]["Potential"] for p in players) / total, 1)
            if total else 0
        ),
        # Diversity metrics
        "unique_archetypes":       unique_archetypes,
        "most_repeated_archetype": most_repeated_arch[0],
        "most_repeated_count":     most_repeated_arch[1],
        "diversity_score":         diversity_score,
        # Sleeper metrics
        "sleeper_counts":          sleeper_counts,
        "legendary_sleepers":      legendary_sleepers,
        # Outcome tag breakdown
        "outcome_tag_counts": {
            tag: sum(1 for p in players if p.get("outcome_tag") == tag)
            for tag in ("guaranteed_good", "normal", "bust_risk",
                        "true_bust", "limited_role_player")
        },
        # Realism warnings (pass-through from generation)
        "validation_warnings":     warnings or [],
        # Used by dashboard / export
        "top_picks": [p for p in players if p["tier"] <= 2],
    }
