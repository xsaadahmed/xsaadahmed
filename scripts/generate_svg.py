"""
Combines ascii_art rows + a stats dict into dark_mode.svg / light_mode.svg,
laid out like a neofetch card: ASCII portrait on the left, labeled stat
lines on the right.
"""

from datetime import datetime, timezone
from xml.sax.saxutils import escape

FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.6      # monospace advance width
LINE_H = FONT_SIZE * 1.3
PAD = 24

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "label": "#58a6ff",
        "dots": "#8b949e",
        "value": "#c9d1d9",
        "accent": "#3fb950",
        "header": "#f0f6fc",
        "art": "#c9d1d9",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "label": "#0969da",
        "dots": "#8c959f",
        "value": "#24292f",
        "accent": "#1a7f37",
        "header": "#1f2328",
        "art": "#57606a",
    },
}


def _uptime_string(created_at: str) -> str:
    joined = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    days_total = (now - joined).days
    years, rem = divmod(days_total, 365)
    months, days = divmod(rem, 30)
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    parts.append(f"{days} day{'s' if days != 1 else ''}")
    return ", ".join(parts)


def _dotted_line(label: str, value: str, width: int = 34) -> tuple[str, str]:
    dots_len = max(2, width - len(label))
    return label, "." * dots_len, value


def build_stat_lines(stats: dict, profile: dict) -> list[tuple]:
    login = stats["login"]
    rows: list[tuple] = []
    rows.append(("header", f"{login}@github", "-" * 28))

    fields = [
        ("Uptime", _uptime_string(stats["created_at"])),
        ("Kernel", profile.get("kernel", "")),
        ("OS", profile.get("os", "")),
        ("Editor", profile.get("editor", "VSCode and Cursor")),
        ("Languages.Programming", profile.get("languages", "Python, Java, C, JS/TS, SQL")),
        ("Education", profile.get("education", "")),
        ("Languages", profile.get("spoken_languages", "")),
        ("Hobbies", profile.get("hobbies", "")),
    ]
    for label, value in fields:
        rows.append(("field", *_dotted_line(label, value)))

    rows.append(("blank",))
    rows.append(("section", "Contact", "-" * 34))
    for label, value in [
        ("Email", profile.get("email", "")),
        ("School Email", profile.get("school_email", "")),
        ("LinkedIn", profile.get("linkedin", "")),
        ("GitHub", login),
    ]:
        if value:
            rows.append(("field", *_dotted_line(label, value)))

    rows.append(("blank",))
    rows.append(("section", "GitHub Stats", "-" * 28))
    rows.append((
        "statline",
        f"Repos: {stats['public_repos']}",
        f"Followers: {stats['followers']}",
        f"Releases: {stats['releases']}",
    ))
    rows.append(("field", *_dotted_line("Commits (all time)", str(stats["commits"]))))
    rows.append(("field", *_dotted_line("Contributions (past year)", str(stats["contributions_past_year"]))))
    rows.append((
        "loc",
        "Lines of Code:",
        f"{stats['loc_added'] + stats['loc_removed']:,}",
        f"+{stats['loc_added']:,}",
        f"-{stats['loc_removed']:,}",
    ))
    return rows


def _text_line(x: float, y: float, spans: list[tuple[str, str]]) -> str:
    inner = "".join(
        f'<tspan fill="{color}">{escape(text)}</tspan>'
        for text, color in spans if text
    )
    return f'<text x="{x:.1f}" y="{y:.1f}" xml:space="preserve">{inner}</text>'


def _ascii_lines(ascii_rows: list[str], x0: float, y0: float, color: str, font_size: float) -> str:
    line_h = font_size * 1.3
    out = []
    for row_i, line in enumerate(ascii_rows):
        y = y0 + row_i * line_h
        out.append(f'<text x="{x0:.1f}" y="{y:.1f}" font-size="{font_size}" xml:space="preserve">'
                    f'<tspan fill="{color}">{escape(line)}</tspan></text>')
    return "\n  ".join(out)


def _stat_lines(rows: list[tuple], x0: float, y0: float, theme: dict) -> tuple[str, float, int]:
    out = []
    y = y0
    max_chars = 0

    def _track(spans: list[tuple[str, str]]) -> None:
        nonlocal max_chars
        max_chars = max(max_chars, sum(len(t) for t, _ in spans))

    for row in rows:
        kind = row[0]
        if kind == "blank":
            y += LINE_H
            continue
        if kind == "header":
            _, name, rule = row
            spans = [(name, theme["header"]), ("  " + rule, theme["border"])]
        elif kind == "section":
            _, name, rule = row
            spans = [("- " + name + " ", theme["header"]), (rule, theme["border"])]
        elif kind == "field":
            _, label, dots, value = row
            spans = [
                (". " + label + ": ", theme["label"]),
                (dots, theme["dots"]),
                (" " + value, theme["value"]),
            ]
        elif kind == "statline":
            _, a, b, c = row
            spans = [
                (". " + a, theme["label"]), ("  |  ", theme["dots"]),
                (b, theme["value"]), ("  |  ", theme["dots"]),
                (c, theme["value"]),
            ]
        elif kind == "loc":
            _, label, total, added, removed = row
            spans = [
                (". " + label + " ", theme["label"]),
                (total + " (", theme["value"]),
                (added, theme["accent"]),
                (", ", theme["value"]),
                (removed, "#f85149"),
                (")", theme["value"]),
            ]
        else:
            spans = []
        _track(spans)
        out.append(_text_line(x0, y, spans))
        y += LINE_H
    return "\n  ".join(out), y, max_chars


def render_svg(ascii_rows: list[str], stats: dict, profile: dict, mode: str,
                art_font_size: float | None = None) -> str:
    theme = THEMES[mode]
    stat_rows = build_stat_lines(stats, profile)

    art_cols = max(len(r) for r in ascii_rows)
    art_rows = len(ascii_rows)
    if art_font_size is None:
        target_h = 480
        art_font_size = max(FONT_SIZE, min(28, target_h / (art_rows * 1.3)))

    art_char_w = art_font_size * 0.6
    art_line_h = art_font_size * 1.3
    art_w = art_cols * art_char_w
    art_h = art_rows * art_line_h

    stats_x = PAD * 2 + art_w
    art_svg = _ascii_lines(ascii_rows, PAD, PAD + art_font_size, theme["art"], art_font_size)
    stats_svg, stats_end_y, stats_max_chars = _stat_lines(stat_rows, stats_x, PAD + FONT_SIZE, theme)

    total_h = max(art_h, stats_end_y - PAD) + PAD * 1.5
    total_w = stats_x + stats_max_chars * CHAR_W + PAD

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}"
     viewBox="0 0 {total_w:.0f} {total_h:.0f}" font-family="'DejaVu Sans Mono','Cascadia Code','Fira Code',Consolas,monospace" font-size="{FONT_SIZE}">
  <rect width="100%" height="100%" rx="10" fill="{theme['bg']}" stroke="{theme['border']}"/>
  {art_svg}
  {stats_svg}
</svg>"""
