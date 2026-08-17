"""
Converts assets/profile.<ext> into colored ASCII art.

Output: a list of rows, each row a list of (char, "#rrggbb") tuples,
consumed by generate_svg.py to render <tspan> elements.

Terminal characters are roughly twice as tall as they are wide, so we
under-sample rows relative to columns to avoid a squashed portrait.
"""

from PIL import Image, ImageOps, ImageFilter

# Classic monotonic density ramp (sparse -> dense). Fewer, well-tested
# characters render far more coherently than a long custom ramp, where
# visual weight often isn't actually monotonic across similar glyphs.
RAMP = " .:-=+*#%@"


def _luminance(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def image_to_ascii(path: str, columns: int = 70) -> list[str]:
    """Monochrome density-mapped ASCII art (brightness -> character only).
    Color is applied uniformly at render time so it stays legible against
    both light and dark card backgrounds - matching the classic neofetch
    look rather than a full-color pixel reproduction."""
    im = Image.open(path).convert("RGBA")

    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("L")  # grayscale
    im = ImageOps.autocontrast(im, cutoff=1)  # spread the tonal range

    aspect_correction = 0.52  # font cells are ~2:1 tall, compensate
    w, h = im.size
    rows = max(1, round((columns * (h / w)) * aspect_correction))

    # slight blur before a high-quality downsample avoids aliasing/noise
    # on fine detail (hair strands, etc.) at low target resolutions
    im = im.filter(ImageFilter.GaussianBlur(radius=max(1.0, w / columns / 6)))
    im = im.resize((columns, rows), resample=Image.LANCZOS)

    # darker pixels (hair, shadow) -> denser glyphs; bright pixels -> space.
    # gamma > 1 pushes midtones lighter so only real shadow/edge detail
    # renders dense, keeping the portrait readable instead of a solid block.
    gamma = 1.3
    ramp_len = len(RAMP)

    out: list[str] = []
    px = im.load()
    for y in range(rows):
        line = []
        for x in range(columns):
            darkness = (1.0 - (px[x, y] / 255.0)) ** gamma
            idx = min(ramp_len - 1, int(darkness * ramp_len))
            line.append(RAMP[idx])
        out.append("".join(line))
    return out


if __name__ == "__main__":
    art = image_to_ascii("assets/profile.png", columns=60)
    for row in art:
        print("".join(c for c, _ in row))
