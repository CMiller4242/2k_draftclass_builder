"""
Per-archetype tendency identity rules.

Drives tendency generation so that 80-90% of a player's tendencies are
shaped by archetype identity, with only 10-20% variance. Eliminates the
cross-archetype noise that previously caused bigs to spam pull-up threes
or shooters to post up at meaningful rates.

Each archetype maps to a dict of TENDENCY GROUP keys → identity tag.
Identity tags:
    "core"       → primary identity. Defaults sit high (55-75) when not
                   listed in the archetype's explicit tendency_profile.
    "support"    → secondary action the archetype reaches for occasionally.
                   Defaults around the 40-55 band.
    "neutral"    → average behavior; defaults around 35-50.
    "suppress"   → off-identity. Defaults sit very low (8-22).
    "hard_off"   → archetype should essentially never do this. Defaults 3-12.

If a tendency is not present in any group OR is already in the archetype's
explicit tendency_profile, the identity rules don't apply (the explicit
profile wins).
"""

# ---------------------------------------------------------------------------
# TENDENCY GROUPS — coarse buckets used to apply identity rules en masse.
# ---------------------------------------------------------------------------

JUMPSHOT_3PT_GROUP = (
    "Shot Three", "Spot Up Shot Three", "Off Screen Shot Three",
    "Shot Three Left", "Shot Three Left-Center", "Shot Three Center",
    "Shot Three Right-Center", "Shot Three Right",
    "Contested Jumper Three", "Stepback Jumper Three",
    "Transition Pull-Up Three", "Drive Pull Up Three",
)

JUMPSHOT_MID_GROUP = (
    "Shot Mid-Range", "Spot Up Shot Mid-Range", "Off Screen Shot Mid-Range",
    "Shot Mid Left", "Shot Mid Left-Center", "Shot Mid Center",
    "Shot Mid Right-Center", "Shot Mid Right",
    "Contested Jumper Mid-Range", "Stepback Jumper Mid-Range",
    "Drive Pull Up Mid-Range", "Spin Jumper",
)

CLOSE_SHOT_GROUP = (
    "Shot Close", "Shot Close Left", "Shot Close Middle", "Shot Close Right",
    "Step Through Shot", "Shot Under Basket",
)

DUNK_GROUP = (
    "Standing Dunk", "Driving Dunk", "Flashy Dunk", "Alley-Oop", "Putback",
)

LAYUP_GROUP = (
    "Driving Layup", "Spin Layup", "Hop Step Layup", "Euro Step Layup",
    "Floater",
)

CRASH_GROUP = ("Crash", "Putback")

DRIVE_GROUP = (
    "Drive", "Spot Up Drive", "Off Screen Drive", "Drive Right",
    "Driving Crossover", "Driving Spin", "Driving Step Back",
    "Driving Half Spin", "Driving Double Crossover",
    "Driving Behind the Back", "Driving Dribble Hesitation",
    "Driving In and Out", "Attack Strong on Drive",
)

DRIVE_SETUP_GROUP = (
    "Triple Threat Pump Fake", "Triple Threat Jab Step",
    "Triple Threat Idle", "Triple Threat Shoot",
    "Setup With Sizeup", "Setup With Hesitation", "No Setup Dribble",
)

POST_GROUP = (
    "Post Up", "Post Shimmy Shot", "Post Face Up",
    "Post Back Down", "Post Aggressive Back Down",
    "Shoot From Post", "Post Hook Left", "Post Hook Right",
    "Post Fade Left", "Post Fade Right",
    "Post Up and Under", "Post Hop Shot", "Post Step Back Shot",
    "Post Drive", "Post Spin", "Post Drop Step", "Post Hop Step",
)

ISO_GROUP = (
    "Iso vs Elite Defender", "Iso vs Good Defender",
    "Iso vs Average Defender", "Iso vs Poor Defender",
)

PASS_GROUP = ("Pass to Open Man", "Flashy Pass", "Alley-Oop Pass")

DEFENSE_RIM_GROUP = ("Block Shot", "Contest Shot")

DEFENSE_PERIMETER_GROUP = ("On-Ball Steal", "Pass Interception")


# ---------------------------------------------------------------------------
# ARCHETYPE IDENTITY MATRIX
# Each archetype lists how every group should behave by default.
# Explicit tendency_profile values in archetypes.py always override these.
# ---------------------------------------------------------------------------

ARCHETYPE_TENDENCY_IDENTITY = {
    # =========================================================================
    # GUARDS / WINGS — perimeter shooters
    # =========================================================================
    "Movement Shooter": {
        JUMPSHOT_3PT_GROUP:        "core",
        JUMPSHOT_MID_GROUP:        "support",
        CLOSE_SHOT_GROUP:          "neutral",
        DUNK_GROUP:                "hard_off",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "hard_off",
        ISO_GROUP:                 "suppress",
        PASS_GROUP:                "support",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "hard_off",
    },
    "Shot Hunter": {
        JUMPSHOT_3PT_GROUP:        "core",
        JUMPSHOT_MID_GROUP:        "core",
        CLOSE_SHOT_GROUP:          "neutral",
        DUNK_GROUP:                "hard_off",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "support",
        POST_GROUP:                "hard_off",
        ISO_GROUP:                 "core",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "hard_off",
    },
    "Iso Creator": {
        JUMPSHOT_3PT_GROUP:        "support",
        JUMPSHOT_MID_GROUP:        "core",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "suppress",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "core",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "core",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "hard_off",
    },
    "Mid-Range Specialist": {
        JUMPSHOT_3PT_GROUP:        "suppress",
        JUMPSHOT_MID_GROUP:        "core",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "hard_off",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "support",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "support",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "hard_off",
    },
    "3-Level Scorer": {
        JUMPSHOT_3PT_GROUP:        "core",
        JUMPSHOT_MID_GROUP:        "core",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "suppress",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "support",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "support",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "hard_off",
    },
    "Inside-Out Scorer": {
        JUMPSHOT_3PT_GROUP:        "support",
        JUMPSHOT_MID_GROUP:        "neutral",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "support",
        LAYUP_GROUP:               "core",
        DRIVE_GROUP:               "core",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "support",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "suppress",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "suppress",
    },

    # =========================================================================
    # WINGS — drivers / two-way / defensive
    # =========================================================================
    "Slashing Forward": {
        JUMPSHOT_3PT_GROUP:        "suppress",
        JUMPSHOT_MID_GROUP:        "neutral",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "core",
        LAYUP_GROUP:               "core",
        DRIVE_GROUP:               "core",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "support",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "neutral",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "support",
    },
    "High Flyer": {
        JUMPSHOT_3PT_GROUP:        "hard_off",
        JUMPSHOT_MID_GROUP:        "suppress",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "core",
        LAYUP_GROUP:               "core",
        DRIVE_GROUP:               "core",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "suppress",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "neutral",
        DEFENSE_PERIMETER_GROUP:   "neutral",
        CRASH_GROUP:               "core",
    },
    "Two-Way Wing": {
        JUMPSHOT_3PT_GROUP:        "support",
        JUMPSHOT_MID_GROUP:        "support",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "neutral",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "support",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "neutral",
        PASS_GROUP:                "support",
        DEFENSE_RIM_GROUP:         "core",
        DEFENSE_PERIMETER_GROUP:   "core",
        CRASH_GROUP:               "neutral",
    },
    "Defensive Connector": {
        JUMPSHOT_3PT_GROUP:        "support",
        JUMPSHOT_MID_GROUP:        "neutral",
        CLOSE_SHOT_GROUP:          "neutral",
        DUNK_GROUP:                "suppress",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "hard_off",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "core",
        DEFENSE_RIM_GROUP:         "core",
        DEFENSE_PERIMETER_GROUP:   "core",
        CRASH_GROUP:               "support",
    },
    "Lockdown Guard": {
        JUMPSHOT_3PT_GROUP:        "neutral",
        JUMPSHOT_MID_GROUP:        "suppress",
        CLOSE_SHOT_GROUP:          "neutral",
        DUNK_GROUP:                "suppress",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "hard_off",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "support",
        DEFENSE_RIM_GROUP:         "support",
        DEFENSE_PERIMETER_GROUP:   "core",
        CRASH_GROUP:               "suppress",
    },

    # =========================================================================
    # BIGS
    # =========================================================================
    "Rim Running Big": {
        JUMPSHOT_3PT_GROUP:        "hard_off",
        JUMPSHOT_MID_GROUP:        "suppress",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "core",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "support",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "core",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "core",
    },
    "Playmaking Big": {
        JUMPSHOT_3PT_GROUP:        "neutral",
        JUMPSHOT_MID_GROUP:        "support",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "support",
        LAYUP_GROUP:               "support",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "support",
        ISO_GROUP:                 "suppress",
        PASS_GROUP:                "core",
        DEFENSE_RIM_GROUP:         "support",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "neutral",
    },
    "Stretch Big": {
        JUMPSHOT_3PT_GROUP:        "core",
        JUMPSHOT_MID_GROUP:        "support",
        CLOSE_SHOT_GROUP:          "neutral",
        DUNK_GROUP:                "neutral",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "support",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "support",
        DEFENSE_RIM_GROUP:         "support",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "neutral",
    },
    "Glass Cleaner": {
        JUMPSHOT_3PT_GROUP:        "hard_off",
        JUMPSHOT_MID_GROUP:        "hard_off",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "support",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "core",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "core",
    },
    "Paint Bully": {
        JUMPSHOT_3PT_GROUP:        "hard_off",
        JUMPSHOT_MID_GROUP:        "suppress",
        CLOSE_SHOT_GROUP:          "core",
        DUNK_GROUP:                "support",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "core",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "core",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "support",
    },
    "Putback Finisher": {
        JUMPSHOT_3PT_GROUP:        "hard_off",
        JUMPSHOT_MID_GROUP:        "hard_off",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "core",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "suppress",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "neutral",
        DEFENSE_RIM_GROUP:         "support",
        DEFENSE_PERIMETER_GROUP:   "suppress",
        CRASH_GROUP:               "core",
    },
    "Break Starter": {
        JUMPSHOT_3PT_GROUP:        "suppress",
        JUMPSHOT_MID_GROUP:        "neutral",
        CLOSE_SHOT_GROUP:          "support",
        DUNK_GROUP:                "support",
        LAYUP_GROUP:               "neutral",
        DRIVE_GROUP:               "suppress",
        POST_GROUP:                "neutral",
        ISO_GROUP:                 "hard_off",
        PASS_GROUP:                "core",
        DEFENSE_RIM_GROUP:         "support",
        DEFENSE_PERIMETER_GROUP:   "support",
        CRASH_GROUP:               "support",
    },
}


# ---------------------------------------------------------------------------
# DEFAULT VALUE BANDS PER IDENTITY TAG
# Returned as (low, high) — the actual value gets a small jitter on top.
# ---------------------------------------------------------------------------

IDENTITY_BANDS = {
    "core":     (60, 80),
    "support":  (42, 58),
    "neutral":  (32, 50),
    "suppress": (10, 24),
    "hard_off": (3,  12),
}


# ---------------------------------------------------------------------------
# BADGE CATEGORY IDENTITY
# Per-archetype tag for each top-level badge category. Used by badge_gen
# to bias toward identity-aligned categories and suppress off-identity ones.
#   "core"    → archetype's bread-and-butter category (priority badges live here)
#   "support" → secondary category that occasionally produces good badges
#   "neutral" → no special bias
#   "off"     → strongly suppressed (e.g. Inside Scoring for a shooter)
# ---------------------------------------------------------------------------

BADGE_CATEGORY_IDENTITY = {
    # Shooters / scorers
    "Movement Shooter": {
        "Outside Scoring": "core", "Playmaking": "support",
        "Inside Scoring": "off", "Defending": "off", "Rebounding": "off",
    },
    "Shot Hunter": {
        "Outside Scoring": "core", "Playmaking": "support",
        "Inside Scoring": "off", "Defending": "off", "Rebounding": "off",
    },
    "Iso Creator": {
        "Outside Scoring": "support", "Playmaking": "core",
        "Inside Scoring": "neutral", "Defending": "off", "Rebounding": "off",
    },
    "Mid-Range Specialist": {
        "Outside Scoring": "core", "Playmaking": "neutral",
        "Inside Scoring": "support", "Defending": "off", "Rebounding": "off",
    },
    "3-Level Scorer": {
        "Outside Scoring": "core", "Playmaking": "support",
        "Inside Scoring": "support", "Defending": "off", "Rebounding": "off",
    },
    "Inside-Out Scorer": {
        "Outside Scoring": "support", "Playmaking": "neutral",
        "Inside Scoring": "core", "Defending": "off", "Rebounding": "neutral",
    },

    # Wings
    "Slashing Forward": {
        "Inside Scoring": "core", "Playmaking": "support",
        "Outside Scoring": "off", "Defending": "neutral", "Rebounding": "neutral",
    },
    "High Flyer": {
        "Inside Scoring": "core", "Defending": "support",
        "Outside Scoring": "off", "Playmaking": "off", "Rebounding": "neutral",
    },
    "Two-Way Wing": {
        "Defending": "core", "Outside Scoring": "support",
        "Inside Scoring": "neutral", "Playmaking": "neutral", "Rebounding": "neutral",
    },
    "Defensive Connector": {
        "Defending": "core", "Rebounding": "support",
        "Outside Scoring": "off", "Inside Scoring": "off", "Playmaking": "neutral",
    },
    "Lockdown Guard": {
        "Defending": "core", "Playmaking": "support",
        "Outside Scoring": "neutral", "Inside Scoring": "off", "Rebounding": "off",
    },

    # Bigs
    "Rim Running Big": {
        "Inside Scoring": "core", "Rebounding": "core",
        "Defending": "support", "Outside Scoring": "off", "Playmaking": "off",
    },
    "Playmaking Big": {
        "Playmaking": "core", "Inside Scoring": "support",
        "Rebounding": "support", "Defending": "neutral", "Outside Scoring": "off",
    },
    "Stretch Big": {
        "Outside Scoring": "core", "Inside Scoring": "support",
        "Rebounding": "support", "Defending": "neutral", "Playmaking": "off",
    },
    "Glass Cleaner": {
        "Rebounding": "core", "Defending": "core",
        "Inside Scoring": "support",
        "Outside Scoring": "off", "Playmaking": "off",
    },
    "Paint Bully": {
        "Inside Scoring": "core", "Defending": "support",
        "Rebounding": "support",
        "Outside Scoring": "off", "Playmaking": "off",
    },
    "Putback Finisher": {
        "Rebounding": "core", "Inside Scoring": "core",
        "Defending": "support",
        "Outside Scoring": "off", "Playmaking": "off",
    },
    "Break Starter": {
        "Playmaking": "core", "Rebounding": "support",
        "Defending": "support", "Inside Scoring": "neutral", "Outside Scoring": "off",
    },
}


def get_badge_category_identity(archetype_name: str, category: str) -> str:
    """Return identity tag for a (archetype, badge_category) pair."""
    return BADGE_CATEGORY_IDENTITY.get(archetype_name, {}).get(category, "neutral")


def get_tendency_identity(archetype_name: str, tendency: str) -> str:
    """
    Return the identity tag ("core" / "support" / "neutral" /
    "suppress" / "hard_off") for a given (archetype, tendency) pair.

    Returns "neutral" if the archetype is unknown or the tendency is
    not classified by any group for this archetype.
    """
    matrix = ARCHETYPE_TENDENCY_IDENTITY.get(archetype_name)
    if not matrix:
        return "neutral"
    for group_list, tag in matrix.items():
        if tendency in group_list:
            return tag
    return "neutral"
