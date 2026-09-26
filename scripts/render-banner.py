"""Zeichnet das Banner des Profils (assets/banner-*.svg).

Links der gezeichnete Avatar auf seiner Identitätsfarbe, rechts ein
Terminal, das sich selbst tippt.
Text wird mit fontTools in Pfade umgewandelt (Talvesa Mono), damit GitHub
keine Schrift laden muss; das Tippen ist SMIL und läuft auch in einem <img>.

    pip install fonttools brotli
    TALVESA_FONTS=<Ordner mit talvesa-mono-regular.woff2> python scripts/render-banner.py
"""

import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = os.environ["TALVESA_FONTS"].rstrip("/")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"


class Face:
    def __init__(self, path):
        font = TTFont(path)
        self.gs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm

    def text(self, s, x, y, size, tracking=0.0):
        """Pfad für `s` mit Grundlinie y, dazu die Kante nach jedem Zeichen."""
        scale = size / self.upm
        pen = SVGPathPen(self.gs)
        cx, edges = x, []
        for ch in s:
            name = self.cmap.get(ord(ch))
            if name is None:
                raise SystemExit(f"Glyphe fehlt: {ch!r}")
            g = self.gs[name]
            if ch != " ":
                g.draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
            cx += g.width * scale + tracking * size
            edges.append(cx)
        return pen.getCommands(), edges


MONO = Face(f"{FONTS}/talvesa-mono-regular.woff2")

# Der Avatar (viewBox 0 0 64 64).
AVATAR = """
<path d="M6 64c1.5-12 12-18 26-18s24.5 6 26 18z" fill="#F4F5F7"/>
<path d="M27 40h10v9a5 5 0 0 1-10 0z" fill="#E2AC80"/>
<ellipse cx="32" cy="28" rx="14.5" ry="16.5" fill="#F0C39C"/>
<path d="M17.5 27c0 13 6.5 20 14.5 20s14.5-7 14.5-20c0 7-5 9.5-14.5 9.5S17.5 34 17.5 27z" fill="#3E2C21"/>
<path d="M17.5 27.5C17 16 23 10.5 32 10.5S47 16 46.5 27.5c-1-6-5.5-8-14.5-8s-13.5 2-14.5 8z" fill="#3E2C21"/>
<circle cx="26.2" cy="27.5" r="1.9" fill="#2A1F18"/>
<circle cx="37.8" cy="27.5" r="1.9" fill="#2A1F18"/>
"""

W, H = 1280, 380
THEMES = {
    "light": dict(
        bg="#F5F5F5", grid="rgba(11,11,11,0.06)", ink="#0B0B0B", soft="#5C5C5C",
        accent="#873FA6", tint="#EADCF0", term="#FFFFFF", bar="#EFEFEF",
        edge="rgba(11,11,11,0.12)", dot="#C9C9C9",
    ),
    "dark": dict(
        bg="#0B0B0B", grid="rgba(245,245,245,0.06)", ink="#F5F5F5", soft="#A3A3A3",
        accent="#BE7ADB", tint="#2B1A33", term="#141414", bar="#1C1C1C",
        edge="rgba(245,245,245,0.12)", dot="#3A3A3A",
    ),
}

# Das Terminal: (Befehl?, Text). Befehle werden getippt, Ausgaben erscheinen.
LINES = [
    (True, "cat studio.txt"),
    (False, "Talvesa · Websites & Apps aus Freiburg"),
    (True, "cat stack.txt"),
    (False, "Python · Django · React · PostgreSQL"),
    (True, "ship --with-care"),
]
TYPE = 0.075  # Sekunden pro Zeichen
PAUSE = 0.45


def banner(t):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        'aria-label="Baut Talvesa — Websites und Apps aus Freiburg.">',
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
    ]
    grid = [f"M{x} 0V{H}" for x in range(0, W + 1, 60)] + [f"M0 {y}H{W}" for y in range(0, H + 1, 60)]
    out.append(f'<path d="{" ".join(grid)}" stroke="{t["grid"]}" fill="none"/>')

    # Das Gesicht im Kreis seiner Farbe.
    cx, cy, r = 250, 192, 118
    out.append(f'<clipPath id="face"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{t["tint"]}"/>')
    s = 2 * r / 64 * 0.92
    out.append(
        f'<g clip-path="url(#face)"><g transform="translate({cx - 32 * s:.2f} {cy - 32 * s + 12:.2f}) scale({s:.4f})">'
        f"{AVATAR}</g></g>"
    )
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="none" stroke="{t["accent"]}" stroke-width="2"/>')

    # Das Terminal.
    x0, y0, x1, y1 = 470, 52, 1196, 332
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="14" fill="{t["term"]}" stroke="{t["edge"]}"/>')
    out.append(f'<path d="M{x0} {y0 + 40}V{y0 + 14}a14 14 0 0 1 14-14H{x1 - 14}a14 14 0 0 1 14 14V{y0 + 40}Z" fill="{t["bar"]}"/>')
    out.append(f'<path d="M{x0} {y0 + 40}H{x1}" stroke="{t["edge"]}"/>')
    for i in range(3):
        out.append(f'<circle cx="{x0 + 24 + i * 20}" cy="{y0 + 20}" r="6" fill="{t["dot"]}"/>')
    title = "zsh"
    _, e = MONO.text(title, 0, 0, 13, 0.04)
    d, _ = MONO.text(title, (x0 + x1 - e[-1]) / 2, y0 + 25, 13, 0.04)
    out.append(f'<path fill="{t["soft"]}" d="{d}"/>')

    left, base, lh, size = x0 + 32, y0 + 88, 40, 22
    clock = 0.4
    cursor_x = left
    for i, (cmd, text) in enumerate(LINES):
        y = base + i * lh
        if cmd:
            d, _ = MONO.text("$", left, y, size)
            out.append(f'<path fill="{t["accent"]}" opacity="0" d="{d}">'
                       f'<set attributeName="opacity" to="1" begin="{clock:.2f}s" fill="freeze"/></path>')
            tx = left + 2 * size * 0.6
            d, edges = MONO.text(text, tx, y, size)
            widths = [0.0] + [e - tx for e in edges]
            dur = TYPE * len(text)
            out.append(f'<clipPath id="l{i}"><rect x="{tx}" y="{y - size}" width="0" height="{size * 1.5}">'
                       f'<animate attributeName="width" values="{";".join(f"{w:.1f}" for w in widths)}" '
                       f'calcMode="discrete" begin="{clock + 0.25:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
            out.append(f'<path fill="{t["ink"]}" clip-path="url(#l{i})" d="{d}"/>')
            clock += 0.25 + dur + PAUSE
            cursor_x = edges[-1] + 4
        else:
            d, _ = MONO.text(text, left, y, size)
            out.append(f'<path fill="{t["soft"]}" opacity="0" d="{d}">'
                       f'<set attributeName="opacity" to="1" begin="{clock:.2f}s" fill="freeze"/></path>')
            clock += PAUSE

    # Der Cursor blinkt nach dem letzten Befehl weiter.
    y = base + (len(LINES) - 1) * lh
    out.append(f'<rect x="{cursor_x:.1f}" y="{y - size * 0.8:.1f}" width="{size * 0.55:.1f}" height="{size:.1f}" '
               f'fill="{t["accent"]}" opacity="0"><animate attributeName="opacity" values="1;0" calcMode="discrete" '
               f'dur="1.1s" begin="{clock - PAUSE:.2f}s" repeatCount="indefinite"/></rect>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


os.makedirs(OUT, exist_ok=True)
for name, theme in THEMES.items():
    with open(f"{OUT}/banner-{name}.svg", "w") as fh:
        fh.write(banner(theme))
print("ok")
