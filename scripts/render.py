"""Zeichnet das ganze Profil als ein Blatt nach assets/profile-{light,dark}.svg.

Blatt 01 (Hero), das Band, Blatt 02 (Stückliste) und Blatt 03
(Jahresbilanz) liegen auf einem Papier: Hintergrund und Raster laufen ohne
Lücke durch, weil GitHub zwischen einzelnen Bildern Abstand setzt.

    pip install fonttools brotli
    GITHUB_TOKEN=… python scripts/render.py      # echte Beiträge
    python scripts/render.py --demo              # Beispieldaten
"""

import sys
from datetime import date
from pathlib import Path

from blueprint import THEMES, compose
from sheets import band, hero, parts
from skyline import demo, fetch, skyline

OUT = Path("assets")


def main():
    weeks = demo() if "--demo" in sys.argv else fetch()
    # Ein leeres Jahr heißt fast immer: der Token sieht die Beiträge nicht.
    # Dann bleibt das alte Blatt stehen, statt eine Null zu veröffentlichen.
    if sum(c for w in weeks for _, c, _ in w) == 0:
        raise SystemExit("Keine Beiträge sichtbar – SKYLINE_TOKEN (read:user) als Secret hinterlegen.")
    today = date.today()
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        svg = compose(t, [hero(t), band(t), parts(t), skyline(weeks, today, t)])
        (OUT / f"profile-{name}.svg").write_text(svg)
    print("ok")


if __name__ == "__main__":
    main()
