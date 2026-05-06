"""
Player outlook assignment — tier-locked, potential-gated label selection.

Replaces the flat DEVELOPMENT_OUTLOOKS random.choice() call with labels that
are coherent with tier, potential, and bust status.
"""

import random

# ---------------------------------------------------------------------------
# LABEL POOLS
# ---------------------------------------------------------------------------

# Bust players always get one of these — never star/cornerstone language
_BUST_OUTLOOKS = [
    "Boom-or-Bust Prospect",
    "High Variance Prospect",
    "Toolsy but Unrefined",
    "Ceiling Chaser",
    "Paper Prospect",
    "Developmental Risk",
    "Unfulfilled Potential",
]

# Non-bust outlooks keyed by (tier, potential_band)
# Potential bands:  elite ≥90 | star 85–89 | high 75–84 | mid 65–74 | low <65
_OUTLOOKS: dict = {
    # --- Tier 1 (Superstar) — potential ranges 88-99 by design ---
    (1, "elite"): ["Franchise Cornerstone", "Perennial All-Star", "Immediate Contributor"],
    (1, "star"):  ["Future All-Star", "Immediate Contributor", "Slow Burn"],
    (1, "high"):  ["Slow Burn", "Late Bloomer", "Peak and Decline"],

    # --- Tier 2 (All-Star / High-End Starter) — potential ranges 80-92 ---
    (2, "elite"): ["Immediate Contributor", "All-Star Caliber", "Peak and Decline"],
    (2, "star"):  ["All-Star Caliber", "Immediate Contributor", "Slow Burn"],
    (2, "high"):  ["Slow Burn", "Late Bloomer", "High-End Starter Upside"],
    (2, "mid"):   ["High-End Role Player", "Slow Burn", "Peak and Decline"],

    # --- Tier 3 (Starter / Rotation) — potential ranges 70-82 ---
    (3, "star"):  ["Late Bloomer", "Starter Upside", "Slow Burn"],
    (3, "high"):  ["Starter Upside", "Slow Burn", "Late Bloomer"],
    (3, "mid"):   ["Culture Player", "Quality Rotation Player", "Slow Burn"],
    (3, "low"):   ["Career Backup", "Culture Player", "Journeyman"],

    # --- Tier 4 (Role Player / Bust) — potential ranges 55-73 ---
    (4, "high"):  ["Developmental Project", "Late Bloomer", "Fringe Roster Piece"],
    (4, "mid"):   ["Career Backup", "Journeyman", "Culture Player"],
    (4, "low"):   ["Career Backup", "Journeyman", "Fringe Roster Piece"],
}

# Bust risk labels by tier (for non-bust players only)
_BUST_RISK_LABELS = {
    1: "Low",
    2: "Moderate",
    3: "Moderate-High",
    4: "High",
}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def assign_player_outlook(player: dict) -> dict:
    """
    Return updated player fields consistent with tier, potential, and bust status.

    Fields returned: development_outlook, bust_risk
    (projected_role is already tier-gated at call site and is not changed)
    """
    tier      = player["tier"]
    potential = player["attributes"].get("Potential", 70)
    is_bust   = player["is_bust"]

    bust_risk = (
        "High — Underperforming Prospect"
        if is_bust
        else _BUST_RISK_LABELS.get(tier, "Unknown")
    )

    if is_bust:
        development_outlook = random.choice(_BUST_OUTLOOKS)
    else:
        band = _potential_band(potential)
        pool = _resolve_pool(tier, band)
        development_outlook = random.choice(pool)

    return {
        "development_outlook": development_outlook,
        "bust_risk":           bust_risk,
    }


def validate_player_profile(player: dict) -> list:
    """
    Return a list of human-readable warning strings for contradictory profile fields.
    An empty list means no contradictions were found.
    """
    warnings = []
    tier      = player["tier"]
    potential = player["attributes"].get("Potential", 70)
    is_bust   = player["is_bust"]
    outlook   = player.get("development_outlook", "")
    role      = player.get("projected_role", "")
    bust_risk = player.get("bust_risk", "")

    # Star/cornerstone language on low-tier or low-potential players
    star_terms = {"Franchise Cornerstone", "Perennial All-Star", "All-Star Caliber", "Future All-Star"}
    if outlook in star_terms and tier >= 3:
        warnings.append(
            f"Tier {tier} player has star-level outlook '{outlook}' — "
            "expected only on Tier 1–2 players."
        )
    if outlook in star_terms and potential < 75:
        warnings.append(
            f"Potential {potential} player has star-level outlook '{outlook}' — "
            "expected potential ≥ 75."
        )

    # Bust player carrying star/cornerstone language
    if is_bust and outlook in star_terms:
        warnings.append(
            f"Bust player has star-level outlook '{outlook}' — "
            "bust players should carry high-variance labels."
        )

    # Bust risk label contradicts is_bust flag
    if is_bust and bust_risk != "High — Underperforming Prospect":
        warnings.append(
            f"Player is_bust=True but bust_risk is '{bust_risk}' — "
            "should be 'High — Underperforming Prospect'."
        )
    if not is_bust and bust_risk == "High — Underperforming Prospect":
        warnings.append(
            "Player is_bust=False but bust_risk is 'High — Underperforming Prospect'."
        )

    return warnings


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _potential_band(potential: int) -> str:
    if potential >= 90:
        return "elite"
    if potential >= 85:
        return "star"
    if potential >= 75:
        return "high"
    if potential >= 65:
        return "mid"
    return "low"


def _resolve_pool(tier: int, band: str) -> list:
    """Find the label pool for (tier, band), falling back to lower bands if needed."""
    band_order = ["elite", "star", "high", "mid", "low"]
    start = band_order.index(band) if band in band_order else len(band_order) - 1
    for b in band_order[start:]:
        pool = _OUTLOOKS.get((tier, b))
        if pool:
            return pool
    # Ultimate fallback
    return ["Journeyman"]
