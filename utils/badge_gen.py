"""
Attribute-driven, archetype-aware, budgeted badge generation.

Rookies are hard-capped at Gold. Hall of Fame and Legend never appear.

Pipeline:
  1. Pull primary / secondary / rare candidate badges from the archetype pool.
  2. Filter out anything in the archetype's avoid list.
  3. For each candidate, compute the max eligible level from attributes + height.
  4. Sample up to a tier-bound gameplay budget, weighted toward primary > secondary > rare.
  5. Apply Gold scarcity per tier.
  6. Sample a separate personality badge budget.
  7. Final validation pass: cap any remaining selections to attribute-eligible level.

Public API:
  - generate_badges_for_archetype(archetype, tier, outcome_tag, attributes, height_inches)
  - enforce_rookie_badge_caps(player)
"""

import random
from typing import Dict, List, Optional, Set, Tuple

from data.fields import ALL_BADGES, PERSONALITY_BADGES
from data.badge_requirements import (
    BADGE_REQUIREMENTS, max_eligible_level, level_at_or_below, _LEVEL_RANK,
)
from data.archetype_badge_pools import get_pool

# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------

# Gameplay badge counts (excluding Personality)
_GAMEPLAY_BUDGET: Dict[int, Tuple[int, int]] = {
    1: (8, 12),
    2: (5, 9),
    3: (2, 5),
    4: (0, 3),
}
# Rare extension for Tier 1 generational/elite specialists
_GAMEPLAY_BUDGET_TIER1_STRETCH: Tuple[int, int] = (13, 14)

# Personality budget per tier
_PERSONALITY_BUDGET: Dict[int, Tuple[int, int]] = {
    1: (2, 4),
    2: (1, 3),
    3: (0, 2),
    4: (0, 1),
}

# Gold scarcity caps per tier (max Gold gameplay badges)
_GOLD_CAPS: Dict[int, int] = {
    1: 3,
    2: 2,
    3: 1,
    4: 0,
}
# Tier 1 generational/elite specialist may stretch to 4 Golds
_GOLD_CAP_TIER1_STRETCH: int = 4

# Pool weights (probability of drawing from each tier of pool)
_POOL_WEIGHTS = {
    "primary":   60,
    "secondary": 30,
    "rare":      10,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_badges_for_archetype(
    archetype: dict,
    tier: int,
    outcome_tag: str = "normal",
    class_type: str = "Average",
    attributes: Optional[dict] = None,
    height_inches: int = 78,
    archetype_name: str = "",
) -> dict:
    """
    Generate a full badge dict for one player. Every gameplay and personality
    badge in ALL_BADGES is keyed; non-selected badges are 'None'.
    """
    if not archetype_name:
        archetype_name = archetype.get("name") or _resolve_archetype_name(archetype)
    pool = get_pool(archetype_name)
    avoid: Set[str] = set(pool.get("avoid", []))

    if attributes is None:
        attributes = {}

    # Initialise every badge to None — preserves wide-format export schema.
    badges: Dict[str, str] = {}
    for _cat, badge_list in ALL_BADGES.items():
        for badge in badge_list:
            badges[badge] = "None"

    # ---- Gameplay budget ----------------------------------------------------
    gameplay_budget = _resolve_gameplay_budget(tier, outcome_tag)
    gold_cap = _resolve_gold_cap(tier, outcome_tag)

    candidate_levels = _build_candidate_levels(pool, avoid, attributes, height_inches)

    selected = _sample_gameplay_badges(
        candidate_levels=candidate_levels,
        pool=pool,
        budget=gameplay_budget,
        gold_cap=gold_cap,
        outcome_tag=outcome_tag,
    )
    for badge, level in selected.items():
        badges[badge] = level

    # ---- Personality budget -------------------------------------------------
    p_lo, p_hi = _PERSONALITY_BUDGET.get(tier, (0, 1))
    p_count = random.randint(p_lo, p_hi)
    if p_count > 0:
        personality_picks = random.sample(
            PERSONALITY_BADGES,
            k=min(p_count, len(PERSONALITY_BADGES)),
        )
        for badge in personality_picks:
            # Personality badges aren't attribute-gated; weighted level
            badges[badge] = _personality_level(tier, outcome_tag)

    return badges


def enforce_rookie_badge_caps(player: dict, class_type: str = "Average") -> None:
    """
    Final validation/pruning. Idempotent — safe to call after manual edits.

    1. Strip any HOF/Legend levels (rookies cap at Gold).
    2. Cap each selected badge to its attribute-eligible level. Bronze-only
       eligible badges already in selection stay at Bronze; ineligible badges
       are removed (set to None).
    3. Enforce gameplay-count budget. Trim by reverse priority if over.
    4. Enforce personality-count budget. Trim if over.
    5. Enforce Gold cap. Demote excess Golds to Silver (non-priority first).
    6. Strip any badge in the archetype avoid list, regardless of level.
    """
    badges: Dict[str, str] = player["badges"]
    tier: int = player["tier"]
    outcome_tag: str = player.get("outcome_tag", "normal")
    archetype_name: str = player.get("archetype", "")
    attributes: dict = player.get("attributes", {}) or {}
    height_inches: int = player.get("height_inches", 78)

    pool = get_pool(archetype_name)
    avoid: Set[str] = set(pool.get("avoid", []))
    primary: Set[str] = set(pool.get("primary", []))
    secondary: Set[str] = set(pool.get("secondary", []))
    rare: Set[str] = set(pool.get("rare", []))

    # 1. Strip HOF/Legend
    for b, lv in list(badges.items()):
        if lv in ("Hall of Fame", "Legend"):
            badges[b] = "None"

    # 2. Attribute eligibility cap (gameplay only)
    for b in list(badges):
        if b in PERSONALITY_BADGES:
            continue
        lv = badges[b]
        if lv == "None":
            continue
        if b not in BADGE_REQUIREMENTS:
            # Unknown gameplay badge — cap at Bronze
            if _LEVEL_RANK.get(lv, 0) > _LEVEL_RANK["Bronze"]:
                badges[b] = "Bronze"
            continue
        max_lv = max_eligible_level(b, attributes, height_inches)
        if max_lv == "None":
            badges[b] = "None"
        else:
            badges[b] = level_at_or_below(lv, max_lv)

    # 6. Strip avoid-list badges (do this before count caps so they don't take slots)
    for b in list(badges):
        if b in avoid and b not in PERSONALITY_BADGES:
            badges[b] = "None"

    # 3. Gameplay count cap
    gp_lo, gp_hi = _resolve_gameplay_budget(tier, outcome_tag)
    gameplay_selected = [b for b, lv in badges.items()
                          if lv != "None" and b not in PERSONALITY_BADGES]
    if len(gameplay_selected) > gp_hi:
        excess = len(gameplay_selected) - gp_hi
        # Trim lowest-priority first, then lowest-level
        def trim_key(badge: str) -> tuple:
            if badge in primary:    pri = 3
            elif badge in secondary: pri = 2
            elif badge in rare:      pri = 1
            else:                    pri = 0
            return (pri, _LEVEL_RANK.get(badges[badge], 0))
        for b in sorted(gameplay_selected, key=trim_key)[:excess]:
            badges[b] = "None"

    # 4. Personality count cap
    p_lo, p_hi = _PERSONALITY_BUDGET.get(tier, (0, 1))
    personality_selected = [b for b in PERSONALITY_BADGES if badges.get(b, "None") != "None"]
    if len(personality_selected) > p_hi:
        excess = len(personality_selected) - p_hi
        # Trim lowest level first
        for b in sorted(personality_selected, key=lambda x: _LEVEL_RANK.get(badges[x], 0))[:excess]:
            badges[b] = "None"

    # 5. Gold cap
    gold_cap = _resolve_gold_cap(tier, outcome_tag)
    gold_list = [b for b, lv in badges.items()
                  if lv == "Gold" and b not in PERSONALITY_BADGES]
    if len(gold_list) > gold_cap:
        excess = len(gold_list) - gold_cap
        non_pri = [b for b in gold_list if b not in primary]
        pri     = [b for b in gold_list if b in primary]
        for b in (non_pri + pri)[:excess]:
            badges[b] = "Silver"


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _build_candidate_levels(
    pool: Dict[str, List[str]],
    avoid: Set[str],
    attributes: dict,
    height_inches: int,
) -> Dict[str, str]:
    """
    For each badge listed in primary/secondary/rare (minus avoid), compute the
    maximum eligible level. Drop badges whose eligibility is None.
    """
    candidates: Dict[str, str] = {}
    for tier_key in ("primary", "secondary", "rare"):
        for badge in pool.get(tier_key, []):
            if badge in avoid or badge in candidates:
                continue
            if badge not in BADGE_REQUIREMENTS:
                # Pool referenced a badge we don't have requirements for; cap Bronze.
                candidates[badge] = "Bronze"
                continue
            lv = max_eligible_level(badge, attributes, height_inches)
            if lv != "None":
                candidates[badge] = lv
    return candidates


def _sample_gameplay_badges(
    candidate_levels: Dict[str, str],
    pool: Dict[str, List[str]],
    budget: Tuple[int, int],
    gold_cap: int,
    outcome_tag: str,
) -> Dict[str, str]:
    """Pick badges up to a target count using pool-tier-weighted sampling."""
    primary = [b for b in pool.get("primary", [])   if b in candidate_levels]
    secondary = [b for b in pool.get("secondary", []) if b in candidate_levels]
    rare = [b for b in pool.get("rare", [])      if b in candidate_levels]

    pool_lists = {"primary": primary, "secondary": secondary, "rare": rare}

    lo, hi = budget
    target = random.randint(lo, hi)
    target = min(target, len(primary) + len(secondary) + len(rare))
    if target <= 0:
        return {}

    # Outcome tag tilt: bust-ish drops max picks; guaranteed_good can lean to high end
    if outcome_tag in ("true_bust", "bust_risk"):
        target = max(lo, target - random.randint(1, 3))
    elif outcome_tag == "guaranteed_good":
        target = min(hi, target + random.randint(0, 1))

    chosen: Dict[str, str] = {}
    available = {k: list(v) for k, v in pool_lists.items()}

    while len(chosen) < target:
        # Weighted pick from non-empty pool tiers
        keys = [k for k in ("primary", "secondary", "rare") if available[k]]
        if not keys:
            break
        weights = [_POOL_WEIGHTS[k] for k in keys]
        bucket = random.choices(keys, weights=weights, k=1)[0]
        badge = random.choice(available[bucket])
        available[bucket].remove(badge)
        chosen[badge] = candidate_levels[badge]

    # Apply Gold scarcity: demote excess Golds to Silver, biased toward non-primary
    gold_list = [b for b, lv in chosen.items() if lv == "Gold"]
    if len(gold_list) > gold_cap:
        excess = len(gold_list) - gold_cap
        non_pri = [b for b in gold_list if b not in primary]
        pri = [b for b in gold_list if b in primary]
        for b in (non_pri + pri)[:excess]:
            chosen[b] = "Silver"

    # Add a tiny chance to pull each Bronze a tiny bit lower for tier-3/4 feel
    return chosen


def _resolve_gameplay_budget(tier: int, outcome_tag: str) -> Tuple[int, int]:
    base = _GAMEPLAY_BUDGET.get(tier, (0, 2))
    if tier == 1 and outcome_tag == "guaranteed_good" and random.random() < 0.10:
        return _GAMEPLAY_BUDGET_TIER1_STRETCH
    return base


def _resolve_gold_cap(tier: int, outcome_tag: str) -> int:
    base = _GOLD_CAPS.get(tier, 0)
    if tier == 1 and outcome_tag == "guaranteed_good" and random.random() < 0.10:
        return _GOLD_CAP_TIER1_STRETCH
    return base


def _personality_level(tier: int, outcome_tag: str) -> str:
    """Sample a level for a personality badge — capped at Gold."""
    weights = {
        1: {"Bronze": 25, "Silver": 45, "Gold": 30},
        2: {"Bronze": 40, "Silver": 40, "Gold": 20},
        3: {"Bronze": 55, "Silver": 35, "Gold": 10},
        4: {"Bronze": 70, "Silver": 25, "Gold": 5},
    }
    w = dict(weights.get(tier, weights[4]))
    if outcome_tag in ("true_bust", "bust_risk"):
        w["Gold"]   = max(0, int(w["Gold"]   * 0.5))
        w["Silver"] = max(0, int(w["Silver"] * 0.7))
        w["Bronze"] = w["Bronze"] + 10
    levels = list(w.keys())
    weights = [w[lv] for lv in levels]
    return random.choices(levels, weights=weights, k=1)[0]


def _resolve_archetype_name(archetype: dict) -> str:
    """Reverse-lookup an archetype's name from the global ARCHETYPES dict."""
    from data.archetypes import ARCHETYPES
    for name, defn in ARCHETYPES.items():
        if defn is archetype:
            return name
    return ""
