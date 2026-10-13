# Team name:        The Equal SQLs
# Student numbers:  4351723, 4354243, 4359047, 4358074, 4335167
# File name:        build_sample_data.py
#
# build_sample_data.py
# Turns the IMDb extracts in data_prep/source/ into sql/02_sample_data.sql.
#
# FILM, FILM_GENRE, ACTOR, CREW_MEMBER, ROLE, FILM_CAST and FILM_CREW come from the
# IMDb non-commercial datasets (https://developer.imdb.com/non-commercial-datasets/).
# IMDb has no filming data, so LOCATION, PRODUCTION_SCHEDULE and the crew contact
# emails are made-up sample values generated here (fixed seed, so the output is
# always the same).
#
# Run from the repository root:   python data_prep/build_sample_data.py

import csv
import json
import random
import unicodedata
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"
OUT = HERE.parent / "sql" / "02_sample_data.sql"
random.seed(312)


def read_tsv(name):
    with open(SRC / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def null(value):
    return None if value in ("\\N", "", None) else value


def sql(value):
    """Format a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


PARTICLES = {"van", "de", "der", "du", "von", "den", "di"}
SUFFIXES = {"jr.", "jr", "sr.", "sr"}


def split_name(full):
    """'Marcel van Heerden' -> ('Marcel', 'van Heerden'); 'Ninja' -> ('Ninja', None)."""
    parts = full.split()
    if len(parts) == 1:
        return parts[0], None
    cut = len(parts) - 1
    if parts[-1].lower() in SUFFIXES and len(parts) > 2:
        cut -= 1
    for i in range(1, len(parts) - 1):
        if parts[i].lower() in PARTICLES:
            cut = min(cut, i)
            break
    return " ".join(parts[:cut]), " ".join(parts[cut:])


def ascii_fold(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "".join(ch for ch in text.lower() if ch.isalnum())


# ---------------------------------------------------------------- films + genres
# Use the South African release title where IMDb's primary title is the export title.
LOCAL_TITLES = {"tt0783532": "Jerusalema", "tt6333070": "Inxeba", "tt1922721": "Skoonheid",
                "tt2585072": "iNumber Number"}
films_src = sorted(read_tsv("films_subset.tsv"),
                   key=lambda r: (int(r["startYear"]), r["primaryTitle"]))
film_id, films, genres = {}, [], []
for i, r in enumerate(films_src, start=1):
    film_id[r["tconst"]] = i
    title = LOCAL_TITLES.get(r["tconst"], r["primaryTitle"])
    runtime = null(r["runtimeMinutes"])
    films.append((i, title, int(r["startYear"]), int(runtime) if runtime else None))
    for g in (null(r["genres"]) or "").split(","):
        if g:
            genres.append((i, g))

# ---------------------------------------------------------------- people, cast, crew
names = {r["nconst"]: r for r in read_tsv("names_subset.tsv")}
principals = sorted(read_tsv("principals_subset.tsv"),
                    key=lambda r: (film_id[r["tconst"]], int(r["ordering"])))

ROLE_NAMES = {"director": "Director", "writer": "Writer", "producer": "Producer",
              "composer": "Composer", "cinematographer": "Cinematographer", "editor": "Editor",
              "casting_director": "Casting Director", "production_designer": "Production Designer"}
# Two roles that exist but have not been assigned yet (optional participation).
UNUSED_ROLES = ["Costume Designer", "Sound Mixer"]
roles = {name: i for i, name in enumerate(list(ROLE_NAMES.values()) + UNUSED_ROLES, start=1)}

actor_id, crew_id = {}, {}
actors, crew, film_cast, film_crew = [], [], [], []
seen_cast, seen_crew = set(), set()

for r in principals:
    person = names[r["nconst"]]
    first, last = split_name(person["primaryName"])
    fid = film_id[r["tconst"]]
    if r["category"] in ("actor", "actress"):
        if r["nconst"] not in actor_id:
            actor_id[r["nconst"]] = len(actors) + 1
            birth = null(person["birthYear"])
            actors.append((len(actors) + 1, first, last, int(birth) if birth else None))
        key = (fid, actor_id[r["nconst"]])
        characters = json.loads(r["characters"]) if null(r["characters"]) else []
        # One cast record per actor per film: keep the first (main) character listed.
        if key not in seen_cast and characters:
            seen_cast.add(key)
            film_cast.append((fid, key[1], characters[0]))
    elif r["category"] in ROLE_NAMES:
        if r["nconst"] not in crew_id:
            crew_id[r["nconst"]] = len(crew) + 1
            email = None
            if last and random.random() < 0.7:      # made-up address, about 70% of crew
                email = f"{ascii_fold(first)}.{ascii_fold(last)}@filmcrew.example"
            crew.append((len(crew) + 1, first, last, email))
        key = (fid, crew_id[r["nconst"]], roles[ROLE_NAMES[r["category"]]])
        if key not in seen_crew:
            seen_crew.add(key)
            film_crew.append(key)

# ---------------------------------------------------------------- locations (made up)
locations = [
    (1, "Cape Town Film Studios", "Faure", "Cape Town"),
    (2, "Atlantic Film Studios", "Montague Gardens", "Cape Town"),
    (3, "Khayelitsha", None, "Cape Town"),
    (4, "Bo-Kaap", "Wale Street", "Cape Town"),
    (5, "Robben Island Museum", None, "Cape Town"),
    (6, "Mitchells Plain", None, "Cape Town"),
    (7, "Kliptown", None, "Soweto"),
    (8, "Chiawelo", None, "Soweto"),
    (9, "Hillbrow", None, "Johannesburg"),
    (10, "Ellis Park Stadium", "Doornfontein", "Johannesburg"),
    (11, "Fordsburg", "Mint Road", "Johannesburg"),
    (12, "Union Buildings", "Government Avenue", "Pretoria"),
    (13, "Michaelhouse School", "Balgowan", None),
    (14, "Chatsworth", None, "Durban"),
    (15, "Mdantsane", None, "East London"),
    (16, "Lady Grey", None, None),
    (17, "Drakensberg Foothills", None, "Bergville"),
    (18, "Constitution Hill", "11 Kotze Street, Braamfontein", "Johannesburg"),   # not used yet
    (19, "V&A Waterfront", "Dock Road", "Cape Town"),                             # not used yet
]
# Locations that suit particular films; other sessions use a studio.
PREFERRED = {
    "District 9": [8, 9], "Chappie": [9, 1], "Tsotsi": [7, 9], "Jerusalema": [9, 7],
    "Invictus": [10, 12, 5], "Mandela: Long Walk to Freedom": [5, 12, 1], "Spud": [13],
    "U-Carmen eKhayelitsha": [3], "Material": [11], "Four Corners": [6, 2],
    "Keeping Up with the Kandasamys": [14], "Five Fingers for Marseilles": [16],
    "Yesterday": [17], "Sarafina!": [7, 8], "Knuckle City": [15], "Skoonheid": [4, 2],
    "The Forgotten Kingdom": [17], "Kalushi: The Story of Solomon Mahlangu": [12, 7],
}
STUDIOS = [1, 2]
# Films that are captured but have no sessions scheduled yet (optional participation).
NOT_SCHEDULED = {"Moffie", "Sew the Winter to My Skin", "Mrs Right Guy"}
STARTS = ["06:00:00", "07:30:00", "09:00:00", "13:00:00", "18:30:00"]

schedule = []
for fid, title, year, _ in films:
    if title in NOT_SCHEDULED:
        continue
    places = PREFERRED.get(title, []) + STUDIOS
    day = date(year - 1, random.randint(2, 9), random.randint(1, 20))
    for n in range(random.randint(2, 5)):
        loc = places[n] if n < len(PREFERRED.get(title, [])) else random.choice(places)
        start = end = None
        chance = random.random()
        if chance < 0.80:                              # both times known
            start = random.choice(STARTS)
            longest = 9 if int(start[:2]) < 13 else 23 - int(start[:2])
            end = f"{int(start[:2]) + random.randint(3, longest):02d}:30:00"
        elif chance < 0.90:                            # start known, end still open
            start = random.choice(STARTS)
        schedule.append([fid, loc, day.isoformat(), start, end])
        day += timedelta(days=random.randint(1, 9))

# A morning and a night shoot for the same film, location and date (business rule BR10).
tsotsi = next(f[0] for f in films if f[1] == "Tsotsi")
schedule.append([tsotsi, 7, "2004-11-16", "06:00:00", "11:30:00"])
schedule.append([tsotsi, 7, "2004-11-16", "18:30:00", "23:45:00"])
schedule.sort(key=lambda s: (s[2], s[3] or ""))
schedule = [(i, *s) for i, s in enumerate(schedule, start=1)]


# ---------------------------------------------------------------- write the SQL file
def insert(table, columns, rows, per_line=1):
    lines = [f"INSERT INTO {table} ({', '.join(columns)}) VALUES"]
    values = ["(" + ", ".join(sql(v) for v in row) + ")" for row in rows]
    chunks = [", ".join(values[i:i + per_line]) for i in range(0, len(values), per_line)]
    lines.append(",\n".join("  " + c for c in chunks) + ";")
    return "\n".join(lines) + "\n"


parts = [
    "-- 02_sample_data.sql",
    "-- Sample data for film_production_db. Generated by data_prep/build_sample_data.py.",
    "-- Films, genres, people, cast and crew: IMDb non-commercial datasets.",
    "-- Locations, production schedules and contact emails: made-up sample values.",
    "-- Run 01_schema.sql first.",
    "",
    "USE film_production_db;",
    "",
    f"-- FILM ({len(films)} rows)",
    insert("FILM", ["FilmID", "Title", "ReleaseYear", "RuntimeMinutes"], films),
    f"-- FILM_GENRE ({len(genres)} rows)",
    insert("FILM_GENRE", ["FilmID", "GenreName"], genres, per_line=5),
    f"-- ACTOR ({len(actors)} rows)",
    insert("ACTOR", ["ActorID", "FirstName", "LastName", "BirthYear"], actors, per_line=3),
    f"-- CREW_MEMBER ({len(crew)} rows)",
    insert("CREW_MEMBER", ["CrewMemberID", "FirstName", "LastName", "ContactEmail"], crew),
    f"-- ROLE ({len(roles)} rows)",
    insert("ROLE", ["RoleID", "RoleName"], [(i, n) for n, i in roles.items()], per_line=5),
    f"-- LOCATION ({len(locations)} rows)",
    insert("LOCATION", ["LocationID", "LocationName", "Address", "City"], locations),
    f"-- FILM_CAST ({len(film_cast)} rows)",
    insert("FILM_CAST", ["FilmID", "ActorID", "CharacterName"], film_cast, per_line=2),
    f"-- FILM_CREW ({len(film_crew)} rows)",
    insert("FILM_CREW", ["FilmID", "CrewMemberID", "RoleID"], film_crew, per_line=8),
    f"-- PRODUCTION_SCHEDULE ({len(schedule)} rows)",
    insert("PRODUCTION_SCHEDULE",
           ["ScheduleID", "FilmID", "LocationID", "FilmingDate", "StartTime", "EndTime"],
           schedule, per_line=2),
]
OUT.write_text("\n".join(parts), encoding="utf-8")

for label, rows in [("FILM", films), ("FILM_GENRE", genres), ("ACTOR", actors),
                    ("CREW_MEMBER", crew), ("ROLE", roles), ("LOCATION", locations),
                    ("FILM_CAST", film_cast), ("FILM_CREW", film_crew),
                    ("PRODUCTION_SCHEDULE", schedule)]:
    print(f"{label:<20} {len(rows):>4} rows")
print(f"Wrote {OUT}")
