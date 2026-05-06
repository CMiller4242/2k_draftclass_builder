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

PERSONALITY_BADGES = [
    "Adrenaline Rush",
    "Brick Wall",
    "Bruiser",
    "Claymore",
    "Comeback Kid",
    "Competitor",
    "Floor General",
    "Grease Lightning",
    "Heart of Gold",
    "Hot Zone Hunter",
    "Interceptor",
    "Iron Will",
    "Killer Instinct",
    "Large and In Charge",
    "Momentum Shifter",
    "Quick Study",
    "Resilience",
    "Solid Foundation",
    "Spark Plug",
    "Steadfast",
    "Team Ace",
    "Temperament",
    "Thriller",
    "Torch Bearer",
    "Winner",
]

INSIDE_SCORING_BADGES = [
    "Acrobat",
    "And-1 Threat",
    "Backdown Punisher",
    "Bully",
    "Contact Finisher",
    "Corner Pocket",
    "Deep Hooks",
    "Dream Shake",
    "Dropstepper",
    "Float Game",
    "Giant Slayer",
    "Layup Mixmaster",
    "Paint Prodigy",       # 2K26 — paint scoring efficiency
    "Physical Finisher",   # 2K26 — contact finishing through traffic
    "Post Fade Phenom",
    "Post Powerhouse",     # 2K26 — dominant post-up scoring
    "Post Spin Technician",
    "Posterizer",          # 2K26 — poster dunk specialist
    "Pro Touch",
    "Putback Artist",
    "Rise Up",
    "Slithery Finisher",
    "Tear Dropper",
    "Up and Under",
]

OUTSIDE_SCORING_BADGES = [
    "Catch and Shoot",
    "Clutch Shooter",
    "Corner Specialist",
    "Deadeye",
    "Deep Fades",
    "Green Machine",
    "Limitless Range",
    "Mismatch Expert",
    "Off-Ball Pest",
    "Pull-Up Precision",
    "Quick Draw",
    "Rhythm Shooter",
    "Set Shot Specialist",  # 2K26 — stationary/spot-up shooting
    "Shifty Shooter",       # 2K26 — self-created pull-up shooting
    "Shimmy Shooter",
    "Slippery Off-Ball",
    "Space Creator",
    "Stop and Pop",
    "Volume Shooter",
]

PLAYMAKING_BADGES = [
    "Ankle Assassin",
    "Break Starter",
    "Chef",
    "Clamp Breaker",
    "Dimer",                # 2K26 — elite passing and assist generation
    "Downhill",
    "Dream Shaker",
    "Dribble Weave",
    "Handles for Days",
    "Hyperdrive",
    "Killer Combos",
    "Last Chance Passer",
    "Lob City Passer",
    "Needle Threader",
    "Pace Setter",
    "Pick and Roll Maestro",
    "Playmaker",
    "Post Playmaker",
    "Quick First Step",
    "Special Delivery",
    "Stop and Go",
    "Unpluckable",
    "Versatile Visionary",  # 2K26 — decision-making in multiple offensive roles
    "Versatilist",
]

DEFENDING_BADGES = [
    "Box",
    "Brick Wall",
    "Challenger",
    "Clamps",
    "Crowd Control",
    "Defensive Leader",
    "Defensive Stopper",
    "Disruption",
    "Fast Feet",
    "Glove",
    "Guard Up",
    "Hard Foul",
    "High-Flying Denier",  # 2K26 — contesting above-the-rim attempts
    "High-Low Detective",
    "Intimidator",
    "Menace",
    "On-Ball Menace",      # 2K26 — sustained on-ball defensive pressure
    "Pick Dodger",         # 2K26 — navigating screens on defense
    "Pogo Stick",
    "Rim Protector",
    "Shot Contester",
    "Sweep the Leg",
    "Tireless Defender",
    "Trapper",
]

ATHLETICISM_BADGES = [
    "Acrobat",
    "Aerial Wizard",
    "Agility Booster",
    "Chase Down Artist",
    "Coiled Spring",
    "Fast Twitch",
    "Freight Train",
    "High Flyer",
    "Jump Starter",
    "Lightning Launch",
    "Mouse in the House",
    "Pace Setter",
    "Physical Specimen",
    "Physical Toughness",
    "Power Mover",
    "Speed Booster",
    "Traction",
]

REBOUNDING_BADGES = [
    "Aerial Wizard",
    "Boxout Beast",        # 2K26 — body positioning for rebounding
    "Brick Wall",
    "Corner Pocket",
    "Crash",
    "Exhibition",
    "Glass Cleaner",
    "Glue Hands",
    "High-Low Detective",
    "Hustle Rebounder",
    "Long Range Rebound",
    "Mega Patron",
    "Post Move Lockdown",
    "Power Rebounder",
    "Putback Artist",
    "Rebound Chaser",
    "Sky Walker",
    "Strong Handle",
    "Worm",
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
