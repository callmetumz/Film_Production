# Team name:        The Equal SQLs
# Student numbers:  4351723, 4354243, 4359047, 4358074, 4335167
# File name:        extract_principals.py
#
# extract_principals.py
# Pulls the cast and crew rows for our 33 selected films out of IMDb's
# title.principals.tsv.gz (too large to upload) into a small file.
#
# How to run:
#   1. Put this file in the same folder as title.principals.tsv.gz
#   2. python extract_principals.py
#   3. Send back the principals_subset.tsv it creates (a few hundred rows)

import gzip

SOURCE = "title.principals.tsv.gz"
OUTPUT = "principals_subset.tsv"

FILM_IDS = {
    "tt0080801",
    "tt0105316",
    "tt0112749",
    "tt0419279",
    "tt0445776",
    "tt0468565",
    "tt0783532",
    "tt1057500",
    "tt1059969",
    "tt10699362",
    "tt1136608",
    "tt1213929",
    "tt1646111",
    "tt1823672",
    "tt1899240",
    "tt1922721",
    "tt1937504",
    "tt2304771",
    "tt2396489",
    "tt2585072",
    "tt3243554",
    "tt3487278",
    "tt3921136",
    "tt4573706",
    "tt4627352",
    "tt4996954",
    "tt5174974",
    "tt5702884",
    "tt5827360",
    "tt6042062",
    "tt6333070",
    "tt7416536",
    "tt8442402",
}

kept = 0
with gzip.open(SOURCE, "rt", encoding="utf-8") as src, \
        open(OUTPUT, "w", encoding="utf-8", newline="") as out:
    out.write(src.readline())  # header row
    for line in src:
        if line.split("\t", 1)[0] in FILM_IDS:
            out.write(line)
            kept += 1

print(f"Done: wrote {kept} rows to {OUTPUT}")
