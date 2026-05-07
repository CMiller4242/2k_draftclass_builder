"""
All NBA 2K attribute, tendency, and mental fields.
These are used across the generation engine to ensure completeness.
"""

# ---------------------------------------------------------------------------
# ATTRIBUTES
# ---------------------------------------------------------------------------

MISC_ATTRIBUTES = [
    "Intangibles",
    "Potential",
]

OFFENSIVE_ATTRIBUTES = [
    "Driving Layup",
    "Post Fade",
    "Post Hook",
    "Post Control",
    "Draw Foul",
    "Close Shot",
    "Mid Range Shot",
    "Three Point Shot",
    "Free Throw",
    "Ball Handle",
    "Pass IQ",
    "Pass Accuracy",
    "Offensive Rebound",
    "Standing Dunk",
    "Driving Dunk",
    "Shot IQ",
    "Pass Vision",
    "Hands",
]

DEFENSIVE_ATTRIBUTES = [
    "Defensive Rebound",
    "Interior Defense",
    "Perimeter Defense",
    "Block",
    "Steal",
]

ATHLETICISM_ATTRIBUTES = [
    "Speed",
    "Speed With Ball",
    "Vertical",
    "Strength",
    "Stamina",
    "Hustle",
    "Agility",
]

DURABILITY_ATTRIBUTES = [
    "Head Durability",
    "Neck Durability",
    "Back Durability",
    "Left Shoulder Durability",
    "Right Shoulder Durability",
    "Left Elbow Durability",
    "Right Elbow Durability",
    "Left Hip Durability",
    "Right Hip Durability",
    "Left Knee Durability",
    "Right Knee Durability",
    "Left Ankle Durability",
    "Right Ankle Durability",
    "Left Foot Durability",
    "Right Foot Durability",
    "Miscellaneous Durability",
]

MENTAL_ATTRIBUTES = [
    "Pass Perception",
    "Defensive Consistency",
    "Help Defense IQ",
    "Offensive Consistency",
]

ALL_ATTRIBUTES = (
    MISC_ATTRIBUTES
    + OFFENSIVE_ATTRIBUTES
    + DEFENSIVE_ATTRIBUTES
    + ATHLETICISM_ATTRIBUTES
    + DURABILITY_ATTRIBUTES
    + MENTAL_ATTRIBUTES
)

ATTRIBUTE_CATEGORIES = {
    "Misc": MISC_ATTRIBUTES,
    "Offensive": OFFENSIVE_ATTRIBUTES,
    "Defensive": DEFENSIVE_ATTRIBUTES,
    "Athleticism": ATHLETICISM_ATTRIBUTES,
    "Durability": DURABILITY_ATTRIBUTES,
    "Mental": MENTAL_ATTRIBUTES,
}

# ---------------------------------------------------------------------------
# TENDENCIES
# ---------------------------------------------------------------------------

JUMP_SHOOTING_TENDENCIES = [
    "Step Through Shot",
    "Shot Under Basket",
    "Shot Close",
    "Shot Close Left",
    "Shot Close Middle",
    "Shot Close Right",
    "Shot Mid-Range",
    "Spot Up Shot Mid-Range",
    "Off Screen Shot Mid-Range",
    "Shot Mid Left",
    "Shot Mid Left-Center",
    "Shot Mid Center",
    "Shot Mid Right-Center",
    "Shot Mid Right",
    "Shot Three",
    "Spot Up Shot Three",
    "Off Screen Shot Three",
    "Shot Three Left",
    "Shot Three Left-Center",
    "Shot Three Center",
    "Shot Three Right-Center",
    "Shot Three Right",
    "Contested Jumper Three",
    "Contested Jumper Mid-Range",
    "Stepback Jumper Three",
    "Stepback Jumper Mid-Range",
    "Spin Jumper",
    "Transition Pull-Up Three",
    "Drive Pull Up Three",
    "Drive Pull Up Mid-Range",
    "Use Glass",
]

LAYUP_DUNK_TENDENCIES = [
    "Driving Layup",
    "Standing Dunk",
    "Driving Dunk",
    "Flashy Dunk",
    "Alley-Oop",
    "Putback",
    "Crash",
    "Spin Layup",
    "Hop Step Layup",
    "Euro Step Layup",
    "Floater",
]

DRIVE_SETUP_TENDENCIES = [
    "Triple Threat Pump Fake",
    "Triple Threat Jab Step",
    "Triple Threat Idle",
    "Triple Threat Shoot",
    "Setup With Sizeup",
    "Setup With Hesitation",
    "No Setup Dribble",
]

DRIVING_TENDENCIES = [
    "Drive",
    "Spot Up Drive",
    "Off Screen Drive",
    "Drive Right",
    "Driving Crossover",
    "Driving Spin",
    "Driving Step Back",
    "Driving Half Spin",
    "Driving Double Crossover",
    "Driving Behind the Back",
    "Driving Dribble Hesitation",
    "Driving In and Out",
    "No Driving Dribble Move",
    "Attack Strong on Drive",
]

PASSING_TENDENCIES = [
    "Pass to Open Man",
    "Flashy Pass",
    "Alley-Oop Pass",
]

POST_GAME_TENDENCIES = [
    "Post Up",
    "Post Shimmy Shot",
    "Post Face Up",
    "Post Back Down",
    "Post Aggressive Back Down",
    "Shoot From Post",
    "Post Hook Left",
    "Post Hook Right",
    "Post Fade Left",
    "Post Fade Right",
    "Post Up and Under",
    "Post Hop Shot",
    "Post Step Back Shot",
    "Post Drive",
    "Post Spin",
    "Post Drop Step",
    "Post Hop Step",
]

FREELANCE_TENDENCIES = [
    "Shot",
    "Touches",
    "Roll vs Pop",
    "Transition Spot Up",
    "Iso vs Elite Defender",
    "Iso vs Good Defender",
    "Iso vs Average Defender",
    "Iso vs Poor Defender",
    "Play Discipline",
]

DEFENSE_TENDENCIES = [
    "Pass Interception",
    "Take Charge",
    "On-Ball Steal",
    "Contest Shot",
    "Block Shot",
    "Foul",
    "Hard Foul",
]

ALL_TENDENCIES = (
    JUMP_SHOOTING_TENDENCIES
    + LAYUP_DUNK_TENDENCIES
    + DRIVE_SETUP_TENDENCIES
    + DRIVING_TENDENCIES
    + PASSING_TENDENCIES
    + POST_GAME_TENDENCIES
    + FREELANCE_TENDENCIES
    + DEFENSE_TENDENCIES
)

TENDENCY_CATEGORIES = {
    "Jump Shooting": JUMP_SHOOTING_TENDENCIES,
    "Layups and Dunks": LAYUP_DUNK_TENDENCIES,
    "Drive Setup": DRIVE_SETUP_TENDENCIES,
    "Driving": DRIVING_TENDENCIES,
    "Passing": PASSING_TENDENCIES,
    "Post Game": POST_GAME_TENDENCIES,
    "Freelance": FREELANCE_TENDENCIES,
    "Defense": DEFENSE_TENDENCIES,
}

# ---------------------------------------------------------------------------
# BADGE LEVELS
# ---------------------------------------------------------------------------

BADGE_LEVELS = ["None", "Bronze", "Silver", "Gold", "Hall of Fame", "Legend"]

# ---------------------------------------------------------------------------
# BADGE CATEGORIES AND BADGES
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 2K26 BADGE LISTS (exact in-game CAP menu order, no cross-category duplicates)
# ---------------------------------------------------------------------------

PERSONALITY_BADGES = [
    "Reserved",
    "Friendly",
    "Team Player",
    "Extremely Confident",
    "Keep It Real",
    "Pat My Back",
    "Expressive",
    "Unpredictable",
    "Laid Back",
    "Media Ringmaster",
    "Warm Weather Fan",
    "Finance Savvy",
    "Alpha Dog",
    "Enforcer",
    "Work Ethic",
    "Marketability",
]

INSIDE_SCORING_BADGES = [
    "Float Game",
    "Posterizer",
    "Rise Up",
    "Aerial Wizard",
    "Hook Specialist",
    "Layup Mixmaster",
    "Paint Prodigy",
    "Physical Finisher",
    "Post Powerhouse",
    "Post-Up Poet",
]

OUTSIDE_SCORING_BADGES = [
    "Post Fade Phenom",
    "Deadeye",
    "Limitless Range",
    "Slippery Off-Ball",
    "Mini Marksman",
    "Set Shot Specialist",
    "Shifty Shooter",
]

PLAYMAKING_BADGES = [
    "Bail Out",
    "Break Starter",
    "Dimer",
    "Handles For Days",
    "Unpluckable",
    "Versatile Visionary",
    "Ankle Assassin",
    "Lightning Launch",
    "Strong Handle",
]

DEFENDING_BADGES = [
    "Post Lockdown",
    "Challenger",
    "Off-Ball Pest",
    "Pick Dodger",
    "Glove",
    "Interceptor",
    "Pogo Stick",
    "On-Ball Menace",
    "High-Flying Denier",
    "Paint Patroller",
]

ATHLETICISM_BADGES = [
    "Brick Wall",
    "Immovable Enforcer",
]

REBOUNDING_BADGES = [
    "Boxout Beast",
    "Rebound Chaser",
]

ALL_BADGES = {
    "Personality": PERSONALITY_BADGES,
    "Inside Scoring": INSIDE_SCORING_BADGES,
    "Outside Scoring": OUTSIDE_SCORING_BADGES,
    "Playmaking": PLAYMAKING_BADGES,
    "Defending": DEFENDING_BADGES,
    "Athleticism": ATHLETICISM_BADGES,
    "Rebounding": REBOUNDING_BADGES,
}

# Positions
POSITIONS = ["PG", "SG", "SF", "PF", "C"]
POSITION_COMBOS = [
    "PG", "SG", "SF", "PF", "C",
    "PG/SG", "SG/PG", "SG/SF", "SF/SG", "SF/PF", "PF/SF", "PF/C", "C/PF",
]
