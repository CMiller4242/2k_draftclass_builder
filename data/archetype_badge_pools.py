"""
Per-archetype badge pools used by the budgeted badge allocator.

Each archetype maps to:
  - primary:   badges that fit the archetype's identity (highest weight)
  - secondary: situational complements (medium weight)
  - rare:      badges that occasionally appear when attributes support them
  - avoid:     badges that should NEVER appear regardless of attribute eligibility

The allocator pulls candidate badges from primary/secondary/rare with weighted
sampling, then validates each against attribute eligibility. Any badge in the
avoid list is filtered out at the candidate stage. Anything not listed is
treated as low-probability noise (Bronze cap).
"""

from typing import Dict, List

ARCHETYPE_BADGE_POOLS: Dict[str, Dict[str, List[str]]] = {
    "Movement Shooter": {
        "primary":   ["Set Shot Specialist", "Shifty Shooter", "Deadeye", "Slippery Off-Ball"],
        "secondary": ["Limitless Range", "Mini Marksman", "Lightning Launch", "Off-Ball Pest"],
        "rare":      ["Dimer", "Bail Out", "Challenger"],
        "avoid":     [
            "Post Powerhouse", "Post-Up Poet", "Post Lockdown", "Hook Specialist",
            "Paint Patroller", "Brick Wall", "Rise Up", "Aerial Wizard",
            "Boxout Beast", "Rebound Chaser", "Paint Prodigy", "Posterizer",
            "Immovable Enforcer", "Post Fade Phenom",
        ],
    },
    "Iso Creator": {
        "primary":   ["Handles For Days", "Ankle Assassin", "Lightning Launch",
                      "Unpluckable", "Shifty Shooter"],
        "secondary": ["Deadeye", "Mini Marksman", "Strong Handle",
                      "Bail Out", "Physical Finisher"],
        "rare":      ["Dimer", "Set Shot Specialist", "Layup Mixmaster"],
        "avoid":     [
            "Boxout Beast", "Rebound Chaser", "Paint Patroller", "Post Lockdown",
            "Post Powerhouse", "Post-Up Poet", "Hook Specialist", "Brick Wall",
            "Paint Prodigy", "Rise Up", "Aerial Wizard", "Posterizer",
            "Immovable Enforcer",
        ],
    },
    "Two-Way Wing": {
        "primary":   ["Challenger", "On-Ball Menace", "Interceptor", "Off-Ball Pest"],
        "secondary": ["Set Shot Specialist", "Deadeye", "Physical Finisher",
                      "Posterizer", "Glove"],
        "rare":      ["Dimer", "Slippery Off-Ball", "Rebound Chaser"],
        "avoid":     [
            "Post Powerhouse", "Post-Up Poet", "Hook Specialist", "Post Lockdown",
            "Paint Patroller", "Brick Wall", "Immovable Enforcer", "Post Fade Phenom",
        ],
    },
    "Rim Running Big": {
        "primary":   ["Aerial Wizard", "Rise Up", "Paint Prodigy",
                      "Rebound Chaser", "Boxout Beast"],
        "secondary": ["Posterizer", "Physical Finisher", "High-Flying Denier",
                      "Brick Wall", "Pogo Stick"],
        "rare":      ["Post Lockdown", "Paint Patroller", "Break Starter"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Mini Marksman", "Shifty Shooter",
            "Set Shot Specialist", "Handles For Days", "Ankle Assassin",
            "Lightning Launch", "Unpluckable", "Strong Handle", "Slippery Off-Ball",
        ],
    },
    "Playmaking Big": {
        "primary":   ["Dimer", "Break Starter", "Versatile Visionary", "Post-Up Poet"],
        "secondary": ["Paint Prodigy", "Post Powerhouse", "Brick Wall",
                      "Rebound Chaser", "Bail Out"],
        "rare":      ["Set Shot Specialist", "Post Fade Phenom", "High-Flying Denier"],
        "avoid":     [
            "Limitless Range", "Mini Marksman", "Shifty Shooter",
            "Handles For Days", "Ankle Assassin", "Lightning Launch",
            "Unpluckable", "Slippery Off-Ball",
        ],
    },
    "Slashing Forward": {
        "primary":   ["Posterizer", "Aerial Wizard", "Physical Finisher", "Layup Mixmaster"],
        "secondary": ["Lightning Launch", "Strong Handle", "Slippery Off-Ball",
                      "Challenger", "High-Flying Denier"],
        "rare":      ["Set Shot Specialist", "Rebound Chaser", "Off-Ball Pest"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Post Powerhouse", "Post-Up Poet",
            "Post Lockdown", "Hook Specialist", "Paint Patroller", "Post Fade Phenom",
            "Brick Wall", "Immovable Enforcer",
        ],
    },
    "Defensive Connector": {
        "primary":   ["Interceptor", "Off-Ball Pest", "Challenger",
                      "High-Flying Denier", "Paint Patroller"],
        "secondary": ["Rebound Chaser", "Boxout Beast", "Brick Wall",
                      "Dimer", "Versatile Visionary"],
        "rare":      ["Set Shot Specialist", "Physical Finisher"],
        "avoid":     [
            "Limitless Range", "Ankle Assassin", "Handles For Days",
            "Mini Marksman", "Post Powerhouse", "Post-Up Poet",
            "Hook Specialist", "Post Fade Phenom",
        ],
    },
    "Stretch Big": {
        "primary":   ["Set Shot Specialist", "Deadeye", "Limitless Range", "Rebound Chaser"],
        "secondary": ["Brick Wall", "Boxout Beast", "Paint Patroller",
                      "Post Lockdown", "Pogo Stick"],
        "rare":      ["Dimer", "Break Starter", "Post Fade Phenom"],
        "avoid":     [
            "Handles For Days", "Ankle Assassin", "Lightning Launch",
            "Unpluckable", "Slippery Off-Ball", "Mini Marksman",
        ],
    },
    "3-Level Scorer": {
        "primary":   ["Deadeye", "Shifty Shooter", "Set Shot Specialist",
                      "Layup Mixmaster", "Physical Finisher"],
        "secondary": ["Posterizer", "Lightning Launch", "Unpluckable",
                      "Mini Marksman", "Bail Out"],
        "rare":      ["Challenger", "Slippery Off-Ball", "Dimer"],
        "avoid":     [
            "Boxout Beast", "Rebound Chaser", "Paint Patroller", "Post Lockdown",
            "Post Powerhouse", "Post-Up Poet", "Hook Specialist", "Brick Wall",
            "Paint Prodigy",
        ],
    },
    "Shot Hunter": {
        "primary":   ["Shifty Shooter", "Deadeye", "Limitless Range", "Handles For Days"],
        "secondary": ["Ankle Assassin", "Lightning Launch", "Unpluckable",
                      "Set Shot Specialist", "Mini Marksman"],
        "rare":      ["Bail Out", "Dimer", "Slippery Off-Ball"],
        "avoid":     [
            "Boxout Beast", "Rebound Chaser", "Paint Patroller", "Post Lockdown",
            "Post Powerhouse", "Post-Up Poet", "Hook Specialist", "Brick Wall",
            "Paint Prodigy", "Aerial Wizard", "Rise Up", "Posterizer",
            "Immovable Enforcer", "Post Fade Phenom",
        ],
    },
    "Mid-Range Specialist": {
        "primary":   ["Deadeye", "Shifty Shooter", "Set Shot Specialist", "Post Fade Phenom"],
        "secondary": ["Mini Marksman", "Float Game", "Physical Finisher",
                      "Unpluckable", "Bail Out"],
        "rare":      ["Dimer", "Challenger", "Slippery Off-Ball"],
        "avoid":     [
            "Limitless Range",
            "Boxout Beast", "Rebound Chaser", "Paint Patroller", "Post Lockdown",
            "Post Powerhouse", "Brick Wall", "Aerial Wizard", "Rise Up",
            "Immovable Enforcer",
        ],
    },
    "High Flyer": {
        "primary":   ["Posterizer", "Aerial Wizard", "Physical Finisher", "Layup Mixmaster"],
        "secondary": ["Pogo Stick", "High-Flying Denier", "Lightning Launch",
                      "Slippery Off-Ball", "Rise Up"],
        "rare":      ["Challenger", "Rebound Chaser", "Set Shot Specialist"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Mini Marksman", "Shifty Shooter",
            "Post Powerhouse", "Post-Up Poet", "Post Lockdown",
            "Hook Specialist", "Paint Patroller", "Post Fade Phenom",
            "Versatile Visionary", "Dimer", "Break Starter", "Bail Out",
            "Handles For Days", "Ankle Assassin", "Unpluckable",
            "Brick Wall", "Immovable Enforcer",
        ],
    },
    "Glass Cleaner": {
        "primary":   ["Rebound Chaser", "Boxout Beast", "Brick Wall"],
        "secondary": ["Paint Patroller", "Post Lockdown", "High-Flying Denier",
                      "Pogo Stick", "Rise Up"],
        "rare":      ["Paint Prodigy", "Break Starter", "Aerial Wizard"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Mini Marksman", "Shifty Shooter",
            "Set Shot Specialist", "Handles For Days", "Ankle Assassin",
            "Lightning Launch", "Unpluckable", "Strong Handle",
            "Slippery Off-Ball", "Post Fade Phenom",
        ],
    },
    "Paint Bully": {
        "primary":   ["Post Powerhouse", "Post-Up Poet", "Paint Prodigy",
                      "Physical Finisher", "Rise Up"],
        "secondary": ["Hook Specialist", "Brick Wall", "Boxout Beast",
                      "Rebound Chaser", "Post Lockdown"],
        "rare":      ["Aerial Wizard", "High-Flying Denier", "Dimer"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Mini Marksman", "Shifty Shooter",
            "Set Shot Specialist", "Handles For Days", "Ankle Assassin",
            "Lightning Launch", "Unpluckable", "Slippery Off-Ball",
        ],
    },
    "Break Starter": {
        "primary":   ["Break Starter", "Dimer", "Versatile Visionary", "Rebound Chaser"],
        "secondary": ["Boxout Beast", "Brick Wall", "Post Lockdown",
                      "Paint Patroller", "Bail Out"],
        "rare":      ["Set Shot Specialist", "Post Fade Phenom", "High-Flying Denier"],
        "avoid":     [
            "Limitless Range", "Mini Marksman", "Shifty Shooter",
            "Handles For Days", "Ankle Assassin", "Lightning Launch",
            "Unpluckable", "Slippery Off-Ball",
        ],
    },
    "Lockdown Guard": {
        "primary":   ["On-Ball Menace", "Challenger", "Pick Dodger", "Glove", "Interceptor"],
        "secondary": ["Off-Ball Pest", "Immovable Enforcer", "Lightning Launch", "Unpluckable"],
        "rare":      ["Set Shot Specialist", "Dimer", "Slippery Off-Ball"],
        "avoid":     [
            "Limitless Range", "Mini Marksman", "Post Powerhouse", "Post-Up Poet",
            "Hook Specialist", "Paint Patroller", "Post Lockdown", "Brick Wall",
            "Boxout Beast", "Rebound Chaser", "Aerial Wizard", "Rise Up",
            "Posterizer", "Paint Prodigy", "Post Fade Phenom",
        ],
    },
    "Putback Finisher": {
        "primary":   ["Aerial Wizard", "Rise Up", "Rebound Chaser",
                      "Boxout Beast", "Paint Prodigy"],
        "secondary": ["Physical Finisher", "Pogo Stick", "High-Flying Denier", "Brick Wall"],
        "rare":      ["Post Lockdown", "Posterizer", "Break Starter"],
        "avoid":     [
            "Limitless Range", "Deadeye", "Mini Marksman", "Shifty Shooter",
            "Set Shot Specialist", "Handles For Days", "Ankle Assassin",
            "Lightning Launch", "Unpluckable", "Slippery Off-Ball",
            "Post Fade Phenom",
        ],
    },
    "Inside-Out Scorer": {
        "primary":   ["Paint Prodigy", "Physical Finisher", "Set Shot Specialist", "Deadeye"],
        "secondary": ["Post Fade Phenom", "Post-Up Poet", "Limitless Range",
                      "Layup Mixmaster", "Brick Wall"],
        "rare":      ["Dimer", "Rebound Chaser", "Challenger"],
        "avoid":     [
            "Mini Marksman", "Slippery Off-Ball", "Ankle Assassin",
            "Handles For Days", "Lightning Launch",
        ],
    },
}


def get_pool(archetype_name: str) -> Dict[str, List[str]]:
    """Return the badge pool dict for an archetype, with empty lists as default."""
    return ARCHETYPE_BADGE_POOLS.get(archetype_name, {
        "primary": [], "secondary": [], "rare": [], "avoid": [],
    })
