"""
Random utility helpers for player generation.
Centralizing randomness here makes it easy to seed for reproducibility.
"""

import random
import string
from typing import Tuple


def clamp(value: int, lo: int = 25, hi: int = 99) -> int:
    """Clamp an integer to the valid 2K attribute range."""
    return max(lo, min(hi, value))


def rand_in_range(rng: Tuple[int, int]) -> int:
    """Return a random integer within a (min, max) tuple, clamped 25–99."""
    return clamp(random.randint(rng[0], rng[1]))


def weighted_choice(options: list, weights: list):
    """Return one item from options using provided weights."""
    return random.choices(options, weights=weights, k=1)[0]


def jitter(value: int, spread: int = 5) -> int:
    """Add small noise to a value — creates natural variation."""
    return clamp(value + random.randint(-spread, spread))


def scale_range(rng: Tuple[int, int], modifier: int) -> Tuple[int, int]:
    """Shift a range by a modifier, clamping to 25–99."""
    return (clamp(rng[0] + modifier), clamp(rng[1] + modifier))


# ---------------------------------------------------------------------------
# Name generation
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Jamal", "DeShawn", "Marcus", "Tyrese", "Jaylen", "Malik", "Darius",
    "Trevon", "Isaiah", "Jordan", "Elijah", "Xavier", "Kendrick", "Quincy",
    "Damian", "Lebron", "Carmelo", "Jalen", "Zion", "Cade", "Evan", "Trevor",
    "Scottie", "Brandon", "Anthony", "Donovan", "Shai", "Ja", "Paolo",
    "Victor", "Scoot", "Amen", "Ausar", "Chet", "Jabari", "Walker",
    "Keyonte", "Gradey", "Taylor", "Jordan", "Brandin", "Jarace", "Cam",
    "Dalen", "Dariq", "Leonard", "Kobe", "Steph", "Kevin", "Giannis",
    "Nikola", "Luka", "Joel", "Devin", "Trae", "Zach", "Bam", "Tyrese",
    "Miles", "Chris", "Andre", "Rajon", "Derrick", "Paul", "Jimmy", "Kawhi",
    "Rudy", "Draymond", "Klay", "Andrew", "Brook", "Jarrett", "Myles",
    "Daniel", "Spencer", "Gary", "Matisse", "OG", "Robert", "Pascal",
    "Fred", "Kyle", "P.J.", "Seth", "Maxi", "Tobias", "Shake", "Tyus",
    "Monte", "Immanuel", "Aaron", "Davion", "Jaden", "Ziaire", "Keon",
    "Moses", "Chris", "Quentin", "Caleb", "Ryan", "Matt", "Bojan",
    "Jonas", "Bogdan", "Nicolas", "Furkan", "Kristaps", "Lauri", "Naz",
    "Anfernee", "Sekou", "Obi", "Dean", "Jalen", "Alperen",
]

LAST_NAMES = [
    "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson",
    "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Young", "Robinson", "Walker", "Scott", "Nelson", "Hill",
    "Allen", "Mitchell", "Carter", "Parker", "Evans", "Turner", "Torres",
    "Collins", "Edwards", "Stewart", "Sanchez", "Morris", "Rogers", "Reed",
    "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper",
    "Richardson", "Cox", "Howard", "Ward", "Brooks", "Watson", "Kelly",
    "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson",
    "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes",
    "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzales",
    "Bryant", "Alexander", "Russell", "Griffin", "Diallo", "Mbaye",
    "Sissoko", "Camara", "Ndiaye", "Traore", "Kouyate", "Coulibaly",
    "Okafor", "Onyeka", "Bamba", "Achiuwa", "Okoro", "Garuba",
    "Sengun", "Bitadze", "Zubac", "Nurkic", "Jokic", "Doncic",
    "Haliburton", "Cunningham", "Mobley", "Barnes", "Green", "Suggs",
    "Duarte", "Davison", "Ziaire", "Wagner", "Kuminga", "Moody",
    "Porter", "Maxey", "Tyrese", "Sharpe", "Holmgren", "Smith",
    "Henderson", "Miller", "Banchero", "Jabari", "Keegan", "Shaedon",
    "Bennedict", "A.J.",
]


def generate_name() -> str:
    """Generate a random player name."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def pick_weighted_from_dict(d: dict, default_weight: float = 1.0) -> str:
    """Pick a key from a dict using values as weights."""
    keys = list(d.keys())
    weights = [d[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]
