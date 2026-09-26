"""Gemeinsames Werkzeug der Blätter: Schrift als Pfade, Farben, Raster, Zeichen.

Text wird mit fontTools in Pfade umgewandelt (Talvesa Mono, OFL, in fonts/),
damit GitHub keine Schrift laden muss.
"""

import os
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(os.environ.get("TALVESA_FONTS", ROOT / "fonts"))

EMBLEM = (
    "M39.154 23.238 15.259 23.238 0 0 106.715 0 91.455 23.238 67.15 23.238 "
    "105.453 81.569 91.455 102.887ZM119.451 60.337 105.453 39.02 131.076 0 159.072 0Z"
)
EMBLEM_W, EMBLEM_H = 159.072, 102.887

W = 1280
THEMES = {
    "light": dict(bg="#F5F5F5", ink="11,11,11", solid="#0B0B0B", soft="#5C5C5C", accent="#873FA6"),
    "dark": dict(bg="#0B0B0B", ink="245,245,245", solid="#F5F5F5", soft="#A3A3A3", accent="#BE7ADB"),
}

# Bewegung: jedes Blatt baut sich einmal auf und steht dann still. Der Grund-
# zustand jeder Klasse ist das fertige Bild, also zeigt „Bewegung reduzieren“
# sofort das Ergebnis.
MOTION = """<style>
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes fade{from{opacity:0}}
@keyframes grow{from{transform:scaleX(0)}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes pop{0%{opacity:0;transform:scale(0)}70%{transform:scale(1.35)}100%{opacity:1;transform:scale(1)}}
@keyframes slam{0%{opacity:0;transform:translateY(34px) scale(1.04)}100%{opacity:1;transform:none}}
.d{stroke-dasharray:1;animation:draw .9s cubic-bezier(.6,0,.2,1) both}
.f{animation:fade .6s ease both}
.g{transform-box:fill-box;transform-origin:0 50%;animation:grow .55s cubic-bezier(.2,.8,.2,1) both}
.r{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
.p{transform-box:fill-box;transform-origin:50% 50%;animation:pop .45s ease-out both}
.s{transform-box:fill-box;transform-origin:0 100%;animation:slam .55s cubic-bezier(.2,.9,.2,1) both}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


class Face:
    def __init__(self, path):
        font = TTFont(path)
        self.gs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm

    def width(self, s, size, tracking=0.0):
        scale = size / self.upm
        w = sum(self._glyph(ch).width * scale + tracking * size for ch in s)
        return w - tracking * size

    def _glyph(self, ch):
        name = self.cmap.get(ord(ch))
        if name is None:
            raise SystemExit(f"Glyphe fehlt: {ch!r}")
        return self.gs[name]

    def path(self, s, x, y, size, tracking=0.0, anchor="start"):
        """Pfad für `s` mit Grundlinie y; anchor start|end|middle."""
        if anchor == "end":
            x -= self.width(s, size, tracking)
        elif anchor == "middle":
            x -= self.width(s, size, tracking) / 2
        scale = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        for ch in s:
            g = self._glyph(ch)
            if ch != " ":
                g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
            x += g.width * scale + tracking * size
        return pen.getCommands()


MONO = Face(FONTS / "talvesa-mono-regular.woff2")
BOLD = Face(FONTS / "talvesa-mono-bold.woff2")


def anim(cls, delay):
    """Attribute für eine Animation mit Verzögerung; leer ohne Klasse."""
    if not cls:
        return ""
    extra = ' pathLength="1"' if cls == "d" else ""
    return f' class="{cls}" style="animation-delay:{delay:.2f}s"{extra}'


class Sheet:
    """Ein Blatt: sammelt SVG-Elemente in einem Thema."""

    def __init__(self, theme, height, label):
        self.t = theme
        self.h = height
        self.o = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img" aria-label="{label}">',
            MOTION,
            f'<rect width="{W}" height="{height}" fill="{theme["bg"]}"/>',
        ]

    def ink(self, a):
        return f"rgba({self.t['ink']},{a})"

    def add(self, el):
        self.o.append(el)

    def text(self, s, x, y, size, fill, face=MONO, tracking=0.0, anchor="start", cls="", delay=0.0):
        d = face.path(s, x, y, size, tracking, anchor)
        self.o.append(f'<path fill="{fill}" d="{d}"{anim(cls, delay)}/>')

    def grid(self, cls="f", delay=0.0):
        h = self.h
        fine = [f"M{x} 0V{h}" for x in range(0, W + 1, 20)] + [f"M0 {y}H{W}" for y in range(0, h + 1, 20)]
        major = [f"M{x} 0V{h}" for x in range(0, W + 1, 100)] + [f"M0 {y}H{W}" for y in range(0, h + 1, 100)]
        self.o.append(f'<g{anim(cls, delay)}>')
        self.o.append(f'<path d="{" ".join(fine)}" stroke="{self.ink(0.03)}" fill="none"/>')
        self.o.append(f'<path d="{" ".join(major)}" stroke="{self.ink(0.07)}" fill="none"/>')
        self.o.append("</g>")

    def kicker(self, label, x, y, cls="f", delay=0.0):
        self.o.append(f'<rect x="{x}" y="{y - 10}" width="10" height="10" fill="{self.t["accent"]}"{anim(cls, delay)}/>')
        self.text(label, x + 22, y, 13, self.t["soft"], tracking=0.22, cls=cls, delay=delay)

    def signature(self, y, cls="f", delay=0.0):
        """Talvesa-Zeichen und Adresse rechts unten."""
        s = 14 / EMBLEM_H
        lw = MONO.width("TALVESA.DE", 12, 0.14)
        ex = 1208 - lw - 12 - EMBLEM_W * s
        self.o.append(f'<g{anim(cls, delay)}>')
        self.o.append(f'<path fill="{self.t["solid"]}" transform="translate({ex:.2f} {y - 12}) scale({s:.5f})" d="{EMBLEM}"/>')
        self.text("TALVESA.DE", 1208, y, 12, self.t["solid"], tracking=0.14, anchor="end")
        self.o.append("</g>")

    def svg(self):
        return "\n".join(self.o + ["</svg>"]) + "\n"


def write_both(out, name, draw):
    """Zeichnet ein Blatt in beiden Themen nach assets/<name>-<thema>.svg."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for theme_name, theme in THEMES.items():
        (out / f"{name}-{theme_name}.svg").write_text(draw(theme))
