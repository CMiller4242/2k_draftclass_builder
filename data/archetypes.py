"""
Archetype definitions for the 2K Draft Class Builder.

Each archetype specifies physical ranges, attribute priorities, tendency
profiles, and badge priorities per tier. New archetypes can be added by
following the same structure.

Attribute ranges are expressed as (min, max) tuples for Tier 3 (average
starter). Tier scaling modifiers adjust the ceiling/floor for higher tiers.
"""

from data.fields import (
    PERSONALITY_BADGES, INSIDE_SCORING_BADGES, OUTSIDE_SCORING_BADGES,
    PLAYMAKING_BADGES, DEFENDING_BADGES, ATHLETICISM_BADGES, REBOUNDING_BADGES,
)

# ---------------------------------------------------------------------------
# TIER ATTRIBUTE MODIFIERS
# Each tier shifts base attribute ranges up or down.
# Applied as: final_range = (base_min + mod, base_max + mod), clamped 25–99
# ---------------------------------------------------------------------------
TIER_ATTRIBUTE_MODIFIERS = {
    1: 20,   # Superstar
    2: 10,   # All-Star / high-end starter
    3: 0,    # Starter / rotation (baseline)
    4: -15,  # Role player / bust
}

# ---------------------------------------------------------------------------
# ARCHETYPES
# ---------------------------------------------------------------------------

ARCHETYPES = {
    "Movement Shooter": {
        "description": (
            "An elite off-ball shooter who thrives in catch-and-shoot "
            "situations. Uses screens masterfully, excels at spot-up threes, "
            "and creates gravity without the ball."
        ),
        "valid_positions": ["SG", "SF", "PG/SG", "SG/SF"],
        "height_range_inches": (73, 78),   # 6'1" to 6'6"
        "weight_range_lbs": (185, 220),
        # Core attribute priority ranges (Tier 3 baseline)
        "attribute_priorities": {
            "Three Point Shot": (78, 88),
            "Mid Range Shot": (72, 82),
            "Free Throw": (75, 85),
            "Shot IQ": (75, 85),
            "Catch and Shoot tendency": (80, 95),
            "Speed": (72, 82),
            "Agility": (72, 82),
            "Ball Handle": (55, 68),
            "Pass IQ": (60, 72),
            "Driving Layup": (50, 62),
            "Interior Defense": (35, 50),
            "Post Control": (30, 45),
        },
        # Tendency profile keys — high values push behavior toward these actions
        "tendency_profile": {
            "Shot Three": 85,
            "Spot Up Shot Three": 90,
            "Off Screen Shot Three": 88,
            "Shot Mid-Range": 40,
            "Drive": 30,
            "Post Up": 15,
            "Pass to Open Man": 65,
            "Contest Shot": 55,
        },
        "badge_priorities": {
            "Outside Scoring": ["Catch and Shoot", "Deadeye", "Limitless Range",
                                 "Corner Specialist", "Rhythm Shooter", "Quick Draw"],
            "Athleticism": ["Fast Twitch", "Speed Booster"],
            "Playmaking": ["Slippery Off-Ball"],
            "Personality": ["Hot Zone Hunter"],
        },
        # Archetypes that bust tend to have low IQ despite high shooting stats
        "bust_profile": {
            "Shot IQ": (-15, -10),
            "Defensive Consistency": (-20, -10),
        },
    },

    "Iso Creator": {
        "description": (
            "A ball-dominant offensive engine who creates his own shot off the "
            "dribble from anywhere on the floor. Elite mid-range and pull-up "
            "game with deceptive quickness."
        ),
        "valid_positions": ["SG", "PG", "SF", "SG/PG", "PG/SG"],
        "height_range_inches": (74, 79),   # 6'2" to 6'7"
        "weight_range_lbs": (190, 225),
        "attribute_priorities": {
            "Ball Handle": (82, 92),
            "Mid Range Shot": (78, 88),
            "Three Point Shot": (72, 84),
            "Shot IQ": (80, 90),
            "Drive Foul": (70, 82),
            "Speed With Ball": (75, 85),
            "Agility": (74, 84),
            "Driving Layup": (74, 85),
            "Pass IQ": (68, 78),
            "Pass Accuracy": (65, 76),
            "Perimeter Defense": (50, 65),
        },
        "tendency_profile": {
            "Drive": 75,
            "Shot Mid-Range": 80,
            "Shot Three": 65,
            "Stepback Jumper Mid-Range": 80,
            "Stepback Jumper Three": 70,
            "Drive Pull Up Mid-Range": 78,
            "Iso vs Good Defender": 80,
            "Iso vs Average Defender": 90,
            "Spot Up Drive": 50,
            "Post Up": 20,
            "Pass to Open Man": 55,
        },
        "badge_priorities": {
            "Outside Scoring": ["Pull-Up Precision", "Mismatch Expert",
                                 "Stop and Pop", "Volume Shooter"],
            "Playmaking": ["Ankle Assassin", "Quick First Step", "Handles for Days",
                           "Killer Combos", "Hyperdrive"],
            "Personality": ["Killer Instinct", "Competitor"],
        },
        "bust_profile": {
            "Pass IQ": (-18, -12),
            "Help Defense IQ": (-20, -10),
            "Offensive Consistency": (-15, -8),
        },
    },

    "Two-Way Wing": {
        "description": (
            "A versatile wing who can guard 1–4 and contribute on both ends. "
            "Not a primary scorer, but reliable enough offensively while being "
            "a defensive anchor."
        ),
        "valid_positions": ["SF", "SG", "PF", "SF/SG", "SF/PF", "SG/SF"],
        "height_range_inches": (77, 82),   # 6'5" to 6'10"
        "weight_range_lbs": (210, 240),
        "attribute_priorities": {
            "Perimeter Defense": (80, 90),
            "Interior Defense": (65, 78),
            "Steal": (72, 82),
            "Defensive Consistency": (78, 88),
            "Help Defense IQ": (75, 85),
            "Three Point Shot": (68, 78),
            "Mid Range Shot": (65, 76),
            "Speed": (74, 84),
            "Agility": (72, 82),
            "Ball Handle": (62, 73),
            "Driving Layup": (68, 78),
            "Hustle": (80, 90),
        },
        "tendency_profile": {
            "Shot Three": 60,
            "Spot Up Shot Three": 72,
            "Drive": 55,
            "Driving Layup": 60,
            "Contest Shot": 85,
            "On-Ball Steal": 75,
            "Pass Interception": 70,
            "Post Up": 25,
            "Pass to Open Man": 70,
        },
        "badge_priorities": {
            "Defending": ["Clamps", "Glove", "Challenger", "Tireless Defender",
                          "Intimidator", "Guard Up"],
            "Outside Scoring": ["Catch and Shoot", "Deadeye"],
            "Athleticism": ["Physical Toughness", "Chase Down Artist"],
            "Personality": ["Defensive Stopper", "Winner"],
        },
        "bust_profile": {
            "Three Point Shot": (-15, -10),
            "Shot IQ": (-12, -8),
        },
    },

    "Rim Running Big": {
        "description": (
            "A high-energy big who lives above the rim as a lob threat, "
            "putback machine, and paint protector. Limited range but "
            "dominant athleticism inside."
        ),
        "valid_positions": ["C", "PF", "C/PF", "PF/C"],
        "height_range_inches": (81, 87),   # 6'9" to 7'3"
        "weight_range_lbs": (240, 280),
        "attribute_priorities": {
            "Standing Dunk": (80, 92),
            "Driving Layup": (72, 83),
            "Close Shot": (74, 85),
            "Offensive Rebound": (80, 90),
            "Defensive Rebound": (80, 90),
            "Interior Defense": (75, 88),
            "Block": (78, 90),
            "Vertical": (82, 93),
            "Strength": (78, 88),
            "Speed": (65, 76),
            "Agility": (60, 72),
            "Three Point Shot": (30, 45),
        },
        "tendency_profile": {
            "Standing Dunk": 85,
            "Driving Dunk": 80,
            "Alley-Oop": 90,
            "Putback": 88,
            "Crash": 85,
            "Post Up": 60,
            "Shot Three": 10,
            "Roll vs Pop": 90,  # Prefers roll
            "Block Shot": 80,
            "Pass to Open Man": 50,
        },
        "badge_priorities": {
            "Inside Scoring": ["Contact Finisher", "Putback Artist", "Rise Up",
                               "Slithery Finisher", "Pro Touch"],
            "Rebounding": ["Glass Cleaner", "Crash", "Power Rebounder",
                           "Worm", "Hustle Rebounder"],
            "Defending": ["Rim Protector", "Intimidator", "Pogo Stick"],
            "Athleticism": ["High Flyer", "Coiled Spring", "Fast Twitch"],
        },
        "bust_profile": {
            "Free Throw": (-25, -15),
            "Defensive Consistency": (-15, -8),
        },
    },

    "Playmaking Big": {
        "description": (
            "A modern center who can initiate offense, hit the mid-range, "
            "and pick-and-roll. The anchor of a modern offense with elite "
            "passing for the position."
        ),
        "valid_positions": ["C", "PF", "C/PF"],
        "height_range_inches": (82, 87),   # 6'10" to 7'3"
        "weight_range_lbs": (240, 275),
        "attribute_priorities": {
            "Pass IQ": (78, 90),
            "Pass Accuracy": (75, 87),
            "Pass Vision": (75, 87),
            "Ball Handle": (65, 78),
            "Mid Range Shot": (70, 82),
            "Three Point Shot": (62, 75),
            "Post Control": (72, 83),
            "Interior Defense": (70, 83),
            "Defensive Rebound": (75, 85),
            "Offensive Rebound": (72, 82),
            "Block": (65, 78),
            "Strength": (75, 85),
        },
        "tendency_profile": {
            "Shot Mid-Range": 70,
            "Shot Three": 40,
            "Roll vs Pop": 50,  # Can do both
            "Post Up": 55,
            "Pass to Open Man": 80,
            "Alley-Oop Pass": 70,
            "Driving Layup": 50,
            "Block Shot": 65,
        },
        "badge_priorities": {
            "Playmaking": ["Pick and Roll Maestro", "Lob City Passer",
                           "Post Playmaker", "Needle Threader", "Special Delivery"],
            "Inside Scoring": ["Deep Hooks", "Backdown Punisher", "Dream Shake"],
            "Rebounding": ["Glass Cleaner", "High-Low Detective"],
            "Defending": ["Rim Protector", "Pogo Stick", "Intimidator"],
        },
        "bust_profile": {
            "Defensive Consistency": (-18, -10),
            "Stamina": (-15, -10),
        },
    },

    "Slashing Forward": {
        "description": (
            "An explosive forward who attacks the rim relentlessly. Thrives "
            "in transition and off ball screens. Limited shooting range but "
            "devastating in the paint."
        ),
        "valid_positions": ["SF", "PF", "SG", "SF/PF", "SF/SG"],
        "height_range_inches": (78, 83),   # 6'6" to 6'11"
        "weight_range_lbs": (220, 250),
        "attribute_priorities": {
            "Driving Layup": (82, 92),
            "Driving Dunk": (75, 87),
            "Draw Foul": (75, 86),
            "Speed": (78, 88),
            "Agility": (76, 86),
            "Vertical": (78, 89),
            "Ball Handle": (68, 78),
            "Strength": (72, 82),
            "Three Point Shot": (50, 65),
            "Perimeter Defense": (62, 75),
            "Interior Defense": (65, 78),
        },
        "tendency_profile": {
            "Drive": 88,
            "Driving Layup": 85,
            "Driving Dunk": 80,
            "Flashy Dunk": 65,
            "Euro Step Layup": 78,
            "Shot Three": 30,
            "Spot Up Shot Three": 35,
            "Post Up": 35,
            "Attack Strong on Drive": 80,
        },
        "badge_priorities": {
            "Inside Scoring": ["Contact Finisher", "Slithery Finisher", "Float Game",
                               "Acrobat", "Giant Slayer", "Pro Touch"],
            "Athleticism": ["Fast Twitch", "High Flyer", "Physical Specimen"],
            "Playmaking": ["Quick First Step", "Downhill"],
            "Defending": ["Challenger", "Fast Feet"],
        },
        "bust_profile": {
            "Three Point Shot": (-20, -12),
            "Free Throw": (-20, -12),
            "Offensive Consistency": (-15, -8),
        },
    },

    "Defensive Connector": {
        "description": (
            "A highly intelligent defensive specialist who ties the defense "
            "together with elite IQ, communication, and versatility. Minimal "
            "offensive role but irreplaceable on winning teams."
        ),
        "valid_positions": ["SG", "SF", "PF", "PG/SG", "SF/PF"],
        "height_range_inches": (76, 82),   # 6'4" to 6'10"
        "weight_range_lbs": (210, 245),
        "attribute_priorities": {
            "Perimeter Defense": (82, 92),
            "Interior Defense": (70, 82),
            "Help Defense IQ": (85, 95),
            "Defensive Consistency": (82, 92),
            "Steal": (72, 84),
            "Block": (60, 72),
            "Hustle": (82, 92),
            "Strength": (72, 83),
            "Speed": (72, 83),
            "Three Point Shot": (62, 73),
            "Ball Handle": (50, 62),
        },
        "tendency_profile": {
            "Contest Shot": 90,
            "On-Ball Steal": 80,
            "Pass Interception": 82,
            "Block Shot": 70,
            "Foul": 40,
            "Shot Three": 55,
            "Spot Up Shot Three": 68,
            "Drive": 35,
            "Post Up": 20,
            "Pass to Open Man": 78,
        },
        "badge_priorities": {
            "Defending": ["Clamps", "Glove", "Defensive Leader", "Menace",
                          "Tireless Defender", "Fast Feet", "Crowd Control",
                          "High-Low Detective"],
            "Athleticism": ["Physical Toughness", "Chase Down Artist"],
            "Personality": ["Defensive Stopper", "Intimidator"],
            "Rebounding": ["Hustle Rebounder"],
        },
        "bust_profile": {
            "Offensive Consistency": (-20, -15),
            "Ball Handle": (-12, -8),
        },
    },

    "Stretch Big": {
        "description": (
            "A modern big man who stretches the floor with three-point "
            "shooting while providing interior presence. Forces opposing "
            "bigs to guard them on the perimeter."
        ),
        "valid_positions": ["PF", "C", "PF/C", "C/PF"],
        "height_range_inches": (80, 86),   # 6'8" to 7'2"
        "weight_range_lbs": (235, 270),
        "attribute_priorities": {
            "Three Point Shot": (75, 87),
            "Mid Range Shot": (72, 84),
            "Free Throw": (70, 82),
            "Post Control": (68, 80),
            "Interior Defense": (68, 80),
            "Defensive Rebound": (72, 82),
            "Offensive Rebound": (65, 75),
            "Block": (68, 80),
            "Strength": (76, 86),
            "Speed": (60, 72),
            "Ball Handle": (58, 70),
        },
        "tendency_profile": {
            "Shot Three": 75,
            "Spot Up Shot Three": 82,
            "Shot Mid-Range": 70,
            "Roll vs Pop": 25,  # Prefers to pop
            "Post Up": 50,
            "Block Shot": 70,
            "Crash": 55,
            "Pass to Open Man": 65,
        },
        "badge_priorities": {
            "Outside Scoring": ["Catch and Shoot", "Corner Specialist",
                                 "Stop and Pop", "Deadeye"],
            "Inside Scoring": ["Backdown Punisher", "Deep Hooks", "Post Fade Phenom"],
            "Rebounding": ["Glass Cleaner", "Power Rebounder"],
            "Defending": ["Rim Protector", "Pogo Stick"],
        },
        "bust_profile": {
            "Defensive Consistency": (-18, -12),
            "Agility": (-15, -10),
        },
    },
}

# Convenience list of all archetype names
ARCHETYPE_NAMES = list(ARCHETYPES.keys())

# Maps positions to archetypes that naturally fit them
POSITION_ARCHETYPE_MAP = {
    "PG": ["Iso Creator", "Movement Shooter"],
    "SG": ["Movement Shooter", "Iso Creator", "Two-Way Wing", "Defensive Connector", "Slashing Forward"],
    "SF": ["Two-Way Wing", "Slashing Forward", "Defensive Connector", "Movement Shooter", "Stretch Big"],
    "PF": ["Stretch Big", "Slashing Forward", "Rim Running Big", "Playmaking Big", "Defensive Connector"],
    "C":  ["Rim Running Big", "Playmaking Big", "Stretch Big"],
}
