"""
Regression and sanity tests for the badge system.

Run from repo root:  python scripts/test_badge_system.py
"""
import random
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.badge_requirements import max_eligible_level, BADGE_REQUIREMENTS
from data.fields import PERSONALITY_BADGES, ALL_BADGES
from data.archetype_badge_pools import ARCHETYPE_BADGE_POOLS
from utils.generate_player import generate_player
from utils.generate_class import generate_draft_class


# -----------------------------------------------------------------------------
# 1. Eligibility unit tests — the regression target from the bad workbook.
# -----------------------------------------------------------------------------

EXPECTED = []  # (name, attrs, height_in, expected_dict)

def case(name, attrs, height_in, expected):
    EXPECTED.append((name, attrs, height_in, expected))


# Anfernee Kuminga from the bad workbook.
kuminga_attrs = {
    "Mid Range Shot":   75,
    "Three Point Shot": 67,
    "Standing Dunk":    65,
    "Driving Dunk":     90,
    "Vertical":         88,
    "Pass Accuracy":    63,
    "Block":            65,
    "Strength":         78,
    "Agility":          80,
    "Speed":            82,
    "Speed With Ball":  70,
    "Ball Handle":      62,
    "Driving Layup":    78,
    "Close Shot":       70,
    "Post Control":     50,
    "Offensive Rebound": 55,
    "Defensive Rebound": 65,
    "Interior Defense": 60,
    "Perimeter Defense": 60,
    "Steal":            55,
    "Pass Vision":      55,
}
case("Kuminga regression — Limitless Range NEVER eligible (3PT 67)",
     kuminga_attrs, 79, {"Limitless Range": "None"})
case("Kuminga regression — Deadeye Bronze max (75/67, neither hits 85)",
     kuminga_attrs, 79, {"Deadeye": "Bronze"})
case("Kuminga regression — Set Shot Specialist Bronze max (75/67 < 78)",
     kuminga_attrs, 79, {"Set Shot Specialist": "Bronze"})
case("Kuminga regression — Rise Up no Gold (Standing Dunk 65 < 90)",
     kuminga_attrs, 79, {"Rise Up": "None"})  # Standing Dunk 65 < bronze 72
case("Kuminga regression — Break Starter Bronze max (PA 63 < 75)",
     kuminga_attrs, 79, {"Break Starter": "None"})  # PA 63 < bronze 65
case("Kuminga — Posterizer Gold should pass (DD90, V88) but cap at S",
     kuminga_attrs, 79, {"Posterizer": "Silver"})  # DD>=87 silver, V>=75 silver, min=Silver

# Sanity: clean shooter
shooter_attrs = {
    "Three Point Shot": 95,
    "Mid Range Shot":   90,
    "Speed":            70,
    "Agility":          70,
    "Ball Handle":      80,
    "Strength":         60,
    "Driving Dunk":     50,
    "Vertical":         55,
    "Standing Dunk":    40,
    "Pass Accuracy":    70,
    "Block":            40,
    "Steal":            70,
    "Interior Defense": 50,
    "Perimeter Defense": 70,
}
case("Shooter — Limitless Range Gold (3PT 95)",
     shooter_attrs, 76, {"Limitless Range": "Gold"})
case("Shooter — Deadeye Gold (3PT 95 >= 92)",
     shooter_attrs, 76, {"Deadeye": "Gold"})
case("Shooter — Posterizer None (DD 50 < 73)",
     shooter_attrs, 76, {"Posterizer": "None"})

# Big with height min
big_attrs = {
    "Standing Dunk": 88, "Driving Dunk": 80, "Vertical": 75,
    "Strength": 90, "Block": 80, "Interior Defense": 88,
    "Offensive Rebound": 85, "Defensive Rebound": 85,
    "Mid Range Shot": 50, "Three Point Shot": 40,
}
case("Big tall — Rise Up Silver (SD 88 silver, V 75 silver)",
     big_attrs, 84, {"Rise Up": "Silver"})
case("Short guy — Rise Up None (height 72 < 78)",
     big_attrs, 72, {"Rise Up": "None"})
case("Big — Brick Wall Silver (Strength 90, height 84)",
     big_attrs, 84, {"Brick Wall": "Silver"})


def run_eligibility_tests():
    failures = []
    for name, attrs, height, expected in EXPECTED:
        for badge, want in expected.items():
            got = max_eligible_level(badge, attrs, height)
            if got != want:
                failures.append((name, badge, want, got))
    print(f"Eligibility tests: {len(EXPECTED)} cases, "
          f"{len(failures)} failures")
    for f in failures:
        print("  FAIL:", f)
    return len(failures) == 0


# -----------------------------------------------------------------------------
# 2. Class generation sample — counts and Gold scarcity by tier
# -----------------------------------------------------------------------------

def class_summary(class_type, n=30, seed=42):
    random.seed(seed)
    players, _warnings = generate_draft_class(
        class_type=class_type, player_count=n, seed=seed
    )
    print(f"\n=== {class_type} ({n} players) — seed {seed} ===")
    print(f"{'Pick':>4}  {'Tier':>4}  {'GP':>3}  {'P':>3}  {'Gld':>3}  Arch / Build")
    by_tier = Counter()
    gameplay_counts = []
    gold_counts = []
    for p in players:
        gp = sum(1 for b, l in p["badges"].items()
                  if l != "None" and b not in PERSONALITY_BADGES)
        per = sum(1 for b, l in p["badges"].items()
                   if l != "None" and b in PERSONALITY_BADGES)
        gold = sum(1 for b, l in p["badges"].items()
                    if l == "Gold" and b not in PERSONALITY_BADGES)
        by_tier[p["tier"]] += 1
        gameplay_counts.append((p["tier"], gp))
        gold_counts.append((p["tier"], gold))
        print(f"{p['pick_number']:>4}  T{p['tier']:>2}   {gp:>3}  {per:>3}  {gold:>3}  "
              f"{p['archetype']}")
    # Per-tier averages
    print("\n  Per-tier gameplay-badge counts (min/avg/max):")
    for t in sorted(by_tier):
        vals = [g for tt, g in gameplay_counts if tt == t]
        if vals:
            print(f"    Tier {t}: n={len(vals)}  "
                  f"min={min(vals)}  avg={sum(vals)/len(vals):.1f}  max={max(vals)}")
    print("  Per-tier Gold counts (min/avg/max):")
    for t in sorted(by_tier):
        vals = [g for tt, g in gold_counts if tt == t]
        if vals:
            print(f"    Tier {t}: n={len(vals)}  "
                  f"min={min(vals)}  avg={sum(vals)/len(vals):.1f}  max={max(vals)}")
    return players


# -----------------------------------------------------------------------------
# 3. Archetype spot checks — confirm avoid lists are respected
# -----------------------------------------------------------------------------

def avoid_list_audit(players):
    bad = []
    for p in players:
        avoid = set(ARCHETYPE_BADGE_POOLS.get(p["archetype"], {}).get("avoid", []))
        for b, l in p["badges"].items():
            if l != "None" and b in avoid:
                bad.append((p["pick_number"], p["archetype"], b, l))
    if bad:
        print(f"\n  AVOID-LIST VIOLATIONS ({len(bad)}):")
        for v in bad:
            print(f"    pick #{v[0]} {v[1]}: {v[2]} = {v[3]}")
    else:
        print("\n  Avoid-list audit: clean (no violations)")
    return len(bad) == 0


def attribute_eligibility_audit(players):
    """Every selected gameplay badge must be attribute-eligible at its level."""
    bad = []
    for p in players:
        for b, l in p["badges"].items():
            if l == "None" or b in PERSONALITY_BADGES:
                continue
            if b not in BADGE_REQUIREMENTS:
                continue
            max_lv = max_eligible_level(b, p["attributes"], p["height_inches"])
            from data.badge_requirements import _LEVEL_RANK
            if _LEVEL_RANK[l] > _LEVEL_RANK[max_lv]:
                bad.append((p["pick_number"], p["archetype"], b, l, max_lv))
    if bad:
        print(f"\n  ELIGIBILITY VIOLATIONS ({len(bad)}):")
        for v in bad:
            print(f"    pick #{v[0]} {v[1]}: {v[2]} = {v[3]} (max eligible: {v[4]})")
    else:
        print("  Eligibility audit: clean")
    return len(bad) == 0


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    ok_unit = run_eligibility_tests()

    all_clean = True
    for class_type in ["Average", "Strong", "Generational", "Weak", "Top-heavy", "Deep role-player class"]:
        try:
            players = class_summary(class_type, n=30, seed=42)
            clean_avoid = avoid_list_audit(players)
            clean_elig = attribute_eligibility_audit(players)
            all_clean = all_clean and clean_avoid and clean_elig
        except Exception as e:
            print(f"Class {class_type} failed: {e}")
            all_clean = False

    print("\n=== SUMMARY ===")
    print("Eligibility unit tests:", "PASS" if ok_unit else "FAIL")
    print("Class audits:           ", "PASS" if all_clean else "FAIL")
    sys.exit(0 if (ok_unit and all_clean) else 1)
