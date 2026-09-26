"""Zeichnet Hero-Bild und Stückliste des Profils (assets/hero-*.svg, assets/parts-*.svg).

Eine technische Zeichnung statt eines Fotos: links die Aussage, rechts ein
Drahtmodell aus Browser und Telefon, bemaßt und beschriftet mit dem, was
bei uns gemessen wird statt versprochen. Statisch, ohne Animation.
Text wird mit fontTools in Pfade umgewandelt, damit GitHub keine Schrift
laden muss.

    pip install fonttools brotli
    TALVESA_FONTS=<Ordner mit talvesa-mono-regular.woff2> python scripts/render-hero.py
"""

import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = os.environ["TALVESA_FONTS"].rstrip("/")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"

EMBLEM = (
    "M39.154 23.238 15.259 23.238 0 0 106.715 0 91.455 23.238 67.15 23.238 "
    "105.453 81.569 91.455 102.887ZM119.451 60.337 105.453 39.02 131.076 0 159.072 0Z"
)
EMBLEM_W, EMBLEM_H = 159.072, 102.887


class Face:
    def __init__(self, path):
        font = TTFont(path)
        self.gs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm

    def path(self, s, x, y, size, tracking=0.0, anchor="start"):
        """Pfad für `s` mit Grundlinie y; anchor start|end|middle."""
        width = self.width(s, size, tracking)
        if anchor == "end":
            x -= width
        elif anchor == "middle":
            x -= width / 2
        scale = size / self.upm
        pen = SVGPathPen(self.gs)
        cx = x
        for ch in s:
            name = self.cmap.get(ord(ch))
            if name is None:
                raise SystemExit(f"Glyphe fehlt: {ch!r}")
            g = self.gs[name]
            if ch != " ":
                g.draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
            cx += g.width * scale + tracking * size
        return pen.getCommands()

    def width(self, s, size, tracking=0.0):
        scale = size / self.upm
        w = sum(self.gs[self.cmap[ord(ch)]].width * scale + tracking * size for ch in s)
        return w - tracking * size


MONO = Face(f"{FONTS}/talvesa-mono-regular.woff2")
BOLD = Face(f"{FONTS}/talvesa-mono-bold.woff2")

W, H = 1280, 560
THEMES = {
    "light": dict(bg="#F5F5F5", ink="11,11,11", solid="#0B0B0B", soft="#5C5C5C", accent="#873FA6"),
    "dark": dict(bg="#0B0B0B", ink="245,245,245", solid="#F5F5F5", soft="#A3A3A3", accent="#BE7ADB"),
}


def hero(t):
    ink = lambda a: f"rgba({t['ink']},{a})"  # noqa: E731
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        'aria-label="Gebaut, nicht behauptet. Websites, Web-Apps, mobile Apps und APIs aus Freiburg im Breisgau.">',
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
    ]

    def text(s, x, y, size, fill, face=MONO, tracking=0.0, anchor="start"):
        o.append(f'<path fill="{fill}" d="{face.path(s, x, y, size, tracking, anchor)}"/>')

    # Millimeterpapier: feines und grobes Raster.
    fine = [f"M{x} 0V{H}" for x in range(0, W + 1, 20)] + [f"M0 {y}H{W}" for y in range(0, H + 1, 20)]
    major = [f"M{x} 0V{H}" for x in range(0, W + 1, 100)] + [f"M0 {y}H{W}" for y in range(0, H + 1, 100)]
    o.append(f'<path d="{" ".join(fine)}" stroke="{ink(0.03)}" fill="none"/>')
    o.append(f'<path d="{" ".join(major)}" stroke="{ink(0.07)}" fill="none"/>')

    # Links: die Aussage.
    o.append(f'<rect x="72" y="82" width="10" height="10" fill="{t["accent"]}"/>')
    text("SOFTWARESTUDIO · FREIBURG IM BREISGAU", 94, 92, 13, t["soft"], tracking=0.22)
    for i, line in enumerate(["Gebaut,", "nicht", "behauptet"]):
        text(line, 66, 206 + i * 94, 88, t["solid"], face=BOLD, tracking=-0.02)
    x_end = 66 + BOLD.width("behauptet", 88, -0.02)
    o.append(f'<rect x="{x_end + 6:.1f}" y="{394 - 17}" width="15" height="15" fill="{t["accent"]}"/>')
    text("Websites · Web-Apps · Mobile Apps · APIs", 72, 446, 16, t["soft"], tracking=0.02)

    # Rechts: das Drahtmodell.
    line = ink(0.55)
    faint = ink(0.22)
    bx, by, bw, bh = 770, 120, 400, 272
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{t["bg"]}" stroke="{line}" stroke-width="1.5"/>')
    o.append(f'<path d="M{bx} {by + 26}H{bx + bw}" stroke="{line}"/>')
    for i in range(3):
        o.append(f'<circle cx="{bx + 16 + i * 14}" cy="{by + 13}" r="4" fill="none" stroke="{line}"/>')
    o.append(f'<rect x="{bx + 70}" y="{by + 7}" width="200" height="12" rx="6" fill="none" stroke="{faint}"/>')
    # Inhalt der Seite.
    o.append(f'<rect x="{bx + 20}" y="{by + 50}" width="190" height="16" fill="{ink(0.7)}"/>')
    for i, w in enumerate((210, 180, 196)):
        o.append(f'<rect x="{bx + 20}" y="{by + 80 + i * 12}" width="{w}" height="5" fill="{ink(0.22)}"/>')
    o.append(f'<rect x="{bx + 20}" y="{by + 128}" width="92" height="24" rx="3" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>')
    ix, iy, iw, ih = bx + 250, by + 46, 130, 106
    o.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="none" stroke="{faint}"/>')
    o.append(f'<path d="M{ix} {iy}L{ix + iw} {iy + ih}M{ix + iw} {iy}L{ix} {iy + ih}" stroke="{faint}"/>')
    for i in range(3):
        o.append(f'<rect x="{bx + 20 + i * 124}" y="{by + 172}" width="112" height="82" fill="none" stroke="{faint}"/>')
        o.append(f'<rect x="{bx + 30 + i * 124}" y="{by + 184}" width="60" height="5" fill="{ink(0.3)}"/>')
        o.append(f'<rect x="{bx + 30 + i * 124}" y="{by + 196}" width="84" height="4" fill="{ink(0.15)}"/>')

    # Das Telefon davor.
    px, py, pw, ph = 1098, 262, 112, 208
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" fill="{t["bg"]}" stroke="{line}" stroke-width="1.5"/>')
    o.append(f'<rect x="{px + 38}" y="{py + 8}" width="36" height="8" rx="4" fill="none" stroke="{faint}"/>')
    o.append(f'<rect x="{px + 12}" y="{py + 30}" width="70" height="10" fill="{ink(0.7)}"/>')
    for i, w in enumerate((88, 76, 84)):
        o.append(f'<rect x="{px + 12}" y="{py + 50 + i * 9}" width="{w}" height="4" fill="{ink(0.22)}"/>')
    o.append(f'<rect x="{px + 12}" y="{py + 86}" width="88" height="44" fill="none" stroke="{faint}"/>')
    o.append(f'<rect x="{px + 12}" y="{py + 164}" width="88" height="26" rx="3" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>')

    # Bemaßung über dem Browser.
    dy = 96
    o.append(f'<path d="M{bx} {dy}H{bx + bw}M{bx} {dy - 6}V{dy + 6}M{bx + bw} {dy - 6}V{dy + 6}" stroke="{ink(0.4)}"/>')
    label = "1280 px"
    lw = MONO.width(label, 11, 0.08) + 16
    o.append(f'<rect x="{bx + bw / 2 - lw / 2:.1f}" y="{dy - 8}" width="{lw:.1f}" height="16" fill="{t["bg"]}"/>')
    text(label, bx + bw / 2, dy + 4, 11, t["soft"], tracking=0.08, anchor="middle")
    # Bemaßung rechts am Telefon.
    dx = 1232
    o.append(f'<path d="M{dx} {py}V{py + ph}M{dx - 6} {py}H{dx + 6}M{dx - 6} {py + ph}H{dx + 6}" stroke="{ink(0.4)}"/>')
    o.append(f'<rect x="{dx - 9}" y="{py + ph / 2 - 26}" width="18" height="52" fill="{t["bg"]}"/>')
    o.append(f'<path fill="{t["soft"]}" transform="rotate(-90 {dx + 4} {py + ph / 2})" '
             f'd="{MONO.path("390 px", dx + 4, py + ph / 2, 11, 0.08, "middle")}"/>')

    # Beschriftungen: Führungslinie, Punkt am Ziel, Text.
    def callout(label, lx, ly, tx, ty, anchor="end"):
        start = lx + 8 if anchor == "end" else lx - 8
        mid = (tx - 18) if anchor == "end" else tx
        o.append(f'<path d="M{start} {ly - 4}H{mid}L{tx} {ty}" fill="none" stroke="{ink(0.4)}"/>')
        o.append(f'<circle cx="{tx}" cy="{ty}" r="7" fill="none" stroke="{t["accent"]}" stroke-opacity="0.45"/>')
        o.append(f'<circle cx="{tx}" cy="{ty}" r="3" fill="{t["accent"]}"/>')
        text(label, lx, ly, 12, t["solid"], tracking=0.04, anchor=anchor)

    callout("CSP: script-src 'self'", 738, 142, bx + 70, by + 13)
    callout("WCAG 2.2 AA · axe-core", 738, 214, bx + 20, by + 88)
    callout("0 Anfragen an Dritte", 738, 318, bx + 20, by + 213)

    # Unter dem Browser: zwei Angaben ohne Ziel am Rand.
    text("44 px Tap-Ziele", px - 20, py + 180, 12, t["solid"], tracking=0.04, anchor="end")
    o.append(f'<path d="M{px - 14} {py + 176}H{px + 12}" stroke="{ink(0.4)}"/>')
    o.append(f'<circle cx="{px + 12}" cy="{py + 176}" r="3" fill="{t["accent"]}"/>')
    text("Hosting: Deutschland", bx, by + bh + 38, 12, t["solid"], tracking=0.04)
    text("Budgets statt Scores", bx, by + bh + 58, 12, t["soft"], tracking=0.04)

    # Schriftfeld unten, wie auf einer Zeichnung.
    fy = 496
    o.append(f'<path d="M72 {fy}H1208" stroke="{ink(0.25)}"/>')
    text("47.9990° N · 7.8421° E", 72, fy + 34, 12, t["soft"], tracking=0.14)
    text("BLATT 01 · MASSSTAB 1:1", W / 2, fy + 34, 12, t["soft"], tracking=0.14, anchor="middle")
    s = 14 / EMBLEM_H
    lw = MONO.width("TALVESA.DE", 12, 0.14)
    ex = 1208 - lw - 12 - EMBLEM_W * s
    o.append(f'<path fill="{t["solid"]}" transform="translate({ex:.2f} {fy + 22}) scale({s:.5f})" d="{EMBLEM}"/>')
    text("TALVESA.DE", 1208, fy + 34, 12, t["solid"], tracking=0.14, anchor="end")

    o.append("</svg>")
    return "\n".join(o) + "\n"


# Blatt 02: die Stückliste. (Position, Benennung, Aufgabe, Menge)
PARTS = [
    ("01", "Python", "Rückgrat", "1"),
    ("02", "Django", "Server & API", "1"),
    ("03", "React", "Oberflächen, die was tun", "1"),
    ("04", "PostgreSQL", "Gedächtnis", "1"),
    ("05", "Docker", "Transport", "1"),
    ("06", "Vite + Sass", "Schliff", "1"),
    ("07", "Liebe zum Detail", "alles andere", "nicht verhandelbar"),
]


def parts(t):
    ink = lambda a: f"rgba({t['ink']},{a})"  # noqa: E731
    row_h, head = 40, 112
    h = head + row_h * (len(PARTS) + 1) + 70
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
        'aria-label="Stückliste: Python, Django, React, PostgreSQL, Docker, Vite und Sass – und Liebe zum Detail, nicht verhandelbar.">',
        f'<rect width="{W}" height="{h}" fill="{t["bg"]}"/>',
    ]

    def text(s, x, y, size, fill, face=MONO, tracking=0.0, anchor="start"):
        o.append(f'<path fill="{fill}" d="{face.path(s, x, y, size, tracking, anchor)}"/>')

    fine = [f"M{x} 0V{h}" for x in range(0, W + 1, 20)] + [f"M0 {y}H{W}" for y in range(0, h + 1, 20)]
    major = [f"M{x} 0V{h}" for x in range(0, W + 1, 100)] + [f"M0 {y}H{W}" for y in range(0, h + 1, 100)]
    o.append(f'<path d="{" ".join(fine)}" stroke="{ink(0.03)}" fill="none"/>')
    o.append(f'<path d="{" ".join(major)}" stroke="{ink(0.07)}" fill="none"/>')

    o.append(f'<rect x="72" y="50" width="10" height="10" fill="{t["accent"]}"/>')
    text("BLATT 02", 94, 60, 13, t["soft"], tracking=0.22)
    text("Stückliste", 72, 96, 34, t["solid"], face=BOLD, tracking=-0.01)

    left, right = 72, 1208
    cols = [left, 170, 520, 1000]  # POS, BENENNUNG, AUFGABE, MENGE
    top = head + 10
    o.append(f'<rect x="{left}" y="{top}" width="{right - left}" height="{row_h * (len(PARTS) + 1)}" fill="{t["bg"]}" stroke="{ink(0.45)}"/>')
    o.append(f'<rect x="{left}" y="{top}" width="{right - left}" height="{row_h}" fill="{ink(0.05)}"/>')
    for x in cols[1:]:
        o.append(f'<path d="M{x} {top}V{top + row_h * (len(PARTS) + 1)}" stroke="{ink(0.2)}"/>')
    for i in range(1, len(PARTS) + 1):
        o.append(f'<path d="M{left} {top + row_h * i}H{right}" stroke="{ink(0.2 if i == 1 else 0.1)}"/>')
    for x, label in zip(cols, ("POS", "BENENNUNG", "AUFGABE", "MENGE")):
        text(label, x + 20, top + 25, 11, t["soft"], tracking=0.22)
    for i, (pos, name, job, qty) in enumerate(PARTS, start=1):
        y = top + row_h * i + 26
        last = i == len(PARTS)
        text(pos, cols[0] + 20, y, 15, t["accent"] if last else t["soft"], tracking=0.06)
        text(name, cols[1] + 20, y, 17, t["solid"], face=BOLD if last else MONO)
        text(job, cols[2] + 20, y, 15, t["soft"])
        text(qty, cols[3] + 20, y, 15, t["accent"] if last else t["solid"], face=BOLD if last else MONO)

    fy = top + row_h * (len(PARTS) + 1) + 40
    text("GEPRÜFT: JA · FREIGEGEBEN: IMMER ERST NACH DEM TEST", 72, fy, 11, t["soft"], tracking=0.18)
    s = 14 / EMBLEM_H
    lw = MONO.width("TALVESA.DE", 12, 0.14)
    ex = 1208 - lw - 12 - EMBLEM_W * s
    o.append(f'<path fill="{t["solid"]}" transform="translate({ex:.2f} {fy - 12}) scale({s:.5f})" d="{EMBLEM}"/>')
    text("TALVESA.DE", 1208, fy, 12, t["solid"], tracking=0.14, anchor="end")
    o.append("</svg>")
    return "\n".join(o) + "\n"


os.makedirs(OUT, exist_ok=True)
for name, theme in THEMES.items():
    with open(f"{OUT}/hero-{name}.svg", "w") as fh:
        fh.write(hero(theme))
    with open(f"{OUT}/parts-{name}.svg", "w") as fh:
        fh.write(parts(theme))
print("ok")
