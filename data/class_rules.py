"""
Class-type and flavor rules for draft class generation.

Tier distribution logic lives here. class_type determines HOW GOOD the class
is overall; class_flavor influences WHAT KINDS of players populate it.
"""

# ---------------------------------------------------------------------------
# TIER DEFINITIONS
# ---------------------------------------------------------------------------

TIER_LABELS = {
    1: "Superstar",
    2: "All-Star / High-End Starter",
    3: "Starter / Rotation",
    4: "Role Player / Bust",
}

# ---------------------------------------------------------------------------
# CLASS TYPE DEFINITIONS
# ---------------------------------------------------------------------------
# Each class type stores:
#   base_distribution:  fractional weights for tiers [T1, T2, T3, T4]
#   tier1_min / tier1_max: absolute min/max Tier 1 players (for small classes)
#   description: flavor text
# ---------------------------------------------------------------------------

CLASS_TYPES = {
    "Generational": {
        "description": "A once-in-a-generation class headlined by multiple franchise players.",
        "base_distribution": [0.12, 0.22, 0.38, 0.28],
        "tier1_guaranteed": 2,
        "star_floor": 3,   # At least this many Tier 1+2 combined
    },
    "Strong": {
        "description": "A deep class with a legitimate franchise player and strong supporting talent.",
        "base_distribution": [0.07, 0.18, 0.42, 0.33],
        "tier1_guaranteed": 1,
        "star_floor": 2,
    },
    "Average": {
        "description": "A typical draft with a few solid contributors and plenty of role players.",
        "base_distribution": [0.03, 0.12, 0.43, 0.42],
        "tier1_guaranteed": 0,
        "star_floor": 1,
    },
    "Weak": {
        "description": "A thin class — even the top pick may not be a franchise cornerstone.",
        "base_distribution": [0.02, 0.06, 0.37, 0.55],
        "tier1_guaranteed": 0,
        "star_floor": 0,
    },
    "Bust-heavy": {
        "description": "Paper prospects — lots of talent on paper, few translating to success.",
        "base_distribution": [0.03, 0.08, 0.27, 0.62],
        "tier1_guaranteed": 0,
        "star_floor": 0,
    },
    "Top-heavy": {
        "description": "Elite at the top, steep drop-off after the top 3–5 picks.",
        "base_distribution": [0.08, 0.10, 0.30, 0.52],
        "tier1_guaranteed": 1,
        "star_floor": 1,
    },
    "Deep role-player class": {
        "description": "No superstars, but loaded with quality role players who last 10+ years.",
        "base_distribution": [0.01, 0.08, 0.55, 0.36],
        "tier1_guaranteed": 0,
        "star_floor": 0,
    },
}

CLASS_TYPE_NAMES = list(CLASS_TYPES.keys())

# ---------------------------------------------------------------------------
# CLASS FLAVOR DEFINITIONS
# ---------------------------------------------------------------------------
# Each flavor biases archetype selection weights.
# Keys are archetype names; values are relative weight multipliers.
# Archetypes not listed default to 1.0.
# ---------------------------------------------------------------------------

CLASS_FLAVORS = {
    # -------------------------------------------------------------------------
    # Balanced — all 18 archetypes get equal weight (no adjustments)
    # -------------------------------------------------------------------------
    "Balanced": {
        "description": "Even mix of positions and archetypes.",
        "archetype_weights": {},
    },

    # -------------------------------------------------------------------------
    # Guard-heavy — perimeter players dominate; bigs deprioritized
    # Boosted: Movement Shooter, Iso Creator, Shot Hunter, Lockdown Guard,
    #          3-Level Scorer, Defensive Connector
    # Reduced: all interior bigs
    # -------------------------------------------------------------------------
    "Guard-heavy": {
        "description": "Loaded with guards and perimeter players.",
        "archetype_weights": {
            "Movement Shooter":   2.5,
            "Iso Creator":        2.5,
            "Shot Hunter":        2.5,
            "Lockdown Guard":     2.0,
            "3-Level Scorer":     2.0,
            "Defensive Connector": 1.5,
            "Mid-Range Specialist": 1.5,
            # Bigs down
            "Rim Running Big":    0.4,
            "Playmaking Big":     0.4,
            "Stretch Big":        0.6,
            "Paint Bully":        0.3,
            "Glass Cleaner":      0.3,
            "Break Starter":      0.4,
            "Putback Finisher":   0.3,
        },
    },

    # -------------------------------------------------------------------------
    # Wing-heavy — versatile wings and forwards in abundance
    # Boosted: Two-Way Wing, Slashing Forward, 3-Level Scorer,
    #          Mid-Range Specialist, Inside-Out Scorer, High Flyer
    # Reduced: interior-only bigs, pure point guards
    # -------------------------------------------------------------------------
    "Wing-heavy": {
        "description": "Depth of versatile wings across both forward spots.",
        "archetype_weights": {
            "Two-Way Wing":        2.5,
            "Slashing Forward":    2.5,
            "3-Level Scorer":      2.0,
            "Mid-Range Specialist": 2.0,
            "Inside-Out Scorer":   2.0,
            "High Flyer":          2.0,
            "Defensive Connector": 2.0,
            "Movement Shooter":    1.5,
            # Bigs down
            "Rim Running Big":     0.4,
            "Paint Bully":         0.3,
            "Glass Cleaner":       0.3,
            "Break Starter":       0.3,
            "Putback Finisher":    0.3,
        },
    },

    # -------------------------------------------------------------------------
    # Big-heavy — loaded at center and power forward
    # Boosted: all big archetypes
    # Reduced: perimeter guards
    # -------------------------------------------------------------------------
    "Big-heavy": {
        "description": "Deep at center and power forward.",
        "archetype_weights": {
            "Rim Running Big":   2.5,
            "Playmaking Big":    2.5,
            "Stretch Big":       2.0,
            "Paint Bully":       2.5,
            "Glass Cleaner":     2.5,
            "Break Starter":     2.0,
            "Putback Finisher":  2.0,
            # Perimeter guards down
            "Iso Creator":       0.5,
            "Movement Shooter":  0.5,
            "Shot Hunter":       0.4,
            "Lockdown Guard":    0.5,
            "3-Level Scorer":    0.6,
        },
    },

    # -------------------------------------------------------------------------
    # Defensive-heavy — defense comes first across every position
    # Boosted: Two-Way Wing, Defensive Connector, Lockdown Guard,
    #          Rim Running Big, Glass Cleaner
    # Reduced: volume scorers, shot creators
    # -------------------------------------------------------------------------
    "Defensive-heavy": {
        "description": "Defense-first prospects throughout.",
        "archetype_weights": {
            "Two-Way Wing":      2.5,
            "Defensive Connector": 3.0,
            "Lockdown Guard":    3.0,
            "Rim Running Big":   2.0,
            "Glass Cleaner":     2.0,
            # Offensive specialists down
            "Movement Shooter":  0.5,
            "Iso Creator":       0.5,
            "Shot Hunter":       0.4,
            "Mid-Range Specialist": 0.6,
            "3-Level Scorer":    0.6,
            "Paint Bully":       0.8,
        },
    },

    # -------------------------------------------------------------------------
    # Shooting-heavy — shooters at every position, stretch bigs prevalent
    # Boosted: Movement Shooter, Shot Hunter, Stretch Big, 3-Level Scorer,
    #          Mid-Range Specialist
    # Reduced: non-shooting bigs, pure defenders
    # -------------------------------------------------------------------------
    "Shooting-heavy": {
        "description": "Shooters everywhere — stretch bigs, spot-up wings, volume guards.",
        "archetype_weights": {
            "Movement Shooter":    3.0,
            "Shot Hunter":         2.5,
            "Stretch Big":         2.5,
            "3-Level Scorer":      2.0,
            "Mid-Range Specialist": 1.5,
            "Iso Creator":         1.5,
            "Inside-Out Scorer":   1.5,
            # Non-shooting bigs / defenders down
            "Rim Running Big":     0.4,
            "Paint Bully":         0.4,
            "Glass Cleaner":       0.4,
            "Defensive Connector": 0.5,
            "Lockdown Guard":      0.5,
        },
    },

    # -------------------------------------------------------------------------
    # High variance — boom-or-bust; archetype mix stays even but busts spike
    # -------------------------------------------------------------------------
    "High variance": {
        "description": "Boom-or-bust prospects — polarized talent distribution.",
        "archetype_weights": {},
        "extra_bust_weight": 0.25,
    },

    # -------------------------------------------------------------------------
    # Low variance — safe, floor-heavy prospects; bust probability suppressed
    # -------------------------------------------------------------------------
    "Low variance": {
        "description": "Safe, polished players — lower upside but fewer busts.",
        "archetype_weights": {},
        "extra_bust_weight": -0.20,
    },
}

CLASS_FLAVOR_NAMES = list(CLASS_FLAVORS.keys())

# ---------------------------------------------------------------------------
# DEVELOPMENT TRAJECTORY LABELS
# ---------------------------------------------------------------------------

DEVELOPMENT_OUTLOOKS = [
    "Immediate Contributor",
    "Slow Burn",
    "Ceiling Chaser",
    "Peak and Decline",
    "Late Bloomer",
    "One-and-Done Potential",
    "Career Backup",
    "Journeyman",
    "Culture Player",
    "Franchise Cornerstone",
]

# ---------------------------------------------------------------------------
# TIER 1 HARD CAPS
# (small_cap, large_cap) for player counts ≤30 and 31–60 respectively
# ---------------------------------------------------------------------------

TIER1_CAPS = {
    "Generational":           (2, 3),
    "Strong":                 (2, 2),
    "Average":                (1, 2),
    "Weak":                   (0, 1),
    "Bust-heavy":             (1, 1),
    "Top-heavy":              (2, 3),
    "Deep role-player class": (0, 1),
}

# ---------------------------------------------------------------------------
# BUST PROBABILITY MODIFIERS BY CLASS TYPE AND FLAVOR
# Added to the per-tier base probability in BUST_RISK_BY_TIER.
# ---------------------------------------------------------------------------

BUST_RISK_CLASS_MODIFIERS = {
    "Generational":           -0.08,
    "Strong":                 -0.05,
    "Average":                  0.0,
    "Weak":                    0.08,
    "Bust-heavy":              0.20,
    "Top-heavy":               0.05,
    "Deep role-player class": -0.10,
}

BUST_RISK_FLAVOR_MODIFIERS = {
    "Balanced":        0.0,
    "Guard-heavy":     0.0,
    "Wing-heavy":      0.0,
    "Big-heavy":       0.0,
    "Defensive-heavy": 0.0,
    "Shooting-heavy":  0.0,
    "High variance":   0.15,
    "Low variance":   -0.15,
}

# ---------------------------------------------------------------------------
# BUST RISK BY TIER
# ---------------------------------------------------------------------------
# Probability that a player underperforms their potential.
# Tier 4 players are by definition low-ceiling; bust here means they're
# simply average rather than contributors.

BUST_RISK_BY_TIER = {
    1: 0.12,   # 12% chance a Tier 1 player severely underperforms
    2: 0.22,
    3: 0.30,
    4: 0.55,   # Tier 4 is already "role player" — bust means they never make a roster
}

# ---------------------------------------------------------------------------
# PROJECTED ROLES
# ---------------------------------------------------------------------------

PROJECTED_ROLES = {
    1: [
        "Franchise Player",
        "Perennial All-Star",
        "First-Option Scorer",
        "Defensive Anchor / All-Star",
    ],
    2: [
        "Second-Option Star",
        "High-End Starter",
        "Elite Role Player",
        "All-Star Caliber",
    ],
    3: [
        "Solid Starter",
        "Quality Rotation Player",
        "Defensive Starter",
        "Offensive Specialist",
    ],
    4: [
        "End-of-Bench Role Player",
        "Energy Guy",
        "Spot Minute Contributor",
        "Two-Way Call-Up",
        "Career Backup",
        "Practice Player",
    ],
}
