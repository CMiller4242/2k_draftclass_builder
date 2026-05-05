"""
Badge assignment logic per tier and archetype.
Defines how many badges of each level a player gets based on their tier.
"""

from data.fields import BADGE_LEVELS

# ---------------------------------------------------------------------------
# BADGE BUDGET PER TIER
# Defines (min, max) count of badges a player gets per tier per category.
# Legend badges are ultra-rare and only appear on Tier 1 at low probability.
# ---------------------------------------------------------------------------

BADGE_BUDGET = {
    # Tier: {level: (min, max)}
    1: {
        "Legend":        (0, 2),
        "Hall of Fame":  (3, 7),
        "Gold":          (5, 10),
        "Silver":        (6, 12),
        "Bronze":        (8, 14),
    },
    2: {
        "Legend":        (0, 0),
        "Hall of Fame":  (1, 3),
        "Gold":          (3, 7),
        "Silver":        (5, 10),
        "Bronze":        (7, 13),
    },
    3: {
        "Legend":        (0, 0),
        "Hall of Fame":  (0, 1),
        "Gold":          (1, 4),
        "Silver":        (3, 7),
        "Bronze":        (5, 10),
    },
    4: {
        "Legend":        (0, 0),
        "Hall of Fame":  (0, 0),
        "Gold":          (0, 2),
        "Silver":        (1, 4),
        "Bronze":        (3, 8),
    },
}

# How likely a priority badge is to receive a higher level vs. a random badge
# Priority badges are 3x more likely to receive Gold/HoF/Legend treatment
PRIORITY_BADGE_MULTIPLIER = 3.0

# Badge level weight distributions used when randomly picking a level
# for a badge slot (after budget is allocated)
BADGE_LEVEL_WEIGHTS = {
    "Legend":       0.02,
    "Hall of Fame": 0.10,
    "Gold":         0.20,
    "Silver":       0.30,
    "Bronze":       0.38,
}

# Minimum tier required for each badge level
BADGE_TIER_MINIMUMS = {
    "Legend":       1,
    "Hall of Fame": 1,
    "Gold":         2,
    "Silver":       3,
    "Bronze":       4,
}
