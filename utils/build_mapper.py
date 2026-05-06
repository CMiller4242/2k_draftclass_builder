"""
Build name → archetype mapping system.

Parses the 2K Labs Excel file, extracts unique build names, and maps each
name to one or more of our archetype templates using keyword rules.

Design:
  - KEYWORD_ARCHETYPE_MAP:  edit this to tune or extend mapping coverage
  - Keywords are matched case-insensitively as substrings of the build name
  - A build name can match multiple keywords → multiple archetypes
  - Build names with zero matches go into the "unmapped" bucket for review
  - Loading the Excel file is lazy/cached so it's fast on repeated calls

To add new keywords:
  Add an entry to KEYWORD_ARCHETYPE_MAP.  The key is a substring to search
  for (case-insensitive); the value is the list of archetypes it implies.

To add a new archetype:
  1. Add it to data/archetypes.py first.
  2. Then add keyword entries here that point to it.
"""

import os
from functools import lru_cache
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# KEYWORD → ARCHETYPE(S) MAP
# ---------------------------------------------------------------------------
# Keys are matched as case-insensitive substrings inside build names.
# Values are lists of archetype names (must match keys in data/archetypes.ARCHETYPES).
#
# Ordering note: all keywords are tested against every build name; a name
# collects every archetype whose keyword appears in it.  Longer / more
# specific entries shadow nothing — they simply add more archetypes.
# ---------------------------------------------------------------------------

KEYWORD_ARCHETYPE_MAP: dict[str, list[str]] = {

    # ── Two-Way Wing ─────────────────────────────────────────────────────────
    "2-Way":             ["Two-Way Wing"],
    "Two Way":           ["Two-Way Wing"],
    "3 & D":             ["Two-Way Wing", "Movement Shooter"],
    "Dual Finisher":     ["Two-Way Wing", "Slashing Forward"],
    "PlaySlash":         ["Two-Way Wing", "Slashing Forward"],
    "PlaySlaSh":         ["Two-Way Wing", "Slashing Forward"],
    "Switch-Defending":  ["Two-Way Wing"],
    "Wing Runner":       ["Two-Way Wing", "Movement Shooter"],
    "Mr. Two Way":       ["Two-Way Wing"],
    "Master Of Both Ends": ["Two-Way Wing"],

    # ── Movement Shooter ─────────────────────────────────────────────────────
    "Sharpshooter":      ["Movement Shooter"],
    "Sharp Riser":       ["Movement Shooter"],
    "Off-Screen":        ["Movement Shooter"],
    "Catch & Shoot":     ["Movement Shooter"],
    "PlayShot":          ["Movement Shooter", "Shot Hunter"],
    "Laser Beam":        ["Movement Shooter"],
    "From The Logo":     ["Movement Shooter"],
    "Cash Out":          ["Movement Shooter"],
    "Silk Stretch":      ["Movement Shooter", "Stretch Big"],
    "Big Smooth":        ["Movement Shooter", "Stretch Big"],
    "Big Range":         ["Movement Shooter", "Stretch Big"],
    "Big Glide":         ["Movement Shooter", "Stretch Big"],
    "Wing-Running Sharpshooter": ["Movement Shooter"],

    # ── Iso Creator ──────────────────────────────────────────────────────────
    "Iso Sniper":        ["Iso Creator", "Shot Hunter"],
    "Iso Savant":        ["Iso Creator"],
    "Iso ":              ["Iso Creator"],          # space prevents "Isolation" false-match
    " Iso":              ["Iso Creator"],
    "Walking Bucket":    ["Iso Creator", "3-Level Scorer"],
    "Bucket Getter":     ["Iso Creator"],
    "Offensive Engine":  ["Iso Creator"],
    "Shot Creator":      ["Iso Creator", "3-Level Scorer", "Shot Hunter"],
    "Combo Guard":       ["Iso Creator"],
    "Playmaking 3PT":    ["Playmaking Big", "Shot Hunter"],   # e.g. "Playmaking 3PT Creator"
    " Creator":          ["Iso Creator"],                     # generic "Creator" suffix
    "Ankle-Breaking":    ["Iso Creator"],
    "Ankle Snatcher":    ["Iso Creator", "Lockdown Guard"],
    "Ankle Taker":       ["Iso Creator", "Lockdown Guard"],
    "Shifty King":       ["Iso Creator", "Shot Hunter"],
    "Crafty Iso":        ["Iso Creator"],

    # ── Shot Hunter ───────────────────────────────────────────────────────────
    "Shot Hunter":       ["Shot Hunter"],
    "3PT Shot Hunter":   ["Shot Hunter"],
    "Iso Sniper":        ["Shot Hunter", "Iso Creator"],
    "3PT Sniper":        ["Shot Hunter", "Movement Shooter"],
    " Sniper":           ["Shot Hunter"],          # e.g. "Ball-Hawking Sniper"
    "3PT-Sniping":       ["Shot Hunter"],          # e.g. "3PT-Sniping Creator"
    "Automatic":         ["Shot Hunter"],
    "Dime-Dropping 3PT Gunner": ["Shot Hunter", "Break Starter"],
    "Shifty King":       ["Shot Hunter", "Iso Creator"],

    # ── 3-Level Scorer ───────────────────────────────────────────────────────
    "3-Level":           ["3-Level Scorer"],
    "Crafty ":           ["3-Level Scorer"],       # Crafty = multi-level skilled scorer
    "Gritty ":           ["3-Level Scorer"],
    "Versatile Scorer":  ["3-Level Scorer"],
    "Versatile Scoring": ["3-Level Scorer"],
    "Versatile-Scoring": ["3-Level Scorer"],
    "Versatile Paint Finisher": ["3-Level Scorer", "Inside-Out Scorer"],
    "Versatile Paint Bully": ["Paint Bully", "3-Level Scorer"],
    "Versatile Slasher": ["Slashing Forward", "3-Level Scorer"],
    "Versatile Post Scorer": ["Paint Bully", "3-Level Scorer"],
    "Versatile Playmaking Slasher": ["3-Level Scorer", "Slashing Forward"],
    "The Anomaly":       ["3-Level Scorer"],
    "Backline ":         ["3-Level Scorer"],       # Backline = post-up 3-level threat
    "Physical 3-Level":  ["3-Level Scorer"],

    # ── Mid-Range Specialist ─────────────────────────────────────────────────
    "Mid-Range":         ["Mid-Range Specialist"],
    "Mid-Paint":         ["Mid-Range Specialist", "Paint Bully"],
    "Mid-Post":          ["Mid-Range Specialist"],
    "Middy ":            ["Mid-Range Specialist"],
    " Middy":            ["Mid-Range Specialist"],
    "Middy-":            ["Mid-Range Specialist"],
    "Middy Maestro":     ["Mid-Range Specialist"],
    "Footwork Pharaoh":  ["Mid-Range Specialist"],
    "Midrange":          ["Mid-Range Specialist"],

    # ── High Flyer ───────────────────────────────────────────────────────────
    "High Flyer":        ["High Flyer"],
    "High-Flying":       ["High Flyer"],
    "High-Flyer":        ["High Flyer"],
    "Aerial ":           ["High Flyer"],
    "Aerial Playmaker":  ["High Flyer", "Break Starter"],
    "Posterizer":        ["High Flyer"],
    "Poster Dunker":     ["High Flyer"],
    "Dunk Tank":         ["High Flyer", "Rim Running Big"],
    "Drive & Rise":      ["High Flyer", "Slashing Forward"],
    "Yamming":           ["High Flyer", "Paint Bully"],
    "Power Dunker":      ["High Flyer", "Rim Running Big"],
    "3PT-Sniping Posterizer": ["High Flyer", "Shot Hunter"],

    # ── Rim Running Big ──────────────────────────────────────────────────────
    "Rim Runner":        ["Rim Running Big"],
    "Rim Running":       ["Rim Running Big"],
    "Rim-Running":       ["Rim Running Big"],
    "Rim Rocker":        ["Rim Running Big"],
    "Rim Wrecker":       ["Rim Running Big"],
    "Rim-Rocking":       ["Rim Running Big"],
    "Rim-Wrecking":      ["Rim Running Big"],
    "Rim-Reaping":       ["Rim Running Big"],
    "Rim Reaper":        ["Rim Running Big"],
    "Rim-Running Putback": ["Rim Running Big", "Putback Finisher"],
    "Lob Threat":        ["Rim Running Big"],
    "Power Finisher":    ["Rim Running Big", "Slashing Forward"],
    "Swats & Shots":     ["Rim Running Big", "Stretch Big"],

    # ── Playmaking Big ───────────────────────────────────────────────────────
    "Point Center":      ["Playmaking Big"],
    "Point Four":        ["Playmaking Big"],
    "Point Forward":     ["Playmaking Big", "Break Starter"],
    "Playmaker ":        ["Playmaking Big"],
    " Playmaker":        ["Playmaking Big"],
    "Triple-Double":     ["Playmaking Big"],
    "Fluid Four":        ["Playmaking Big"],
    "Footer":            ["Playmaking Big"],
    "Dot Dispenser":     ["Playmaking Big", "Break Starter"],
    "Playmaking Slasher": ["Playmaking Big", "Slashing Forward"],
    "Post Playmaker":    ["Playmaking Big", "Paint Bully"],
    "Post Creator":      ["Playmaking Big", "Paint Bully"],
    "Crafty Post Playmaker": ["Playmaking Big"],

    # ── Slashing Forward ─────────────────────────────────────────────────────
    "Slasher":           ["Slashing Forward"],
    "Slashing ":         ["Slashing Forward"],
    " Slashing":         ["Slashing Forward"],
    "Blow-By":           ["Slashing Forward"],
    "Power Slasher":     ["Slashing Forward"],
    "Floor-Sweeping":    ["Slashing Forward"],
    "Layup Artist":      ["Slashing Forward"],
    "Laymaker":          ["Slashing Forward"],
    "Physical Laymaker": ["Slashing Forward"],
    "Slashing Point Forward": ["Slashing Forward", "Playmaking Big"],
    "Snatch & Slash":    ["Slashing Forward", "Lockdown Guard"],
    "Wing-Running Finisher": ["Slashing Forward"],
    "Wing-Running Dynamic Finisher": ["Slashing Forward", "High Flyer"],

    # ── Defensive Connector ──────────────────────────────────────────────────
    "Edge Enforcer":     ["Defensive Connector"],
    "Edge-Enforcing":    ["Defensive Connector"],
    "Bodyguard":         ["Defensive Connector"],
    "Steel Curtain":     ["Defensive Connector"],
    "Eliminator":        ["Defensive Connector"],
    "The Guard Dog":     ["Defensive Connector", "Lockdown Guard"],
    "Versatile Defender": ["Defensive Connector", "Two-Way Wing"],
    "Physical Versatile Defender": ["Defensive Connector"],
    "Defensive Playmaker": ["Defensive Connector", "Playmaking Big"],
    "Perimeter Lock":    ["Defensive Connector", "Lockdown Guard"],
    "Physical Defense":  ["Defensive Connector"],

    # ── Stretch Big ──────────────────────────────────────────────────────────
    "Stretch ":          ["Stretch Big"],
    " Stretch":          ["Stretch Big"],
    "Pick & Pop":        ["Stretch Big"],
    "Pick & Popper":     ["Stretch Big"],
    " Popper":           ["Stretch Big"],
    "Skilled Stretch":   ["Stretch Big"],
    "Stretch Four":      ["Stretch Big"],
    "Stretch Five":      ["Stretch Big"],
    "Stretch Anchor":    ["Stretch Big"],
    "Small Ball Four":   ["Stretch Big"],
    "Stretch Board Enforcer": ["Stretch Big", "Glass Cleaner"],
    "Post-Scoring Stretch": ["Stretch Big", "Paint Bully"],
    "Backline Stretch":  ["Stretch Big", "3-Level Scorer"],

    # ── Glass Cleaner ────────────────────────────────────────────────────────
    "Glass ":            ["Glass Cleaner"],
    " Glass":            ["Glass Cleaner"],
    "Glass Guardian":    ["Glass Cleaner"],
    "Glass Visionary":   ["Glass Cleaner"],
    " Cleaner":          ["Glass Cleaner"],
    "Cleaner ":          ["Glass Cleaner"],
    "Board-Hunting":     ["Glass Cleaner"],
    "Board-Enforcing":   ["Glass Cleaner"],
    "Board Hunter":      ["Glass Cleaner"],
    "Board Enforcer":    ["Glass Cleaner"],
    "Lock & Board":      ["Glass Cleaner", "Lockdown Guard", "Defensive Connector"],
    "Lockdown Cleaner":  ["Glass Cleaner", "Lockdown Guard"],
    "Riser":             ["Glass Cleaner", "Rim Running Big"],

    # ── Paint Bully ──────────────────────────────────────────────────────────
    "Paint Bully":       ["Paint Bully"],
    " Bully":            ["Paint Bully"],
    "Bulldozer":         ["Paint Bully"],
    "Bulldozing":        ["Paint Bully"],
    "Bulldimer":         ["Paint Bully", "Break Starter"],
    "Post Bully":        ["Paint Bully"],
    "Post-Bully":        ["Paint Bully"],
    "Force of Nature":   ["Paint Bully"],
    "Masher":            ["Paint Bully"],
    "Grinder":           ["Paint Bully"],
    "Athletic Paint Prodigy": ["Paint Bully", "High Flyer"],
    "Power-Finishing":   ["Paint Bully", "Rim Running Big"],
    "Paint Pounder":     ["Paint Bully"],
    "Backline Paint Bully": ["Paint Bully", "3-Level Scorer"],
    "Paint-Pounding":    ["Paint Bully"],
    "Paint-Scoring":     ["Paint Bully"],
    "Paint-Finishing":   ["Paint Bully", "Inside-Out Scorer"],
    "Paint Hawk":        ["Paint Bully", "Lockdown Guard"],

    # ── Break Starter ────────────────────────────────────────────────────────
    "Break Starter":     ["Break Starter"],
    "Break-Starting":    ["Break Starter"],
    "Dime-Dropper":      ["Break Starter"],
    "Dimer":             ["Break Starter"],
    "Diming ":           ["Break Starter"],
    " Diming":           ["Break Starter"],
    "Tempo Pusher":      ["Break Starter"],
    "Table Setter":      ["Break Starter", "Playmaking Big"],
    "Table-Setting":     ["Break Starter", "Playmaking Big"],
    "Chaos Trigger":     ["Break Starter"],
    "Rim-Running Dime":  ["Break Starter", "Rim Running Big"],
    "Transition":        ["Break Starter"],
    "Disruptive Wing Runner": ["Break Starter", "Defensive Connector"],
    "Defensive Rebounder": ["Break Starter", "Glass Cleaner"],

    # ── Lockdown Guard ───────────────────────────────────────────────────────
    "Ball-Hawking":      ["Lockdown Guard"],
    "Ball-Snatching":    ["Lockdown Guard"],
    "Clamp Thief":       ["Lockdown Guard"],
    "Clamp ":            ["Lockdown Guard"],
    " Clamp":            ["Lockdown Guard"],
    "Lockdown ":         ["Lockdown Guard"],
    " Lockdown":         ["Lockdown Guard"],
    "Shot-Erasing":      ["Lockdown Guard", "Defensive Connector"],
    "Shot-Obliterating": ["Lockdown Guard"],
    "Disruptive Lockdown": ["Lockdown Guard"],
    "Physical Lockdown": ["Lockdown Guard"],
    "Thieving":          ["Lockdown Guard"],
    "Disruptive ":       ["Lockdown Guard", "Defensive Connector"],
    " Disruptive":       ["Lockdown Guard", "Defensive Connector"],
    "Ball Snatcher":     ["Lockdown Guard"],
    "Physical Ball":     ["Lockdown Guard"],
    "3PT Rim-Wrecking Ball Hawk": ["Lockdown Guard", "Rim Running Big"],
    "Inside-Out Ball Hawk": ["Lockdown Guard", "Inside-Out Scorer"],
    "Playmaking 3-Level Ball Hawk": ["Lockdown Guard", "3-Level Scorer"],
    "3PT High-Flying Ball Hawk":   ["Lockdown Guard", "High Flyer"],

    # ── Putback Finisher ─────────────────────────────────────────────────────
    "Putback":           ["Putback Finisher"],
    "Crasher":           ["Putback Finisher", "Glass Cleaner"],
    "Crashing ":         ["Putback Finisher"],
    " Crashing":         ["Putback Finisher"],
    "Faceup ":           ["Putback Finisher"],
    " Faceup":           ["Putback Finisher"],
    "Putback Pro":       ["Putback Finisher"],
    "Putback High-Flying": ["Putback Finisher", "High Flyer"],
    "Drive & Rise Board Enforcer": ["Putback Finisher", "Glass Cleaner"],

    # ── Inside-Out Scorer ────────────────────────────────────────────────────
    "Inside-Out ":       ["Inside-Out Scorer"],
    " Inside-Out":       ["Inside-Out Scorer"],
    "Inside-Out-":       ["Inside-Out Scorer"],
    "Inside-Out Scorer": ["Inside-Out Scorer"],
    "Inside-Out Slasher": ["Inside-Out Scorer", "Slashing Forward"],
    "Inside-Out Creator": ["Inside-Out Scorer", "Iso Creator"],
    "Inside-Out Playmaker": ["Inside-Out Scorer", "Playmaking Big"],
}

# ---------------------------------------------------------------------------
# EXCEL LOADING
# ---------------------------------------------------------------------------

EXCEL_FILENAME = "Archs for Build.xlsx"
BUILD_NAME_COLUMN = "Build Name"


def find_excel_path(search_from: Optional[str] = None) -> Optional[str]:
    """Search for the Excel file relative to search_from (defaults to this file's dir)."""
    if search_from is None:
        search_from = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(search_from, EXCEL_FILENAME)
    return candidate if os.path.isfile(candidate) else None


@lru_cache(maxsize=1)
def load_build_names(path: str) -> list[str]:
    """
    Load and return sorted unique build names from the Excel file.
    Result is cached after first load.
    """
    df = pd.read_excel(path, engine="openpyxl", usecols=[BUILD_NAME_COLUMN])
    names = df[BUILD_NAME_COLUMN].dropna().astype(str).str.strip()
    return sorted(set(n for n in names if n))


# ---------------------------------------------------------------------------
# MATCHING LOGIC
# ---------------------------------------------------------------------------

def map_build_name(build_name: str) -> list[str]:
    """
    Return a deduplicated, sorted list of archetype names that match the
    given build name via KEYWORD_ARCHETYPE_MAP.

    Matching is case-insensitive substring search.
    """
    name_lower = build_name.lower()
    matched: set[str] = set()

    for keyword, archetypes in KEYWORD_ARCHETYPE_MAP.items():
        if keyword.lower() in name_lower:
            matched.update(archetypes)

    return sorted(matched)


def map_all_builds(path: str) -> dict:
    """
    Load all unique build names and map each to archetypes.

    Returns:
        {
            "total": int,
            "mapped_count": int,
            "unmapped_count": int,
            "mapped": [ {"build_name": str, "archetypes": [str, ...]}, ... ],
            "unmapped": [str, ...],
        }
    """
    build_names = load_build_names(path)

    mapped = []
    unmapped = []

    for name in build_names:
        archetypes = map_build_name(name)
        if archetypes:
            mapped.append({"build_name": name, "archetypes": archetypes})
        else:
            unmapped.append(name)

    return {
        "total": len(build_names),
        "mapped_count": len(mapped),
        "unmapped_count": len(unmapped),
        "mapped": mapped,
        "unmapped": unmapped,
    }


def get_builds_for_archetype(archetype_name: str, path: str) -> list[str]:
    """Return all build names that map to a given archetype."""
    build_names = load_build_names(path)
    return [n for n in build_names if archetype_name in map_build_name(n)]
