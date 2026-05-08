"""
Random utility helpers for player generation.
Centralizing randomness here makes it easy to seed for reproducibility.
"""

import random
import string
from typing import Tuple, Optional, Set


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
#
# Regional pools with weighted selection so most prospects feel like
# contemporary U.S. names while still producing plausible international
# draftees (Francophone West African, European/Balkan, Spanish/Latino,
# East Asian, etc.). First and last names are drawn from the same region
# in most cases to avoid jarring combinations, with a small chance of a
# multicultural mix to reflect real-world variety.
# ---------------------------------------------------------------------------

# US-general: broad contemporary first names from varied U.S. backgrounds.
_US_FIRST = [
    # Classic / common
    "James", "Michael", "David", "Daniel", "Matthew", "Andrew", "Joseph",
    "Joshua", "Christopher", "Ryan", "Tyler", "Brandon", "Jacob", "Nathan",
    "Aaron", "Adam", "Alex", "Benjamin", "Caleb", "Cameron", "Carter",
    "Cole", "Connor", "Cooper", "Dylan", "Ethan", "Evan", "Garrett",
    "Grant", "Henry", "Hunter", "Ian", "Isaac", "Jack", "Jackson",
    "Jared", "Jason", "John", "Jonathan", "Justin", "Kyle", "Logan",
    "Lucas", "Luke", "Mason", "Nathaniel", "Nicholas", "Noah", "Owen",
    "Patrick", "Peter", "Robert", "Samuel", "Sean", "Spencer", "Stephen",
    "Thomas", "Trevor", "Wesley", "William", "Wyatt", "Zachary",
    # Contemporary varied / urban U.S.
    "Aiden", "Ayden", "Brayden", "Bryson", "Camden", "Chase", "Dominic",
    "Drew", "Easton", "Elijah", "Emmett", "Gavin", "Grayson", "Hayden",
    "Holden", "Jaden", "Jaxon", "Josiah", "Kaden", "Landon", "Levi",
    "Maddox", "Maverick", "Micah", "Parker", "Preston", "Sawyer", "Silas",
    "Tanner", "Tate", "Tristan", "Weston",
    # African-American common
    "Andre", "Anthony", "Antoine", "Brandon", "Bryce", "Calvin", "Cedric",
    "Cory", "Curtis", "Damon", "Darnell", "Darrell", "Darrin", "DeAndre",
    "Deion", "Demetrius", "Derek", "Derrick", "Devin", "Dominique",
    "Donovan", "Dwayne", "Eric", "Ezekiel", "Frederick", "Gerald",
    "Isaiah", "Jamal", "Jamar", "Jaquan", "Jaylen", "Jeremiah",
    "Jermaine", "Jerome", "Julian", "Kameron", "Keion", "Kendall",
    "Kendrick", "Khalil", "Kobe", "Kris", "Kwame", "Lamar", "Lance",
    "Langston", "Larry", "Leon", "Maurice", "Marquis", "Marvin",
    "Maximus", "Micah", "Miles", "Nelson", "Omar", "Orlando", "Paul",
    "Quincy", "Quinton", "Rashad", "Raheem", "Reggie", "Rico",
    "Roland", "Ronald", "Ronnie", "Roy", "Russell", "Shawn", "Sidney",
    "Solomon", "Stanley", "Sterling", "Sylvester", "Terrance", "Terrell",
    "Terrence", "Theo", "Tobias", "Tristan", "Tyrone", "Vince",
    "Wallace", "Wendell", "Xavier",
    # Less-common / modern
    "Asher", "Atticus", "August", "Beau", "Bennett", "Brooks", "Cassius",
    "Dawson", "Dexter", "Emerson", "Ezra", "Felix", "Finley", "Forrest",
    "Graham", "Greyson", "Jasper", "Judah", "Kaiden", "Kingston",
    "Kyrie", "Lennox", "Maddox", "Nehemiah", "Nico", "Otis", "Phoenix",
    "Quentin", "Reid", "Roman", "Tate", "Zion",
]

# US-general surnames: census-common American family names.
_US_LAST = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez",
    "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright",
    "Scott", "Hill", "Adams", "Baker", "Nelson", "Carter", "Mitchell",
    "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans",
    "Edwards", "Collins", "Stewart", "Morris", "Murphy", "Cook", "Rogers",
    "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Gomez",
    "Kelly", "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood",
    "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes", "Cruz",
    "Hughes", "Price", "Myers", "Long", "Foster", "Sanders", "Ross",
    "Morales", "Powell", "Sullivan", "Russell", "Ortiz", "Jenkins",
    "Gutierrez", "Perry", "Butler", "Barnes", "Fisher", "Henderson",
    "Coleman", "Simmons", "Patterson", "Jordan", "Reynolds", "Hamilton",
    "Graham", "Kim", "Gonzales", "Alexander", "Ramos", "Wallace",
    "Griffin", "West", "Cole", "Hayes", "Chavez", "Gibson", "Bryant",
    "Ellis", "Stevens", "Murray", "Ford", "Marshall", "Owens", "McDonald",
    "Harrison", "Ruiz", "Kennedy", "Wells", "Alvarez", "Woods",
    "Mendoza", "Castillo", "Olson", "Webb", "Washington", "Tucker",
    "Freeman", "Burns", "Henry", "Vasquez", "Snyder", "Simpson",
    "Crawford", "Jimenez", "Porter", "Mason", "Shaw", "Gordon",
    "Wagner", "Hunter", "Romero", "Hicks", "Dixon", "Hunt", "Palmer",
    "Robertson", "Black", "Holmes", "Stone", "Meyer", "Boyd",
    "Mills", "Warren", "Fox", "Rose", "Rice", "Moreno", "Schmidt",
    "Patel", "Ferguson", "Nichols", "Herrera", "Medina", "Ryan",
    "Fernandez", "Weaver", "Daniels", "Stephens", "Gardner", "Payne",
    "Kelley", "Dunn", "Pierce", "Arnold", "Tran", "Spencer", "Peters",
    "Hawkins", "Grant", "Hansen", "Castro", "Hoffman", "Hart",
    "Elliott", "Cunningham", "Knight", "Bradley", "Carroll", "Hudson",
    "Duncan", "Armstrong", "Berry", "Andrews", "Johnston", "Ray",
    "Lane", "Riley", "Carpenter", "Perkins", "Aguilar", "Silva",
    "Richards", "Willis", "Matthews", "Chapman", "Lawrence", "Garza",
    "Vargas", "Watkins", "Wheeler", "Larson", "Carlson", "Harper",
    "George", "Greene", "Burke", "Guzman", "Morrison", "Munoz",
    "Jacobs", "Obrien", "Lawson", "Franklin", "Lynch", "Bishop",
    "Carr", "Salazar", "Austin", "Mendez", "Holland", "Wilcox",
    "Fleming", "Schultz", "Pearson", "Soto", "Lambert", "Cohen",
]

# West African / Francophone (Senegal, Mali, Ivory Coast, Cameroon, etc.)
# Common in international basketball pipelines.
_WAFRICAN_FIRST = [
    "Ibou", "Ibrahima", "Mamadou", "Moussa", "Modibo", "Cheick", "Cheikh",
    "Souleymane", "Ousmane", "Amadou", "Adama", "Aliou", "Bakary",
    "Boubacar", "Issa", "Mohamed", "Hamidou", "Abdoulaye", "Pape",
    "Pathe", "Khalil", "Yakhouba", "Yves", "Sidy", "Moustapha",
    "Tidiane", "Salif", "Drissa", "Birama", "Fode", "Bamba",
    "Oumar", "Idrissa", "Lassana", "Sekou", "Tariq", "Hamady",
    "Olivier", "Pascal", "Serge", "Christian", "Joel", "Alex",
]

_WAFRICAN_LAST = [
    "Diallo", "Diakite", "Cisse", "Sissoko", "Camara", "Konate",
    "Coulibaly", "Toure", "Traore", "Diabate", "Doumbia", "Keita",
    "Niang", "Ndiaye", "Mbaye", "Faye", "Fall", "Diop", "Sow",
    "Gueye", "Sarr", "Sy", "Sagna", "Ba", "Kone", "Ouattara",
    "Bamba", "Kouyate", "Sidibe", "Drame", "Diawara", "Dembele",
    "Ndong", "Mbah", "Eboue", "Tchouameni", "Anguelou",
    "Fofana", "Soumare", "Mboup", "Kanoute", "Sylla", "Bah",
    "Diatta", "Thiam", "Wade", "Seck", "Lo", "Ndoye",
]

# European/Balkan/Eastern (Serbia, Croatia, Slovenia, Lithuania, Greece, Turkey)
_BALKAN_FIRST = [
    "Nikola", "Dragan", "Stefan", "Marko", "Aleksandar", "Bogdan",
    "Bojan", "Vlatko", "Vlado", "Dario", "Dejan", "Goran", "Ivica",
    "Mario", "Milos", "Nemanja", "Petar", "Filip",
    "Tomislav", "Vasilije", "Darko", "Boban", "Ognjen", "Mirko",
    "Jusuf", "Andro", "Kristijan", "Toni", "Ante",
    "Roko", "Ivan", "Zoran", "Branko", "Igor", "Slaven",
    # Lithuanian / Baltic
    "Jonas", "Domantas", "Sarunas", "Mantas", "Marius",
    "Tadas", "Linas", "Edgaras", "Karolis", "Rokas", "Paulius",
    "Tomas", "Mindaugas",
    # Greek
    "Kostas", "Vassilis", "Thanasis", "Nikos", "Dimitris",
    "Yannis", "Panagiotis", "Stelios", "Georgios",
    # Turkish
    "Omer", "Mehmet", "Ercan", "Onuralp",
    "Sertac", "Berke", "Emre", "Murat", "Hakan", "Burak",
    # Slovenian / Latvian / Finnish
    "Andrejs", "Janis", "Sasu", "Mikko", "Aleksi", "Petteri",
    "Tomaz", "Klemen", "Matic", "Jaka",
]

_BALKAN_LAST = [
    "Petrovic", "Stojanovic", "Markovic", "Nikolic", "Pavlovic",
    "Lukic", "Jovanovic", "Mitrovic", "Maric", "Ilic", "Tomic",
    "Vukovic", "Kovac", "Horvat", "Babic", "Novak", "Cvetkovic",
    "Mihailovic", "Vasiljevic", "Krstic", "Andric", "Stankovic",
    "Radulovic", "Simic", "Popovic", "Filipovic", "Knezevic",
    # Lithuanian / Baltic
    "Kazlauskas", "Petrauskas", "Jankauskas", "Balciunas",
    "Stankevicius", "Grigaliunas", "Jasikevicius", "Kalnins",
    "Berzins", "Ozols", "Ozolins",
    # Greek
    "Papadopoulos", "Papanikolaou", "Kalaitzakis", "Sloukas",
    "Mantzaris", "Karagiannis", "Andreadis", "Vlachos",
    # Turkish
    "Yilmaz", "Demir", "Kara", "Aydin", "Sahin", "Celik",
    "Yildiz", "Aslan", "Ozdemir", "Aksoy", "Korkmaz", "Polat",
]

# Spanish / Latino (Spain, Argentina, Brazil, DR, Puerto Rico, Mexico)
_LATINO_FIRST = [
    "Carlos", "Javier", "Luis", "Diego", "Eduardo", "Fernando", "Ricardo",
    "Sebastian", "Mateo", "Santiago", "Andres", "Manuel", "Pablo",
    "Pedro", "Alvaro", "Alejandro", "Adrian", "Ignacio", "Hugo",
    "Marco", "Gabriel", "Rafael", "Lucas", "Joaquin", "Emilio",
    "Cristian", "Esteban", "Gonzalo", "Nicolas", "Tomas", "Bruno",
    "Rodrigo", "Salvador", "Vicente", "Jose", "Juan", "Miguel",
    "Felipe", "Leonardo", "Joao", "Vinicius", "Paulo", "Gustavo",
    "Juancho", "Willy", "Alex", "Ricky", "Sergio", "Juan Pablo",
]

_LATINO_LAST = [
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera",
    "Gomez", "Diaz", "Reyes", "Morales", "Cruz", "Ortiz", "Gutierrez",
    "Chavez", "Ramos", "Ruiz", "Alvarez", "Mendoza", "Vasquez",
    "Castillo", "Jimenez", "Romero", "Herrera", "Medina", "Aguilar",
    "Vargas", "Castro", "Soto", "Mendez", "Salazar", "Delgado",
    "Pena", "Ibarra", "Orozco", "Cabrera", "Cortez", "Rojas",
    "Velez", "Acosta", "Navarro", "Vega", "Molina", "Cordero",
    "Rosales", "Nieves", "Espinoza", "Marin", "Carmona", "Trejo",
    "Solis", "Ponce", "Lara", "Cervantes", "Saldana", "Peralta",
    "Quintero", "Velasquez", "Arias", "Camacho", "Galvan",
    # Brazilian / Portuguese
    "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa",
    "Carvalho", "Almeida", "Ribeiro", "Barbosa", "Lima",
]

# East Asian (Chinese, Japanese, Korean) — kept focused; westernized
# "Asian-American" prospects show up via the U.S. pool already.
_EASIAN_FIRST = [
    "Yuta", "Rui", "Hayato", "Ren", "Sho", "Ryo", "Riku", "Daiki",
    "Kenta", "Naoki", "Takumi", "Hiroki", "Yuki", "Sora", "Haruto",
    "Yusuke", "Akira", "Kaito", "Takashi", "Kenji",
    "Ji-Hoon", "Min-Jun", "Hyun-Woo", "Seung-Hyun", "Jae-Won",
    "Jin-Ho", "Joon-Ho", "Sung-Min", "Tae-Yong",
    "Jianhao", "Wei", "Bo", "Hao", "Junwei", "Tianyu", "Zihao",
]

_EASIAN_LAST = [
    "Watanabe", "Tanaka", "Yamamoto", "Suzuki", "Sato",
    "Takahashi", "Kobayashi", "Nakamura", "Ito", "Yoshida",
    "Saito", "Yamada", "Sasaki", "Matsumoto", "Inoue",
    "Kim", "Park", "Choi", "Jung", "Kang", "Yoon", "Ahn",
    "Cho", "Shin", "Jang", "Hong",
    "Wang", "Li", "Zhang", "Chen", "Yang", "Zhao", "Huang",
    "Wu", "Zhou", "Lin", "Ma", "Hu", "Guo", "Sun", "Xu",
]

# Francophone / Caribbean French (broad, French-speaking African and Caribbean
# basketball pipelines). Avoids obvious current-NBA full-name clones.
_CARIBBEAN_FIRST = [
    "Olivier", "Pascal", "Theo", "Killian", "Nicolas", "Frank",
    "Mathias", "Adrien", "Hugo", "Quentin", "Yves", "Romain",
    "Lucien", "Sebastien", "Maxime", "Thibault", "Vincent",
    "Etienne", "Antoine", "Florent", "Gaetan", "Loic",
    "Mickael", "Renaud", "Cyril", "Jeremy", "Bruno",
]

_CARIBBEAN_LAST = [
    "Bertrand", "Lefebvre", "Moreau", "Laurent", "Simon", "Michel",
    "Leroy", "Roux", "Vincent", "Fontaine", "Chevalier", "Robin",
    "Schneider", "Lemoine", "Marchand", "Dufour", "Blanchard",
    "Gauthier", "Perrin", "Morel", "Girard", "Bonnet",
    "Francois", "Dupont", "Boyer", "Gerard", "Caron", "Renard",
    "Faure", "Andre", "Pichon",
]

# Pools registry: (first_pool, last_pool, region_label, default_weight)
# Same-region first+last is the typical draw to avoid jarring combos.
_REGIONS = [
    ("us_general", _US_FIRST, _US_LAST, 78),
    ("wafrican", _WAFRICAN_FIRST, _WAFRICAN_LAST, 7),
    ("balkan_euro", _BALKAN_FIRST, _BALKAN_LAST, 7),
    ("latino", _LATINO_FIRST, _LATINO_LAST, 4),
    ("easian", _EASIAN_FIRST, _EASIAN_LAST, 2),
    ("caribbean_franco", _CARIBBEAN_FIRST, _CARIBBEAN_LAST, 2),
]

# Probability of crossing first-name region with last-name region (multicultural).
_CROSS_REGION_PROB = 0.05

# Hard blocklist: full names that read as obvious current-NBA stars.
# Generation will reroll if it hits one of these.
_NBA_FULLNAME_BLOCKLIST = {
    "lebron james", "stephen curry", "steph curry", "kevin durant",
    "giannis antetokounmpo", "nikola jokic", "luka doncic", "joel embiid",
    "jayson tatum", "jaylen brown", "jimmy butler", "kawhi leonard",
    "paul george", "damian lillard", "devin booker", "anthony davis",
    "ja morant", "shai gilgeous-alexander", "trae young", "zion williamson",
    "victor wembanyama", "chet holmgren", "paolo banchero", "scoot henderson",
    "anthony edwards", "tyrese haliburton", "tyrese maxey", "donovan mitchell",
    "jrue holiday", "draymond green", "klay thompson", "rudy gobert",
    "bam adebayo", "karl-anthony towns", "jamal murray", "kyrie irving",
    "james harden", "russell westbrook", "chris paul", "lamelo ball",
    "lonzo ball", "zach lavine", "demar derozan", "deandre ayton",
    "evan mobley", "scottie barnes", "cade cunningham", "jalen green",
    "jaren jackson", "desmond bane", "jalen brunson", "mikal bridges",
    "ausar thompson", "amen thompson", "brandon miller", "jabari smith",
    "keyonte george", "gradey dick", "dereck lively", "bilal coulibaly",
    "kel'el ware", "alex sarr", "donovan clingan", "stephon castle",
    "zaccharie risacher", "reed sheppard",
}

# Soft blocklist: surnames so identifiable they create star-clones too easily.
# These get downweighted heavily (effectively excluded from US pool draws).
_HIGH_SIGNAL_NBA_LAST = {
    "antetokounmpo", "doncic", "jokic", "embiid", "wembanyama",
    "haliburton", "banchero", "holmgren", "tatum",
}


def _pick_region() -> Tuple[list, list, str]:
    """Pick a regional name pool by weight. Returns (first_pool, last_pool, label)."""
    weights = [r[3] for r in _REGIONS]
    region = random.choices(_REGIONS, weights=weights, k=1)[0]
    return region[1], region[2], region[0]


def _pick_region_filtered(blocked_labels: Set[str]) -> Tuple[list, list, str]:
    """Pick a regional pool, excluding labels in blocked_labels if possible."""
    candidates = [r for r in _REGIONS if r[0] not in blocked_labels]
    if not candidates:
        return _pick_region()
    weights = [r[3] for r in candidates]
    region = random.choices(candidates, weights=weights, k=1)[0]
    return region[1], region[2], region[0]


def _pick_one_name(blocked_regions: Optional[Set[str]] = None) -> Tuple[str, str, str]:
    """Pick a (first, last, region_label) tuple, mostly same-region with rare crossover."""
    if blocked_regions:
        first_pool, last_pool, label = _pick_region_filtered(blocked_regions)
    else:
        first_pool, last_pool, label = _pick_region()
    # Small chance to cross last name from a different region for multicultural feel.
    if random.random() < _CROSS_REGION_PROB:
        _, alt_last_pool, _ = _pick_region()
        last_pool = alt_last_pool
    first = random.choice(first_pool)
    last = random.choice(last_pool)
    return first, last, label


# Pick numbers (1-indexed) where extra naming constraints apply.
_TOP10_FIRST_NAME_DEDUP_LIMIT = 10
_TOP5_REGIONAL_SPREAD_LIMIT = 5
_TOP5_NON_US_CLUSTER_CAP = 2  # avoid 3+ non-US/general regions in top 5


def generate_name(
    used_names: Optional[Set[str]] = None,
    pick_number: int = 0,
    class_flavor: str = "",
    used_first_names_top10: Optional[Set[str]] = None,
    top5_regions: Optional[list] = None,
) -> str:
    """
    Generate a random player name.

    Args:
        used_names: Optional set of already-used full names (lowercased) to
                    avoid duplicates within a class. When provided, the
                    generated name is added to it.
        pick_number: 1-indexed pick number. Enables top-10 first-name dedup
                    and (for Balanced) top-5 regional-cluster spread.
        class_flavor: Class flavor name ("Balanced", "Guard-heavy", etc.).
                    Top-5 regional spread is only enforced for "Balanced".
        used_first_names_top10: Set of lowercased first names already used
                    among picks 1..10. Updated in-place when this pick is
                    in the top 10.
        top5_regions: Ordered list of region labels for picks 1..5 so far.
                    Used for Balanced flavor to avoid regional clustering.
                    Updated in-place when this pick is in the top 5.

    Returns:
        "First Last" string.
    """
    in_top10 = 1 <= pick_number <= _TOP10_FIRST_NAME_DEDUP_LIMIT
    in_top5  = 1 <= pick_number <= _TOP5_REGIONAL_SPREAD_LIMIT
    enforce_top5_spread = (in_top5 and class_flavor == "Balanced"
                           and top5_regions is not None)

    # Build region blocklist for top-5 Balanced spread, if applicable.
    # The non-US cluster cap is the dominant constraint; back-to-back
    # avoidance is dropped when it would conflict (e.g. last pick was
    # us_general and non-US is already at the cap).
    def _blocked_regions() -> Set[str]:
        blocked: Set[str] = set()
        if not enforce_top5_spread:
            return blocked
        # Cluster cap first (dominant): avoid 3+ non-US/general picks in top 5.
        non_us = sum(1 for r in (top5_regions or []) if r != "us_general")
        cluster_active = non_us >= _TOP5_NON_US_CLUSTER_CAP
        if cluster_active:
            for r in _REGIONS:
                if r[0] != "us_general":
                    blocked.add(r[0])
        # Back-to-back avoidance — only add when it doesn't empty the pool.
        if top5_regions:
            last_label = top5_regions[-1]
            # If cluster is active, never block us_general (that's the only
            # remaining option); otherwise it's safe to block last_label.
            if not (cluster_active and last_label == "us_general"):
                blocked.add(last_label)
        return blocked

    # Two-phase attempt: first with strict constraints, then relaxed.
    for phase in (0, 1):
        # In phase 1 we relax top-5 region blocklist (still keep dedup).
        blocked = _blocked_regions() if phase == 0 else set()
        for _ in range(40):
            first, last, region_label = _pick_one_name(blocked_regions=blocked)
            full_lc = f"{first} {last}".lower()
            first_lc = first.lower()
            # Block obvious NBA full-name collisions.
            if full_lc in _NBA_FULLNAME_BLOCKLIST:
                continue
            # Heavily downweight high-signal NBA surnames (skip ~80% of the time).
            if last.lower() in _HIGH_SIGNAL_NBA_LAST and random.random() < 0.8:
                continue
            # Class-level dedup (full name).
            if used_names is not None and full_lc in used_names:
                continue
            # Top-10 first-name dedup. Always enforced when set is provided.
            if (in_top10 and used_first_names_top10 is not None
                    and first_lc in used_first_names_top10):
                continue
            # Accept this pick.
            if used_names is not None:
                used_names.add(full_lc)
            if in_top10 and used_first_names_top10 is not None:
                used_first_names_top10.add(first_lc)
            if in_top5 and top5_regions is not None:
                top5_regions.append(region_label)
            return f"{first} {last}"
    # Fallback if we somehow exhausted attempts: just return whatever we drew.
    first, last, region_label = _pick_one_name()
    if used_names is not None:
        used_names.add(f"{first} {last}".lower())
    if in_top10 and used_first_names_top10 is not None:
        used_first_names_top10.add(first.lower())
    if in_top5 and top5_regions is not None:
        top5_regions.append(region_label)
    return f"{first} {last}"


def pick_weighted_from_dict(d: dict, default_weight: float = 1.0) -> str:
    """Pick a key from a dict using values as weights."""
    keys = list(d.keys())
    weights = [d[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]
