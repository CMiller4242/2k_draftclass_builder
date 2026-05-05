"""
Scouting report and entry notes generation.

Produces human-readable text for each player based on their stats,
tier, archetype, and bust status. These are the narrative fields that
make the output feel like real scouting.
"""

import random
from data.archetypes import ARCHETYPES


def generate_scouting_summary(player: dict) -> str:
    """Generate a 2–3 sentence scouting summary for a player."""
    archetype = player["archetype"]
    tier = player["tier"]
    is_bust = player["is_bust"]
    attrs = player["attributes"]
    name = player["name"]
    pos = player["position"]
    height = player["height_display"]

    archetype_data = ARCHETYPES.get(archetype, {})
    desc = archetype_data.get("description", "")

    # Opening line — physical/positional
    openers = [
        f"{name} is a {height} {pos} who projects as a {player['projected_role'].lower()}.",
        f"At {height}, {name} profiles as a {archetype.lower()} with {player['projected_role'].lower()} upside.",
        f"{name} ({pos}, {height}) enters the draft as a classic {archetype.lower()}.",
    ]
    opening = random.choice(openers)

    # Middle — key strengths
    strength_lines = _build_strength_line(archetype, attrs, tier)

    # Closing — outlook or concern
    if is_bust:
        concerns = [
            f"However, concerns about {_random_concern(archetype)} may limit his ceiling.",
            f"Questions remain about his ability to translate {_bust_worry()} to the next level.",
            f"Despite his tools, scouts worry his {_random_concern(archetype)} may hold him back.",
        ]
        closing = random.choice(concerns)
    else:
        optimism = [
            f"His {_random_strength(archetype)} gives him a clear path to a long NBA career.",
            f"Projects as a {player['development_outlook'].lower()} who should contribute quickly.",
            f"Scouts love his {_random_strength(archetype)} and see him as a {player['projected_role'].lower()}.",
        ]
        closing = random.choice(optimism)

    return f"{opening} {strength_lines} {closing}"


def generate_development_notes(player: dict) -> str:
    """Generate development outlook notes."""
    tier = player["tier"]
    is_bust = player["is_bust"]
    outlook = player["development_outlook"]

    notes_by_tier = {
        1: [
            "Ready to contribute from Day 1. Should be a franchise centerpiece within 2–3 seasons.",
            "Elite ceiling. Will need a system that maximizes his strengths. Star-level producer.",
            "Top prospect with multiple All-Star appearances in his future if development stays on track.",
        ],
        2: [
            "Solid starter from Year 1. Projects as a reliable second or third option.",
            "Good starter with All-Star upside if he continues to develop his secondary skills.",
            "Should anchor a rotation immediately. Ceiling of high-end starter to borderline All-Star.",
        ],
        3: [
            "Rotation player from early in his career. Will need a defined role to thrive.",
            "Quality contributor. Fits best in a system that uses his strengths specifically.",
            "Starter potential if given time. More likely a quality rotation piece long-term.",
        ],
        4: [
            "Fringe roster player. Will need to find a niche to stick in the league.",
            "Two-way contract candidate. Needs to prove himself in the G League first.",
            "Long-term project. Raw athleticism/skills but years away from contributing.",
        ],
    }

    if is_bust:
        return (
            f"BUST ALERT: Despite the tools, this prospect has shown a pattern of "
            f"underperformance. High paper potential does not guarantee success. "
            f"Recommended: low-risk contract, defined minutes role, strong coaching staff."
        )

    base = random.choice(notes_by_tier.get(tier, notes_by_tier[3]))
    return f"[{outlook}] {base}"


def generate_2k_entry_notes(player: dict) -> str:
    """Generate suggested notes for manually entering this player into 2K."""
    arch = player["archetype"]
    pos = player["position"]
    attrs = player["attributes"]
    height = player["height_display"]
    weight = player["weight_lbs"]

    top_attrs = _top_attributes(attrs, n=4)
    top_attr_str = ", ".join(top_attrs)

    badge_highlights = _top_badges(player.get("badges", {}), n=3)
    badge_str = ", ".join(f"{b} ({l})" for b, l in badge_highlights)

    lines = [
        f"Position: {pos} | Height: {height} | Weight: {weight} lbs",
        f"Archetype: {arch}",
        f"Key Attributes to Set High: {top_attr_str}",
    ]
    if badge_str:
        lines.append(f"Priority Badges: {badge_str}")
    lines.append(
        f"Tip: Set Potential to {attrs.get('Potential', '??')} before simulating seasons."
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _build_strength_line(archetype: str, attrs: dict, tier: int) -> str:
    """Build a sentence describing the player's primary strengths."""
    strength_phrases = {
        # Original 8
        "Movement Shooter":   "His elite shooting mechanics and off-ball movement make him a constant threat.",
        "Iso Creator":        "His ball-handling and pull-up game allow him to create shots for himself and others.",
        "Two-Way Wing":       "He brings elite defensive versatility while providing enough offense to demand respect.",
        "Rim Running Big":    "He dominates above the rim as a lob threat and interior force.",
        "Playmaking Big":     "His vision and passing ability at the center position is genuinely rare.",
        "Slashing Forward":   "His explosiveness and finishing ability in traffic set him apart.",
        "Defensive Connector": "His defensive IQ and communication make every team better.",
        "Stretch Big":        "His combination of size and shooting range is a matchup nightmare for opposing bigs.",
        # New 10
        "3-Level Scorer":        "He can hurt defenses at all three levels, making him impossible to consistently contain.",
        "Shot Hunter":           "His ability to create and drain pull-up jumpers off the dribble is elite.",
        "Mid-Range Specialist":  "The mid-range is his office — he commands the 15-to-20-foot area better than anyone.",
        "High Flyer":            "His above-the-rim athleticism is a legitimate weapon that changes how opponents defend.",
        "Glass Cleaner":         "He dominates the glass on both ends — second-chance points are his specialty.",
        "Paint Bully":           "His strength and physicality in the post make him nearly impossible to front or move.",
        "Break Starter":         "His outlet passing and vision from the high post triggers some of the best fast breaks in the class.",
        "Lockdown Guard":        "His on-ball defense and anticipation are elite — he makes opposing guards miserable.",
        "Putback Finisher":      "He crashes relentlessly and converts around the rim with outstanding timing and athleticism.",
        "Inside-Out Scorer":     "His combination of rim pressure and three-point range keeps defenses completely off-balance.",
    }
    return strength_phrases.get(archetype, "He brings a unique skill set to the court.")


def _random_strength(archetype: str) -> str:
    strength_map = {
        "Movement Shooter":   "shooting mechanics",
        "Iso Creator":        "creation ability",
        "Two-Way Wing":       "defensive versatility",
        "Rim Running Big":    "athleticism and rim pressure",
        "Playmaking Big":     "vision and passing",
        "Slashing Forward":   "explosiveness",
        "Defensive Connector": "defensive IQ",
        "Stretch Big":        "floor-spacing ability",
        "3-Level Scorer":     "multi-level scoring threat",
        "Shot Hunter":        "pull-up shot creation",
        "Mid-Range Specialist": "mid-range mastery",
        "High Flyer":         "above-the-rim athleticism",
        "Glass Cleaner":      "rebounding dominance",
        "Paint Bully":        "physical interior presence",
        "Break Starter":      "transition-triggering passing",
        "Lockdown Guard":     "on-ball defensive intensity",
        "Putback Finisher":   "offensive rebounding and putback ability",
        "Inside-Out Scorer":  "inside-out scoring versatility",
    }
    return strength_map.get(archetype, "basketball IQ")


def _random_concern(archetype: str) -> str:
    concern_map = {
        "Movement Shooter":   "shot selection",
        "Iso Creator":        "decision-making",
        "Two-Way Wing":       "offensive consistency",
        "Rim Running Big":    "free throw shooting",
        "Playmaking Big":     "defensive effort",
        "Slashing Forward":   "outside shooting",
        "Defensive Connector": "offensive impact",
        "Stretch Big":        "lateral mobility",
        "3-Level Scorer":     "consistency across all three zones",
        "Shot Hunter":        "shot volume and selectivity",
        "Mid-Range Specialist": "range limitations against drop coverage",
        "High Flyer":         "half-court offensive IQ",
        "Glass Cleaner":      "free throw shooting",
        "Paint Bully":        "mobility against modern switching defenses",
        "Break Starter":      "half-court offensive impact",
        "Lockdown Guard":     "offensive creation",
        "Putback Finisher":   "positional versatility",
        "Inside-Out Scorer":  "shot consistency from both zones",
    }
    return concern_map.get(archetype, "consistency")


def _bust_worry() -> str:
    worries = [
        "his physical tools",
        "his college production",
        "his athleticism",
        "his raw upside",
    ]
    return random.choice(worries)


def _top_attributes(attrs: dict, n: int = 4) -> list:
    """Return the names of the top N attributes by value, excluding Potential."""
    filtered = {k: v for k, v in attrs.items() if k != "Potential" and "Durability" not in k}
    sorted_attrs = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    return [a[0] for a in sorted_attrs[:n]]


def _top_badges(badges: dict, n: int = 3) -> list:
    """Return (badge_name, level) for the top N non-None badges by level."""
    level_order = {"Legend": 5, "Hall of Fame": 4, "Gold": 3, "Silver": 2, "Bronze": 1, "None": 0}
    ranked = [(b, l) for b, l in badges.items() if l != "None"]
    ranked.sort(key=lambda x: level_order.get(x[1], 0), reverse=True)
    return ranked[:n]
