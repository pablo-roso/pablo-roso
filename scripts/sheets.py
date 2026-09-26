"""Blatt 01 (Hero), das Band darunter und Blatt 02 (Stückliste).

Blatt 01 ist eine technische Zeichnung, die sich einmal selbst zeichnet:
Raster, dann Browser und Telefon wie von einem Plotter, dann Maße und
Beschriftungen, zuletzt die Aussage. Danach steht das Bild still.
"""

from blueprint import BOLD, MONO, Sheet, anim

W_HALF = 640


def hero(t):
    sh = Sheet(t, 560, "Gebaut, nicht behauptet. Websites, Web-Apps, mobile Apps und APIs aus Freiburg im Breisgau.")
    ink = sh.ink
    sh.kicker("SOFTWARESTUDIO · FREIBURG IM BREISGAU", 72, 92, delay=0.2)
    sh.text("Websites · Web-Apps · Mobile Apps · APIs", 72, 446, 16, t["soft"], tracking=0.02, cls="f", delay=0.4)

    line, faint, bg = ink(0.55), ink(0.22), t["bg"]

    def stroke(el, delay, width=1):
        # Ein gezeichnetes Element: Kontur, die der Plotter abfährt.
        sh.add(el.replace("/>", f' fill="none" stroke-width="{width}"{anim("d", delay)}/>', 1))

    def bar(x, y, w, h, alpha, delay):
        sh.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{ink(alpha)}"{anim("g", delay)}/>')

    # Browser.
    bx, by, bw, bh = 770, 120, 400, 272
    sh.add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{bg}"{anim("f", 0.3)}/>')
    stroke(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" stroke="{line}"/>', 0.3, 1.5)
    stroke(f'<path d="M{bx} {by + 26}H{bx + bw}" stroke="{line}"/>', 0.8)
    for i in range(3):
        stroke(f'<circle cx="{bx + 16 + i * 14}" cy="{by + 13}" r="4" stroke="{line}"/>', 0.9 + i * 0.08)
    stroke(f'<rect x="{bx + 70}" y="{by + 7}" width="200" height="12" rx="6" stroke="{faint}"/>', 1.0)
    bar(bx + 20, by + 50, 190, 16, 0.7, 1.1)
    for i, w in enumerate((210, 180, 196)):
        bar(bx + 20, by + 80 + i * 12, w, 5, 0.22, 1.2 + i * 0.07)
    stroke(f'<rect x="{bx + 20}" y="{by + 128}" width="92" height="24" rx="3" stroke="{t["accent"]}"/>', 1.4, 1.5)
    ix, iy, iw, ih = bx + 250, by + 46, 130, 106
    stroke(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" stroke="{faint}"/>', 1.2)
    stroke(f'<path d="M{ix} {iy}L{ix + iw} {iy + ih}" stroke="{faint}"/>', 1.5)
    stroke(f'<path d="M{ix + iw} {iy}L{ix} {iy + ih}" stroke="{faint}"/>', 1.6)
    for i in range(3):
        stroke(f'<rect x="{bx + 20 + i * 124}" y="{by + 172}" width="112" height="82" stroke="{faint}"/>', 1.5 + i * 0.1)
        bar(bx + 30 + i * 124, by + 184, 60, 5, 0.3, 1.8 + i * 0.1)
        bar(bx + 30 + i * 124, by + 196, 84, 4, 0.15, 1.85 + i * 0.1)

    # Telefon davor.
    px, py, pw, ph = 1098, 262, 112, 208
    sh.add(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" fill="{bg}"{anim("f", 1.9)}/>')
    stroke(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" stroke="{line}"/>', 1.9, 1.5)
    stroke(f'<rect x="{px + 38}" y="{py + 8}" width="36" height="8" rx="4" stroke="{faint}"/>', 2.3)
    bar(px + 12, py + 30, 70, 10, 0.7, 2.3)
    for i, w in enumerate((88, 76, 84)):
        bar(px + 12, py + 50 + i * 9, w, 4, 0.22, 2.4 + i * 0.06)
    stroke(f'<rect x="{px + 12}" y="{py + 86}" width="88" height="44" stroke="{faint}"/>', 2.4)
    stroke(f'<rect x="{px + 12}" y="{py + 164}" width="88" height="26" rx="3" stroke="{t["accent"]}"/>', 2.5, 1.5)

    # Maße.
    dy = 96
    stroke(f'<path d="M{bx} {dy}H{bx + bw}" stroke="{ink(0.4)}"/>', 2.4)
    stroke(f'<path d="M{bx} {dy - 6}V{dy + 6}M{bx + bw} {dy - 6}V{dy + 6}" stroke="{ink(0.4)}"/>', 2.4)
    label = "1280 px"
    lw = MONO.width(label, 11, 0.08) + 16
    sh.add(f'<rect x="{bx + bw / 2 - lw / 2:.1f}" y="{dy - 8}" width="{lw:.1f}" height="16" fill="{bg}"{anim("f", 2.8)}/>')
    sh.text(label, bx + bw / 2, dy + 4, 11, t["soft"], tracking=0.08, anchor="middle", cls="f", delay=2.8)
    dx = 1232
    stroke(f'<path d="M{dx} {py}V{py + ph}M{dx - 6} {py}H{dx + 6}M{dx - 6} {py + ph}H{dx + 6}" stroke="{ink(0.4)}"/>', 2.6)
    sh.add(f'<g{anim("f", 3.0)}><rect x="{dx - 9}" y="{py + ph / 2 - 26}" width="18" height="52" fill="{bg}"/>'
           f'<path fill="{t["soft"]}" transform="rotate(-90 {dx + 4} {py + ph / 2})" '
           f'd="{MONO.path("390 px", dx + 4, py + ph / 2, 11, 0.08, "middle")}"/></g>')

    # Beschriftungen: Führungslinie, Punkt am Ziel, Text.
    def callout(label, lx, ly, tx, ty, delay):
        stroke(f'<path d="M{lx + 8} {ly - 4}H{tx - 18}L{tx} {ty}" stroke="{ink(0.4)}"/>', delay)
        sh.add(f'<circle cx="{tx}" cy="{ty}" r="7" fill="none" stroke="{t["accent"]}" stroke-opacity="0.45"{anim("p", delay + 0.5)}/>')
        sh.add(f'<circle cx="{tx}" cy="{ty}" r="3" fill="{t["accent"]}"{anim("p", delay + 0.45)}/>')
        sh.text(label, lx, ly, 12, t["solid"], tracking=0.04, anchor="end", cls="f", delay=delay + 0.2)

    callout("CSP: script-src 'self'", 738, 142, bx + 70, by + 13, 2.7)
    callout("WCAG 2.2 AA · axe-core", 738, 214, bx + 20, by + 88, 2.85)
    callout("0 Anfragen an Dritte", 738, 318, bx + 20, by + 213, 3.0)
    sh.text("44 px Tap-Ziele", px - 20, py + 180, 12, t["solid"], tracking=0.04, anchor="end", cls="f", delay=3.2)
    stroke(f'<path d="M{px - 14} {py + 176}H{px + 12}" stroke="{ink(0.4)}"/>', 3.1)
    sh.add(f'<circle cx="{px + 12}" cy="{py + 176}" r="3" fill="{t["accent"]}"{anim("p", 3.5)}/>')
    sh.text("Hosting: Deutschland", bx, by + bh + 38, 12, t["solid"], tracking=0.04, cls="f", delay=3.3)
    sh.text("Budgets statt Scores", bx, by + bh + 58, 12, t["soft"], tracking=0.04, cls="f", delay=3.4)

    # Zuletzt: die Aussage.
    for i, word in enumerate(["Gebaut,", "nicht", "behauptet"]):
        sh.text(word, 66, 206 + i * 94, 88, t["solid"], face=BOLD, tracking=-0.02, cls="s", delay=3.5 + i * 0.16)
    x_end = 66 + BOLD.width("behauptet", 88, -0.02)
    sh.add(f'<rect x="{x_end + 6:.1f}" y="377" width="15" height="15" fill="{t["accent"]}"{anim("p", 4.1)}/>')

    # Schriftfeld.
    fy = 496
    stroke(f'<path d="M72 {fy}H1208" stroke="{ink(0.25)}"/>', 0.2)
    sh.text("47.9990° N · 7.8421° E", 72, fy + 34, 12, t["soft"], tracking=0.14, cls="f", delay=0.6)
    sh.text("BLATT 01 · MASSSTAB 1:1", W_HALF, fy + 34, 12, t["soft"], tracking=0.14, anchor="middle", cls="f", delay=0.7)
    sh.signature(fy + 34, delay=0.8)
    return sh


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
    row_h, head = 40, 112
    top = head + 10
    rows = len(PARTS) + 1
    h = top + row_h * rows + 78
    sh = Sheet(t, h, "Stückliste: Python, Django, React, PostgreSQL, Docker, Vite und Sass – und Liebe zum Detail, nicht verhandelbar.")
    ink = sh.ink
    sh.kicker("BLATT 02", 72, 60, delay=0.1)
    sh.text("Stückliste", 72, 96, 34, t["solid"], face=BOLD, tracking=-0.01, cls="r", delay=0.2)

    left, right = 72, 1208
    cols = [left, 170, 520, 1000]
    sh.add(f'<rect x="{left}" y="{top}" width="{right - left}" height="{row_h * rows}" fill="{t["bg"]}" stroke="{ink(0.45)}"/>')
    sh.add(f'<rect x="{left}" y="{top}" width="{right - left}" height="{row_h}" fill="{ink(0.05)}"/>')
    for x in cols[1:]:
        sh.add(f'<path d="M{x} {top}V{top + row_h * rows}" stroke="{ink(0.2)}"/>')
    for i in range(1, len(PARTS) + 1):
        sh.add(f'<path d="M{left} {top + row_h * i}H{right}" stroke="{ink(0.2 if i == 1 else 0.1)}"/>')
    for x, label in zip(cols, ("POS", "BENENNUNG", "AUFGABE", "MENGE")):
        sh.text(label, x + 20, top + 25, 11, t["soft"], tracking=0.22)
    for i, (pos, name, job, qty) in enumerate(PARTS, start=1):
        y = top + row_h * i + 26
        last = i == len(PARTS)
        sh.add(f'<g{anim("r", 0.3 + i * 0.09)}>')
        sh.text(pos, cols[0] + 20, y, 15, t["accent"] if last else t["soft"], tracking=0.06)
        sh.text(name, cols[1] + 20, y, 17, t["solid"], face=BOLD if last else MONO)
        sh.text(job, cols[2] + 20, y, 15, t["soft"])
        sh.text(qty, cols[3] + 20, y, 15, t["accent"] if last else t["solid"], face=BOLD if last else MONO)
        sh.add("</g>")

    fy = top + row_h * rows + 40
    sh.text("GEPRÜFT: JA · FREIGEGEBEN: IMMER ERST NACH DEM TEST", 72, fy, 11, t["soft"], tracking=0.18)
    sh.signature(fy)
    return sh



def band(t):
    """Die Zeile zwischen Blatt 01 und 02: was wir machen, wo."""
    sh = Sheet(t, 140, "Websites, Web-Apps und Apps, von der ersten Skizze bis live. Gebaut in Freiburg, bei Talvesa.")
    sh.add(f'<path d="M72 40H1208M72 {140 - 20}H1208" stroke="{sh.ink(0.12)}" stroke-dasharray="4 6"/>')
    sh.text("Websites, Web-Apps und Apps — von der ersten Skizze bis live.", W_HALF, 78, 19, t["solid"],
            anchor="middle", cls="f", delay=4.3)
    sh.text("Gebaut in Freiburg, bei Talvesa.", W_HALF, 104, 15, t["soft"], anchor="middle", cls="f", delay=4.4)
    return sh
