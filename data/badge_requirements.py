"""
Attribute-driven badge eligibility — NBA 2K26 / NBA2KLab-style thresholds.

Each gameplay badge maps to:
  - category: Inside Scoring / Outside Scoring / Playmaking / Defending /
              Athleticism / Rebounding
  - groups: list of requirement groups. Each group is a list of
            (attribute_name, (bronze_thr, silver_thr, gold_thr)) pairs.
            Within a group, all listed attributes must clear the threshold
            (group level = MIN qualifying level across attributes).
            Across groups, the eligible level is the MAX over groups.
            One group with one attribute = simple "any" badge.
            One group with N attributes = "all" (e.g. Posterizer:
                Driving Dunk + Vertical).
            N groups = "any" alternatives (e.g. Deadeye:
                Mid Range OR Three Point).
  - height_min_inches / height_max_inches: optional inclusive bounds.

Rookies cap at Gold; HOF/Legend are never produced by this module.
"""

from typing import Dict, Iterable, List, Optional, Tuple

# Level ordering helpers
LEVEL_ORDER = ["None", "Bronze", "Silver", "Gold"]
_LEVEL_RANK = {lv: i for i, lv in enumerate(LEVEL_ORDER)}


def level_max(a: str, b: str) -> str:
    return a if _LEVEL_RANK.get(a, 0) >= _LEVEL_RANK.get(b, 0) else b


def level_min(a: str, b: str) -> str:
    return a if _LEVEL_RANK.get(a, 0) <= _LEVEL_RANK.get(b, 0) else b


def level_at_or_below(level: str, cap: str) -> str:
    return cap if _LEVEL_RANK.get(level, 0) > _LEVEL_RANK.get(cap, 0) else level


# Threshold convention: (bronze, silver, gold)
T = Tuple[int, int, int]
ReqGroup = List[Tuple[str, T]]


BADGE_REQUIREMENTS: Dict[str, dict] = {
    # ---------------- Outside Scoring ----------------
    "Deadeye": {
        "category": "Outside Scoring",
        "groups": [
            [("Mid Range Shot",  (73, 85, 92))],
            [("Three Point Shot", (73, 85, 92))],
        ],
    },
    "Limitless Range": {
        "category": "Outside Scoring",
        "groups": [
            [("Three Point Shot", (83, 89, 93))],
        ],
    },
    "Set Shot Specialist": {
        "category": "Outside Scoring",
        "groups": [
            [("Mid Range Shot",  (65, 78, 89))],
            [("Three Point Shot", (65, 78, 89))],
        ],
    },
    "Mini Marksman": {
        "category": "Outside Scoring",
        "height_max_inches": 75,  # 6'3"
        "groups": [
            [("Mid Range Shot",  (70, 82, 90))],
            [("Three Point Shot", (70, 82, 90))],
        ],
    },
    "Shifty Shooter": {
        "category": "Outside Scoring",
        "height_max_inches": 83,  # 6'11"
        "groups": [
            [("Mid Range Shot",  (72, 83, 91))],
            [("Three Point Shot", (72, 83, 91))],
        ],
    },
    "Slippery Off-Ball": {
        "category": "Outside Scoring",
        "height_max_inches": 81,  # 6'9"
        "groups": [
            [("Speed",   (70, 80, 88))],
            [("Agility", (70, 80, 88))],
        ],
    },
    "Post Fade Phenom": {
        "category": "Outside Scoring",
        "groups": [
            [("Post Control",  (70, 82, 90))],
            [("Mid Range Shot", (72, 83, 91))],
        ],
    },

    # ---------------- Inside Scoring ----------------
    "Posterizer": {
        "category": "Inside Scoring",
        "groups": [
            [("Driving Dunk", (73, 87, 93)), ("Vertical", (65, 75, 80))],
        ],
    },
    "Rise Up": {
        "category": "Inside Scoring",
        "height_min_inches": 78,  # 6'6"
        "groups": [
            [("Standing Dunk", (72, 81, 90)), ("Vertical", (60, 62, 66))],
        ],
    },
    "Aerial Wizard": {
        "category": "Inside Scoring",
        "groups": [
            [("Driving Dunk",  (64, 70, 80))],
            [("Standing Dunk", (60, 75, 84))],
        ],
    },
    "Hook Specialist": {
        "category": "Inside Scoring",
        "groups": [
            [("Close Shot",   (65, 78, 88))],
            [("Post Control", (65, 78, 88))],
        ],
    },
    "Layup Mixmaster": {
        "category": "Inside Scoring",
        "groups": [
            [("Driving Layup", (70, 82, 90))],
        ],
    },
    "Paint Prodigy": {
        "category": "Inside Scoring",
        "height_min_inches": 75,  # 6'3"
        "groups": [
            [("Close Shot", (70, 82, 90))],
        ],
    },
    "Physical Finisher": {
        "category": "Inside Scoring",
        "groups": [
            [("Driving Layup", (70, 82, 90)), ("Strength", (65, 75, 84))],
            [("Driving Dunk",  (73, 85, 92)), ("Strength", (65, 75, 84))],
        ],
    },
    "Post Powerhouse": {
        "category": "Inside Scoring",
        "groups": [
            [("Post Control", (70, 82, 90)), ("Strength", (70, 80, 88))],
        ],
    },
    "Post-Up Poet": {
        "category": "Inside Scoring",
        "groups": [
            [("Post Control", (70, 82, 90))],
        ],
    },
    "Float Game": {
        "category": "Inside Scoring",
        "groups": [
            [("Close Shot",    (68, 80, 88))],
            [("Driving Layup", (68, 80, 88))],
        ],
    },

    # ---------------- Playmaking ----------------
    "Break Starter": {
        "category": "Playmaking",
        "groups": [
            [("Pass Accuracy", (65, 75, 87))],
        ],
    },
    "Dimer": {
        "category": "Playmaking",
        "groups": [
            [("Pass Accuracy", (55, 71, 82))],
        ],
    },
    "Bail Out": {
        "category": "Playmaking",
        "groups": [
            [("Pass Accuracy", (62, 76, 86))],
        ],
    },
    "Versatile Visionary": {
        "category": "Playmaking",
        "groups": [
            [("Pass Accuracy", (70, 80, 88)), ("Pass Vision", (70, 80, 88))],
        ],
    },
    "Handles For Days": {
        "category": "Playmaking",
        "groups": [
            [("Ball Handle", (71, 81, 90))],
        ],
    },
    "Unpluckable": {
        "category": "Playmaking",
        "groups": [
            [("Ball Handle", (68, 80, 89))],
        ],
    },
    "Ankle Assassin": {
        "category": "Playmaking",
        "groups": [
            [("Ball Handle", (75, 86, 93))],
        ],
    },
    "Lightning Launch": {
        "category": "Playmaking",
        "groups": [
            [("Speed With Ball", (68, 75, 86))],
        ],
    },
    "Strong Handle": {
        "category": "Playmaking",
        "groups": [
            [("Ball Handle", (65, 78, 88)), ("Strength", (60, 72, 82))],
        ],
    },

    # ---------------- Defending ----------------
    "Challenger": {
        "category": "Defending",
        "groups": [
            [("Perimeter Defense", (71, 82, 92))],
        ],
    },
    "Glove": {
        "category": "Defending",
        "groups": [
            [("Steal", (67, 79, 91))],
        ],
    },
    "Interceptor": {
        "category": "Defending",
        "groups": [
            [("Steal", (65, 78, 88))],
        ],
    },
    "On-Ball Menace": {
        "category": "Defending",
        "groups": [
            [("Perimeter Defense", (74, 85, 91)), ("Agility", (70, 76, 80))],
        ],
    },
    "Pick Dodger": {
        "category": "Defending",
        "groups": [
            [("Perimeter Defense", (73, 83, 90)), ("Agility", (71, 75, 79))],
        ],
    },
    "Off-Ball Pest": {
        "category": "Defending",
        "groups": [
            [("Interior Defense",  (65, 78, 88))],
            [("Perimeter Defense", (65, 78, 88))],
        ],
    },
    "High-Flying Denier": {
        "category": "Defending",
        "groups": [
            [("Block", (68, 78, 88)), ("Vertical", (60, 74, 80))],
        ],
    },
    "Paint Patroller": {
        "category": "Defending",
        "height_min_inches": 78,  # 6'6"
        "groups": [
            [("Interior Defense", (68, 80, 90))],
            [("Block",            (68, 80, 90))],
        ],
    },
    "Post Lockdown": {
        "category": "Defending",
        "height_min_inches": 78,  # 6'6"
        "groups": [
            [("Interior Defense", (68, 80, 90)), ("Strength", (65, 76, 86))],
            [("Interior Defense", (72, 83, 92))],
        ],
    },
    "Pogo Stick": {
        "category": "Defending",
        "groups": [
            [("Vertical", (70, 80, 88))],
        ],
    },

    # ---------------- Athleticism ----------------
    "Brick Wall": {
        "category": "Athleticism",
        "height_min_inches": 77,  # 6'5"
        "groups": [
            [("Strength", (72, 83, 91))],
        ],
    },
    "Immovable Enforcer": {
        "category": "Athleticism",
        "groups": [
            [("Strength", (70, 82, 90)), ("Interior Defense", (62, 74, 84))],
            [("Strength", (70, 82, 90)), ("Perimeter Defense", (62, 74, 84))],
        ],
    },

    # ---------------- Rebounding ----------------
    "Rebound Chaser": {
        "category": "Rebounding",
        "groups": [
            [("Offensive Rebound", (60, 80, 92))],
            [("Defensive Rebound", (60, 80, 92))],
        ],
    },
    "Boxout Beast": {
        "category": "Rebounding",
        "groups": [
            [("Offensive Rebound", (55, 70, 85))],
            [("Defensive Rebound", (55, 70, 85))],
        ],
    },
}


# ---------------------------------------------------------------------------
# Eligibility evaluation
# ---------------------------------------------------------------------------

def _level_for_value(value: int, thresholds: T) -> str:
    bronze, silver, gold = thresholds
    if value >= gold:
        return "Gold"
    if value >= silver:
        return "Silver"
    if value >= bronze:
        return "Bronze"
    return "None"


def _group_level(group: ReqGroup, attributes: dict) -> str:
    """All attributes in a group must qualify; group level = MIN across them."""
    level = "Gold"
    for attr, thresholds in group:
        val = attributes.get(attr, 0) or 0
        attr_level = _level_for_value(val, thresholds)
        if attr_level == "None":
            return "None"
        level = level_min(level, attr_level)
    return level


def max_eligible_level(badge: str, attributes: dict, height_inches: int) -> str:
    """
    Return the maximum eligible level for a badge given player attributes
    and height. Returns one of: None | Bronze | Silver | Gold.
    """
    spec = BADGE_REQUIREMENTS.get(badge)
    if spec is None:
        # Unknown gameplay badge: be permissive, but cap at Bronze
        return "Bronze"

    h_min = spec.get("height_min_inches")
    h_max = spec.get("height_max_inches")
    if h_min is not None and height_inches < h_min:
        return "None"
    if h_max is not None and height_inches > h_max:
        return "None"

    best = "None"
    for group in spec["groups"]:
        best = level_max(best, _group_level(group, attributes))
    return best


def is_gameplay_badge(badge: str) -> bool:
    return badge in BADGE_REQUIREMENTS


def gameplay_badges() -> Iterable[str]:
    return BADGE_REQUIREMENTS.keys()
