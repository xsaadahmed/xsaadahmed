"""
Static version - no GitHub Actions, no live fetching.
Edit STATS and PROFILE below with your real numbers, then:

    python3 build_static.py

Re-run any time your numbers change; it just regenerates the two SVGs.
"""

import sys
sys.path.insert(0, "scripts")
from generate_svg import render_svg

# ---- edit these whenever your numbers change --------------------------
STATS = {
    "login": "xsaadahmed",
    "created_at": "2024-07-17T09:45:00Z",   # your GitHub join date (used for "Uptime")
    "public_repos": 18,
    "followers": 1,
    "releases": 2,
    "commits": 1736,                        # sum of totalCommitContributions across all years
    "contributions_past_year": 124,
    "loc_added": 64959,
    "loc_removed": 1251,
}

PROFILE = {
    "editor": "VS Code, PyCharm",
    "languages": "Python, Java, C, JS/TS, SQL",
    "favorite_language": "Python",
    "currently": "SWE Extern @ Pfizer",
    "university": "UMass Amherst - CS + Stats",
    "email": "xsaadahmed@gmail.com",
    "linkedin": "linkedin.com/in/saadhmed",
}
# -------------------------------------------------------------------------

with open("ascii.txt") as f:
    ascii_rows = [line.rstrip("\n") for line in f]

for mode in ("dark", "light"):
    svg = render_svg(ascii_rows, STATS, PROFILE, mode)
    with open(f"{mode}_mode.svg", "w") as out:
        out.write(svg)
    print(f"wrote {mode}_mode.svg")
