import sys
sys.path.insert(0, "scripts")
from generate_svg import render_svg

STATS = {
    "login": "xsaadahmed",
    "created_at": "2024-07-17T09:45:00Z",
    "public_repos": 18,
    "followers": 1,
    "releases": 2,
    "commits": 1736,
    "contributions_past_year": 124,
    "loc_added": 64959,
    "loc_removed": 1251,
}

PROFILE = {
    "kernel": "Software Developer",
    "os": "Windows 11, iOS 27 beta, Linux",
    "editor": "VSCode and Cursor",
    "languages": "Python, Java, C, JS/TS, SQL",
    "education": "UMass Amherst - CS + Stats",
    "spoken_languages": "English, Urdu, Hindi, Arabic",
    "hobbies": "Soccer, Cooking",
    "email": "xsaadahmed@gmail.com",
    "school_email": "saadahmed@umass.edu",
    "linkedin": "linkedin.com/in/saadhmed",
}

with open("ascii_dark.txt") as f:
    ascii_rows_dark = [line.rstrip("\n") for line in f]
with open("ascii_light.txt") as f:
    ascii_rows_light = [line.rstrip("\n") for line in f]

svg_dark = render_svg(ascii_rows_dark, STATS, PROFILE, "dark")
with open("dark_mode.svg", "w") as out:
    out.write(svg_dark)
print("wrote dark_mode.svg")

svg_light = render_svg(ascii_rows_light, STATS, PROFILE, "light")
with open("light_mode.svg", "w") as out:
    out.write(svg_light)
print("wrote light_mode.svg")
