"""Zeichnet Blatt 03 (Jahresbilanz) nach assets/skyline-*.svg.

Die Beiträge der letzten zwölf Monate als isometrische Stadt: jeder Tag ein
Block, seine Höhe die Zahl der Beiträge. Die Daten kommen aus dem
Beitragskalender der GitHub-GraphQL-API; die Action in
.github/workflows/skyline.yml zeichnet das Blatt jede Nacht neu.

    GITHUB_TOKEN=… python scripts/render-skyline.py          # echte Daten
    python scripts/render-skyline.py --demo                   # Beispieldaten

Private Beiträge zählen mit, wenn im Profil „Private contributions“ sichtbar
geschaltet ist; übertragen werden nur Zahlen pro Tag, keine Repositories.
"""

import json
import math
import os
import random
import sys
import urllib.request
from datetime import date, timedelta

from blueprint import BOLD, Sheet, anim, write_both

OUT = "assets"
LOGIN = os.environ.get("PROFILE_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER")
WEEKDAYS = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch():
    """Die Wochen des Kalenders als Liste von Listen (date, count, weekday)."""
    token = os.environ.get("GITHUB_TOKEN")
    if not LOGIN:
        raise SystemExit("PROFILE_LOGIN fehlt (in der Action: GITHUB_REPOSITORY_OWNER).")
    if not token:
        raise SystemExit("GITHUB_TOKEN fehlt (oder --demo verwenden).")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if body.get("errors"):
        raise SystemExit(f"GraphQL-Fehler: {body['errors']}")
    cal = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [
        [(date.fromisoformat(d["date"]), d["contributionCount"], d["weekday"]) for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]


def demo():
    """Plausible Beispieldaten, damit sich das Blatt ohne Token prüfen lässt."""
    rnd = random.Random(7)
    end = date.today()
    start = end - timedelta(days=364 + (end.weekday() + 1) % 7)
    weeks, week = [], []
    d = start
    while d <= end:
        wd = (d.weekday() + 1) % 7
        base = 0 if wd in (0, 6) and rnd.random() < 0.6 else rnd.choice([0, 1, 2, 3, 5, 8, 12])
        burst = 18 + rnd.randint(0, 30) if rnd.random() < 0.04 else 0
        week.append((d, base + burst, wd))
        if wd == 6:
            weeks.append(week)
            week = []
        d += timedelta(days=1)
    if week:
        weeks.append(week)
    return weeks


def stats(weeks):
    days = [d for w in weeks for d in w]
    total = sum(c for _, c, _ in days)
    record = max(days, key=lambda x: x[1])
    streak = best = 0
    for _, c, _ in days:
        streak = streak + 1 if c else 0
        best = max(best, streak)
    per_wd = [0] * 7
    for _, c, wd in days:
        per_wd[wd] += c
    active = sum(1 for _, c, _ in days if c)
    return dict(total=total, record=record, streak=best, weekday=per_wd.index(max(per_wd)), active=active, days=len(days))


def num(n):
    return f"{n:,}".replace(",", ".")


def blend(fg, bg, a):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * a + y * (1 - a)):02X}" for x, y in zip(f, b))


def skyline(weeks, today):
    st = stats(weeks)
    peak = max(st["record"][1], 1)

    def draw(t):
        h = 640
        sh = Sheet(t, h, f"Jahresbilanz: {num(st['total'])} Beiträge in zwölf Monaten, Rekord {st['record'][1]} an einem Tag, "
                         f"längste Serie {st['streak']} Tage.")
        ink = sh.ink
        sh.grid()
        sh.kicker("BLATT 03", 72, 60, delay=0.1)
        sh.text("Jahresbilanz", 72, 96, 34, t["solid"], face=BOLD, tracking=-0.01, cls="r", delay=0.2)
        sh.text("JEDER BLOCK EIN TAG · HÖHE = BEITRÄGE", 72, 124, 11, t["soft"], tracking=0.2, cls="f", delay=0.3)

        # Kennzahlen links.
        rows = [
            (num(st["total"]), "Beiträge in 12 Monaten"),
            (str(st["record"][1]), f"Rekord am {st['record'][0]:%d.%m.%Y}"),
            (str(st["streak"]), "Tage längste Serie"),
            (f"{round(100 * st['active'] / st['days'])} %", "der Tage mit Beiträgen"),
            (f"{st['total'] / max(st['active'], 1):.1f}".replace(".", ","), f"pro aktivem Tag, am meisten {WEEKDAYS[st['weekday']]}s"),
        ]
        for i, (big, small) in enumerate(rows):
            y = 200 + i * 78
            sh.add(f'<g{anim("r", 0.4 + i * 0.12)}>')
            sh.text(big, 72, y, 40, t["accent"] if i == 0 else t["solid"], face=BOLD, tracking=-0.02)
            sh.text(small, 72, y + 24, 12, t["soft"], tracking=0.04)
            sh.add("</g>")
        sh.add(f'<path d="M380 160V560" stroke="{ink(0.18)}"/>')

        # Die Stadt.
        ux, uy, vx, vy = 12.4, 3.0, 7.2, -4.6
        ox, oy = 440, 378
        gap = 0.82
        faces = {
            "light": dict(top="#FFFFFF", front="#D2D2D2", right="#A6A6A6", edge="rgba(11,11,11,0.4)"),
            "dark": dict(top="#EDEDED", front="#9A9A9A", right="#5E5E5E", edge="rgba(11,11,11,0.5)"),
        }["light" if t["bg"] == "#F5F5F5" else "dark"]
        acc = dict(top=blend(t["accent"], "#FFFFFF", 0.75), front=t["accent"], right=blend(t["accent"], "#000000", 0.7),
                   edge=faces["edge"])

        def pt(x, y):
            return f"{x:.1f},{y:.1f}"

        cells = []
        for w, week in enumerate(weeks):
            for d, count, wd in week:
                cells.append((w * uy + wd * vy, w, wd, d, count))
        cells.sort(key=lambda c: (c[0], c[1]))

        for _, w, wd, d, count in cells:
            px = ox + w * ux + wd * vx
            py = oy + w * uy + wd * vy
            aU, aV = (ux * gap, uy * gap), (vx * gap, vy * gap)
            p0 = (px, py)
            p1 = (px + aU[0], py + aU[1])
            p2 = (p1[0] + aV[0], p1[1] + aV[1])
            p3 = (px + aV[0], py + aV[1])
            if count == 0:
                sh.add(f'<polygon points="{pt(*p0)} {pt(*p1)} {pt(*p2)} {pt(*p3)}" fill="none" stroke="{ink(0.14)}"{anim("f", 0.3 + w * 0.02)}/>')
                continue
            hh = 5 + 175 * math.sqrt(count / peak)
            is_rec = d == st["record"][0]
            is_today = d == today
            c = acc if is_rec or is_today else faces
            up = lambda p: (p[0], p[1] - hh)  # noqa: E731
            sh.add(f'<g stroke="{c["edge"]}" stroke-width="0.6" stroke-linejoin="round"{anim("r", 0.3 + w * 0.03)}>')
            sh.add(f'<polygon points="{pt(*p0)} {pt(*p1)} {pt(*up(p1))} {pt(*up(p0))}" fill="{c["front"]}"/>')
            sh.add(f'<polygon points="{pt(*p1)} {pt(*p2)} {pt(*up(p2))} {pt(*up(p1))}" fill="{c["right"]}"/>')
            sh.add(f'<polygon points="{pt(*up(p0))} {pt(*up(p1))} {pt(*up(p2))} {pt(*up(p3))}" fill="{c["top"]}"/>')
            sh.add("</g>")
            if is_rec:
                tx, ty = up(p0)[0] + aU[0] / 2 + aV[0] / 2, up(p0)[1] + aU[1] / 2 + aV[1] / 2
                ly = min(ty - 40, 190)
                delay = 0.5 + w * 0.03
                sh.add(f'<path d="M{tx:.1f} {ty - 4:.1f}V{ly}H{tx + 24:.1f}" fill="none" stroke="{t["accent"]}"{anim("d", delay)}/>')
                sh.add(f'<circle cx="{tx:.1f}" cy="{ty - 4:.1f}" r="3" fill="{t["accent"]}"{anim("p", delay)}/>')
                sh.text(f"REKORD · {count}", tx + 30, ly + 4, 12, t["solid"], face=BOLD, tracking=0.1, cls="f", delay=delay + 0.4)

        # Monatsmarken an der Vorderkante.
        seen = set()
        for w, week in enumerate(weeks):
            first = week[0][0]
            if first.day <= 7 and first.month not in seen:
                seen.add(first.month)
                mx = ox + w * ux - 4
                my = oy + w * uy + 20
                sh.text(f"{first:%m}", mx, my, 10, t["soft"], tracking=0.1, cls="f", delay=0.3)

        fy = h - 40
        sh.add(f'<path d="M72 {fy - 30}H1208" stroke="{ink(0.25)}"/>')
        sh.text(f"STAND {today:%d.%m.%Y} · WIRD JEDE NACHT NEU GEZEICHNET", 72, fy, 11, t["soft"], tracking=0.18)
        sh.signature(fy)
        return sh.svg()

    return draw


if __name__ == "__main__":
    weeks = demo() if "--demo" in sys.argv else fetch()
    write_both(OUT, "skyline", skyline(weeks, date.today()))
    print("ok", stats(weeks)["total"])
