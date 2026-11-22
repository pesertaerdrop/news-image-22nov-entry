"""Front page for news-image-20261122 — "THE WORLD IN ONE DAY".

One-page broadsheet summing up Sunday 22 November 2026: 36 stories,
7 regions, 3 hero leads, 12 small leads, a UTC timeline bar, a dotted
world map with numbered pins, a DATE CHECK box and a sources line.
Every picture is drawn fresh in code with Pillow primitives (flat
shapes, no photos, no network, no embedded images). Deterministic:
the same bytes on every run. Output: entry.png, 1024x1024 RGB.

Editorial notes (verified live 2026-11-22, wires to 20:15 UTC):
- Hero 1 is the FRESH overnight raid (186 drones, Sat->Sun), not the
  stale 400-drone barrage of Thu 19-Fri 20 Nov, which DATE CHECK
  explicitly excludes. Dymer toll uses the later wires (3 killed,
  14 missing), not the early-morning figures.
- Hero 2: COP31's final text names no fossil fuels AND the deal was
  REJECTED on Sunday — the cover decision was not adopted. The
  headline says so; the top-1 rival's "deal lands" is wrong.
- Hero 3 is a CLAIM, labelled as such; Bahrain's account (a fire at
  a civilian industrial site, two injured) is given alongside it.
- Certainty is labelled on every illustrated lead: REPORTED = carried
  by the day's wires, CLAIM = one side's account, FORECAST = still to
  happen when drawn. The legend sits in the footer.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MX = 12
CW = W - 2 * MX

PAPER = (247, 242, 232)
INK = (26, 26, 26)
RED = (178, 34, 34)
NAVY = (25, 36, 66)
GREY = (96, 96, 92)
RULE = (120, 112, 98)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_fonts = {}


def get_font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(d, text, f, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, f, max_w, max_lines):
    """Wrap; step the font down until it fits max_lines (floor 8pt)."""
    size = f.size
    while size > 8:
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
        f = get_font(f.path, size)
    return wrap(d, text, f, max_w), f


def draw_text(d, x, y, text, f, max_w, max_lines, fill=INK, lh=None):
    """Draw wrapped text; return the y just below the last line."""
    lines, f2 = fit(d, text, f, max_w, max_lines)
    step = lh if lh is not None else int(f2.size * 1.22)
    for line in lines:
        d.text((x, y), line, font=f2, fill=fill)
        y += step
    return y


def tag_pill(d, x, y, text, f, fg, bg, pad_x=6, pad_y=2):
    """Rounded label; returns its right edge."""
    tw = d.textlength(text, font=f)
    th = f.size + 2 * pad_y
    d.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + th], radius=th // 2,
                        fill=bg)
    d.text((x + pad_x, y + pad_y - 1), text, font=f, fill=fg)
    return x + tw + 2 * pad_x


# ------------------------------------------------------------------ data
SUBLINE = ("186 drones over Ukraine in the night \u00b7 COP31 ends with "
           "no deal \u00b7 Iran's radar claim meets Bahrain's denial")

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed by air defence"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total in NZ"),
    ("50", "Wembanyama points, 19 rebounds"),
]

REGIONS = [
    ("EUROPE 8", 8, (38, 70, 139)),
    ("MIDDLE EAST 4", 4, (178, 34, 34)),
    ("AMERICAS 7", 7, (44, 116, 92)),
    ("ASIA-PACIFIC 9", 9, (196, 138, 30)),
    ("AFRICA 3", 3, (121, 70, 37)),
    ("OCEANIA 3", 3, (38, 120, 110)),
    ("WORLD 2", 2, (124, 92, 168)),
]

UTC_BAR = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections close"),
    ("05:11", "Hamas seeks talks"),
    ("05:30", "Verstappen wins Vegas"),
    ("06:00", "COP31 approval due"),
    ("07:30", "Approval slips again"),
]

# (tag, pill, source, kicker, headline, sub, certainty)
HEROES = [
    ("186 DRONES OVERNIGHT", "161 DOWNED", "Ukrainian Air Force",
     "1  KYIV REGION, UKRAINE \u00b7 WAR",
     "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "161 of 186 drones downed, 72 jet-powered. A block in Dymer "
     "falls: 3 killed, 14 missing. (Ukrainian Air Force)",
     "REPORTED"),
    ("COP31: NO DEAL", "NO FOSSIL FUELS", "COP31 presidency",
     "2  ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE",
     "COP31 ends with no deal as fossil fuels are left out",
     "'Recalls' Dubai, keeps 35%, drops $120bn, admits 1.5\u00b0C "
     "will be overshot. The EU refuses it. (Reuters, BBC)",
     "REPORTED"),
    ("CLAIM VS DENIAL", "2 RADARS?", "IRGC / Bahrain",
     "3  MANAMA, BAHRAIN \u00b7 IRAN",
     "Iran claims two US radars hit; Bahrain denies it",
     "IRGC says it hit two Patriot radars. Bahrain: a civilian "
     "site burned, two injured. (Khaleej Times, Al Jazeera)",
     "CLAIM"),
]

# (number, tag, source, kicker, headline, sub, certainty)
SMALLS = [
    (4, "856 CANDIDATES", "SCMP", "4  HONG KONG \u00b7 ELECTION",
     "Hong Kong elects its Election Committee",
     "856 candidates, 723 seats; polls 09:00\u201318:00.",
     "REPORTED"),
    (5, "720/9 DECLARED", "ESPN", "5  WELLINGTON \u00b7 CRICKET",
     "India declare on 720/9, a record in New Zealand",
     "Rahul 136, Pant 128; hosts 119/2, trailing by 233.",
     "REPORTED"),
    (6, "VERSTAPPEN WINS", "FIA", "6  LAS VEGAS \u00b7 FORMULA 1",
     "Verstappen takes the Las Vegas Grand Prix",
     "From pole, 35 lead changes; Norris +0.639, Piastri +1.529.",
     "REPORTED"),
    (7, "50 POINTS", "Reuters", "7  SAN ANTONIO \u00b7 NBA",
     "Wembanyama scores 50 as the Spurs roll on",
     "50 pts, 19 rebounds, 5 blocks; 114\u201391 over New Orleans.",
     "REPORTED"),
    (8, "SHIP ABLAZE", "Reuters", "8  GULF OF FINLAND \u00b7 SEA",
     "Russian cargo ship Sparta II still burning",
     "Hit by drones Saturday; Finland leads Loviisa rescue.",
     "REPORTED"),
    (9, "POWER CUTS", "Wires", "9  TEHRAN, IRAN \u00b7 ENERGY",
     "Iran begins rationing electricity",
     "Rolling cuts up to two hours a day as war damage bites.",
     "REPORTED"),
    (10, "IN INTENSIVE CARE", "Reuters", "10  BRAS\u00cdLIA, BRAZIL \u00b7 HEALTH",
     "Bolsonaro in intensive care in Bras\u00edlia",
     "Acute bowel obstruction; stable; surgery possible.",
     "REPORTED"),
    (11, "FBI PROBE", "AP", "11  WASHINGTON \u00b7 CYBER",
     "FBI probes apparent hack of its crime database",
     "State pauses gun-dealer checks; breach assessed.",
     "REPORTED"),
    (12, "FLIGHTS GROUNDED", "Wires", "12  BRUSSELS \u00b7 TRAVEL",
     "Belgian controllers join Monday's national strike",
     "Most flights grounded 07:00\u201321:00; controllers walk out.",
     "REPORTED"),
    (13, "TOLL AT 19", "Xinhua", "13  MANIPUR, INDIA \u00b7 POISONING",
     "Toxic-liquor toll in Manipur climbs to 19",
     "600 in hospital, six held; toll up from 16 on Saturday.",
     "REPORTED"),
    (14, "3 DEAD, 36 MISSING", "Detiknews", "14  CIKANDE, INDONESIA \u00b7 FIRE",
     "Candy-factory fire in Cikande: 3 dead, 36 missing",
     "Blaze tore through the Banten plant; search goes on.",
     "REPORTED"),
    (15, "1 DEAD, 16 HURT", "Reuters", "15  JUN\u00cdN, PERU \u00b7 QUAKE TOLL",
     "Peru quake toll updated: 1 dead, 16 hurt",
     "170 homes damaged in Jun\u00edn; the count is completed.",
     "REPORTED"),
]

# (number, one-line brief) — numbers 16..36, two columns of 11 and 10
BRIEFS = [
    (16, "Europe: Estonia to shut five Russia crossings 1 Dec (Reuters)"),
    (17, "Europe: Denmark expels Russian attach\u00e9 (Guardian)"),
    (18, "Asia-Pacific: Nepal PM Shah lands in Delhi (IANS)"),
    (19, "Asia-Pacific: Chinese bomber turns back (AP)"),
    (20, "Asia-Pacific: Philippines M5.9 quake off Palawan (EMSC)"),
    (21, "Asia-Pacific: Japan poll: 92% friendly to S. Korea (IKN)"),
    (22, "Asia-Pacific: Taiwan live-fire drill on Kinmen (CNA)"),
    (23, "Africa: Somalia expels UAE ambassador (Wires)"),
    (24, "Africa: Sudan: RSF accused of killing civilians (Claim)"),
    (25, "Africa: Kenya discharges last Ebola patient (Wires)"),
    (26, "Oceania: Marles rejects US report on AUKUS (ABC)"),
    (27, "Oceania: Melbourne: 70 years since 1956 Olympics (ABC)"),
    (28, "Oceania: Cummins keeps Australia's captaincy (Wires)"),
    (29, "Americas: Trump seeks 'permanent' Iran deal (Al Jazeera)"),
    (30, "Middle East: Eisenkot invites Likud to talks (Straits Times)"),
    (31, "Americas: Nvidia faces SEC probe, say reports (Reports)"),
    (32, "Middle East: Hamas seeks urgent mediator talks (Al Jazeera)"),
    (33, "World: Bitcoin back above $60,000 (Market data)"),
    (34, "World: Gold holds near $3,535 (Reuters)"),
    (35, "Europe \u00b7 FORECAST: ATP final: Zverev v Alcaraz (Forecast)"),
    (36, "Europe \u00b7 FORECAST: Liverpool host Man Utd (Forecast)"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Wires read to 20:15 UTC, Sun 22 Nov 2026. "
    "Every story here was reported, or still developing, on 22 Nov "
    "somewhere in the world. Kept out: the 400-drone barrage "
    "(19\u201320 Nov); Kryvyi Rih (20 Nov); 'El Chapo Isidro' (Fri); "
    "Bayelsa boat, 24 dead (Fri); Gaza aid-van strike (Sat); Poland "
    "missiles (19 Nov); Kerch Bridge (earlier); Shenzhen summit "
    "(19 Nov).")

SOURCES_LINE = (
    "Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky "
    "News, CNA, ABC, TOI, Guardian, Kyiv Ind., ISNA, ESPN, FIA, "
    "SCMP, Detiknews, Xinhua, EMSC. Pictures: original, drawn in "
    "code.")

CERTAINTY_LEGEND = (
    "CERTAINTY: REPORTED = carried by the day's wires \u00b7 CLAIM = "
    "one side's account, labelled as such \u00b7 FORECAST = still to "
    "happen when drawn")


# ------------------------------------------------------------------ art
def flame(d, cx, base, w, h, cols=((255, 170, 0), (255, 110, 0), (220, 40, 20))):
    """A small stylised flame: three stacked teardrops."""
    for i, c in enumerate(cols):
        fw = w * (1 - i * 0.28)
        fh = h * (1 - i * 0.22)
        d.polygon([(cx - fw / 2, base), (cx, base - fh),
                   (cx + fw / 2, base)], fill=c)
        d.ellipse([cx - fw * 0.32, base - fh * 0.55, cx + fw * 0.32,
                   base - fh * 0.05], fill=c)


def smoke(d, cx, cy, r, col=(70, 70, 72)):
    for dx, dy, rr in ((-14, 6, 9), (0, -4, 12), (14, 4, 9), (4, -14, 10)):
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr,
                   cy + dy + rr], fill=col)


def hero_drones(d, x, y, w, h):
    """Night raid: dark sky, lit skyline, fires, drone streaks."""
    for i in range(h):  # dusk sky: deep navy to burnt orange at horizon
        t = i / h
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((12, 16, 44), (150, 70, 30)))
        d.line([(x, y + i), (x + w, y + i)], fill=c)
    # drone streaks
    for sx, sy, ln, ang in ((40, 8, 34, 0.5), (110, 2, 44, 0.45),
                            (180, 12, 30, 0.55), (250, 4, 40, 0.5),
                            (300, 16, 28, 0.6)):
        ex = sx + ln * math.cos(ang)
        ey = sy + ln * math.sin(ang)
        d.line([(x + sx, y + sy), (x + ex, y + ey)], fill=(255, 240, 200),
               width=2)
        d.ellipse([x + ex - 2, y + ey - 2, x + ex + 2, y + ey + 2],
                  fill=(255, 220, 120))
    # skyline
    base = y + h - 18
    bx = x
    for bw, bh in ((34, 52), (26, 70), (40, 44), (30, 62), (36, 50),
                   (28, 74), (42, 46), (30, 58), (34, 48)):
        d.rectangle([bx, base - bh, bx + bw, base], fill=(16, 16, 26))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(bx + 5, bx + bw - 4, 10):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5],
                                fill=(255, 200, 90))
        bx += bw + 4
    # fires along the base
    for fx in (x + 60, x + 170, x + 280):
        flame(d, fx, base + 2, 26, 30)
        d.ellipse([fx - 22, base - 2, fx + 22, base + 6],
                  fill=(255, 140, 40))


def hero_cop31(d, x, y, w, h):
    """Pale hall: globe, thermometer, clock, a long table of delegates."""
    for i in range(h):  # sky: pale blue to warm cream
        t = i / h
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((168, 205, 225), (238, 232, 205)))
        d.line([(x, y + i), (x + w, y + i)], fill=c)
    # globe, left
    gx, gy, gr = x + 52, y + 46, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 120, 190),
              outline=(30, 70, 130), width=2)
    d.ellipse([gx - 20, gy - 18, gx + 2, gy + 2], fill=(90, 170, 90))
    d.ellipse([gx + 4, gy + 6, gx + 24, gy + 24], fill=(90, 170, 90))
    d.ellipse([gx - 8, gy - 26, gx + 12, gy - 12], fill=(120, 190, 120))
    # thermometer, right of globe
    tx = x + 118
    d.rounded_rectangle([tx - 5, y + 14, tx + 5, y + 62], radius=5,
                        fill=(255, 255, 255), outline=(150, 40, 40), width=2)
    d.ellipse([tx - 9, y + 58, tx + 9, y + 76], fill=(200, 40, 40),
              outline=(150, 40, 40), width=2)
    d.rectangle([tx - 2, y + 34, tx + 2, y + 62], fill=(200, 40, 40))
    # clock, right
    cx, cy, cr = x + w - 42, y + 34, 24
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
              outline=(26, 26, 26), width=2)
    d.line([(cx, cy), (cx, cy - 15)], fill=(26, 26, 26), width=2)
    d.line([(cx, cy), (cx + 11, cy + 2)], fill=(26, 26, 26), width=2)
    # long table + delegates
    ty = y + h - 26
    d.rectangle([x + 8, ty, x + w - 8, ty + 10], fill=(120, 72, 32))
    d.rectangle([x + 8, ty + 10, x + w - 8, ty + 14], fill=(90, 52, 22))
    cols = [(178, 34, 34), (38, 70, 139), (44, 116, 92), (196, 138, 30),
            (124, 92, 168), (200, 90, 20), (38, 70, 139), (178, 34, 34)]
    for i, c in enumerate(cols):
        px = x + 26 + i * 38
        d.ellipse([px - 7, ty - 16, px + 7, ty - 2], fill=(232, 190, 150))
        d.rectangle([px - 11, ty - 2, px + 11, ty], fill=c)


def hero_radar(d, x, y, w, h):
    """Dusk over the gulf: radar dishes, a low sun, flames and smoke."""
    for i in range(h):  # dusk: amber to deep plum
        t = i / h
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((240, 150, 60), (90, 40, 70)))
        d.line([(x, y + i), (x + w, y + i)], fill=c)
    d.ellipse([x + w - 70, y + 10, x + w - 30, y + 50],
              fill=(255, 220, 140))  # low sun
    sea = y + h - 26
    d.rectangle([x, sea, x + w, y + h], fill=(24, 48, 84))
    # two radar dishes on masts: a shallow arc bowl + a feed arm
    for rx, tilt in ((x + 55, -14), (x + 125, 10)):
        d.rectangle([rx - 2, sea - 36, rx + 2, sea], fill=(210, 210, 205))
        d.arc([rx - 24, sea - 64 + tilt, rx + 24, sea - 16 + tilt],
              start=180, end=360, fill=(240, 240, 235), width=4)
        d.line([(rx, sea - 40), (rx + 14, sea - 52)], fill=(240, 240, 235),
               width=2)
        d.ellipse([rx + 12, sea - 54, rx + 16, sea - 50], fill=(240, 240, 235))
    # storage tanks, centre-right
    for tx in (x + 180, x + 220):
        d.rectangle([tx, sea - 34, tx + 30, sea], fill=(235, 230, 220),
                    outline=(120, 110, 100), width=1)
        d.polygon([(tx, sea - 34), (tx + 15, sea - 44), (tx + 30, sea - 34)],
                  fill=(200, 195, 185))
    # flames + smoke over the tanks (kept inside the picture)
    flame(d, x + 195, sea - 30, 22, 26)
    flame(d, x + 235, sea - 30, 18, 22)
    smoke(d, x + 195, sea - 44, 10)
    smoke(d, x + 235, sea - 40, 9)


# -- small-lead pictures (each ~160x52, flat, few shapes) --------------
def small_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 220, 235))
    d.rectangle([x + 30, y + h - 30, x + 90, y + h - 8], fill=(38, 70, 139))
    d.rectangle([x + 30, y + h - 38, x + 90, y + h - 30], fill=(28, 55, 115))
    d.rectangle([x + 52, y + h - 46, x + 68, y + h - 38], fill=(255, 255, 255))
    d.line([(x + 95, y + 10), (x + 115, y + 30), (x + 145, y + 2)],
           fill=(30, 140, 60), width=5)
    d.rectangle([x + 100, y + h - 22, x + 150, y + h - 10], fill=(255, 255, 255),
                outline=(150, 140, 120), width=1)


def small_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 140, 70))
    d.rectangle([x + 55, y + 6, x + 105, y + h - 6], fill=(210, 190, 140))
    for sx in (60, 100):
        for k in range(3):
            d.rectangle([x + sx + k * 6, y + 10, x + sx + k * 6 + 3, y + 26],
                        fill=(240, 220, 160))
    d.ellipse([x + 130, y + 18, x + 142, y + 30], fill=(200, 40, 40))
    d.rectangle([x + 20, y + h - 8, x + w - 20, y + h], fill=(40, 110, 50))


def small_racecar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 34))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(40, 40, 48))
    for lx in range(x + 8, x + w - 8, 24):
        d.rectangle([lx, y + h - 8, lx + 12, y + h - 5], fill=(255, 220, 60))
    # low wedge car
    d.polygon([(x + 30, y + h - 16), (x + 55, y + h - 30),
               (x + 105, y + h - 30), (x + 130, y + h - 16)],
              fill=(200, 30, 30))
    d.polygon([(x + 62, y + h - 30), (x + 72, y + h - 38),
               (x + 95, y + h - 38), (x + 100, y + h - 30)],
              fill=(30, 30, 36))
    for wx in (48, 118):
        d.ellipse([x + wx - 9, y + h - 18, x + wx + 9, y + h], fill=(10, 10, 12),
                  outline=(120, 120, 120), width=1)


def small_hoop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 150, 80))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(180, 110, 50))
    d.rectangle([x + 110, y + 8, x + 118, y + h - 14], fill=(240, 240, 235))
    d.rectangle([x + 96, y + 12, x + 132, y + 26], fill=(255, 255, 255),
                outline=(200, 60, 40), width=2)
    d.ellipse([x + 104, y + 26, x + 124, y + 34], fill=None,
              outline=(220, 80, 30), width=2)
    d.ellipse([x + 30, y + 12, x + 58, y + 40], fill=(220, 110, 40),
              outline=(120, 60, 20), width=1)
    d.arc([x + 30, y + 12, x + 58, y + 40], start=200, end=340,
          fill=(120, 60, 20), width=1)


def small_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 90))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(16, 40, 66))
    d.polygon([(x + 20, y + h - 18), (x + 130, y + h - 18),
               (x + 142, y + h - 4), (x + 8, y + h - 4)], fill=(150, 30, 30))
    d.rectangle([x + 55, y + h - 32, x + 95, y + h - 18], fill=(200, 195, 185))
    flame(d, x + 75, y + h - 24, 22, 26)
    smoke(d, x + 75, y + 26, 8)


def small_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 22, 44))
    base = y + h
    for i, (bw, bh) in enumerate(((28, 30), (24, 38), (30, 26), (24, 34))):
        bx = x + 8 + i * 38
        d.rectangle([bx, base - bh, bx + bw, base], fill=(10, 12, 26))
        for wy in range(base - bh + 5, base - 4, 10):
            for wx in range(bx + 3, bx + bw - 3, 8):
                if (wx + wy) % 4 == 0:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 200, 90))
    d.polygon([(x + 132, y + 8), (x + 122, y + 26), (x + 130, y + 26),
               (x + 124, y + 42), (x + 140, y + 20), (x + 132, y + 20)],
              fill=(255, 220, 60))


def small_icu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 235, 235))
    d.rectangle([x + 16, y + h - 20, x + 100, y + h - 10], fill=(200, 210, 210))
    d.rectangle([x + 22, y + h - 32, x + 58, y + h - 20], fill=(240, 245, 245),
                outline=(150, 160, 160), width=1)
    d.ellipse([x + 26, y + h - 38, x + 38, y + h - 28], fill=(232, 190, 150))
    d.rectangle([x + 108, y + 6, x + 152, y + 28], fill=(30, 40, 50))
    d.line([(x + 112, y + 18), (x + 120, y + 18), (x + 125, y + 10),
            (x + 130, y + 24), (x + 135, y + 14), (x + 144, y + 18),
            (x + 148, y + 18)], fill=(80, 220, 120), width=2)


def small_search(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 40))
    d.rectangle([x + 12, y + 8, x + w - 44, y + h - 8], fill=(24, 34, 56))
    for ry in range(y + 14, y + h - 12, 10):
        d.line([(x + 18, ry), (x + w - 50, ry)], fill=(60, 90, 130), width=1)
    d.ellipse([x + w - 40, y + 6, x + w - 14, y + 32], fill=None,
              outline=(255, 200, 60), width=3)
    d.line([(x + w - 18, y + 30), (x + w - 8, y + 42)],
           fill=(255, 200, 60), width=3)


def small_plane(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 205, 220))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(140, 150, 160))
    d.polygon([(x + 40, y + 26), (x + 120, y + 26), (x + 132, y + 32),
               (x + 40, y + 32)], fill=(240, 240, 235))
    d.polygon([(x + 60, y + 26), (x + 100, y + 26), (x + 96, y + 14),
               (x + 68, y + 14)], fill=(240, 240, 235))
    d.polygon([(x + 120, y + 26), (x + 138, y + 18), (x + 138, y + 26)],
              fill=(200, 60, 50))
    d.rectangle([x + 20, y + 8, x + 60, y + 16], fill=(38, 70, 139))
    d.rectangle([x + 20, y + 20, x + 60, y + 28], fill=(178, 34, 34))


def small_warning(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 30, 20))
    d.polygon([(x + w // 2, y + 6), (x + w - 16, y + h - 10),
               (x + 16, y + h - 10)], fill=(255, 200, 0),
              outline=(200, 150, 0), width=2)
    d.rectangle([x + w // 2 - 2, y + 16, x + w // 2 + 2, y + 32],
                fill=(40, 30, 20))
    d.ellipse([x + w // 2 - 3, y + 36, x + w // 2 + 3, y + 42],
              fill=(40, 30, 20))
    d.rectangle([x + 18, y + h - 16, x + 34, y + h - 6], fill=(30, 120, 60))
    d.rectangle([x + 38, y + h - 14, x + 50, y + h - 6], fill=(200, 60, 40))


def small_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 55, 50))
    d.rectangle([x + 14, y + h - 26, x + 90, y + h - 8], fill=(120, 115, 108))
    d.polygon([(x + 14, y + h - 26), (x + 30, y + h - 40),
               (x + 46, y + h - 26)], fill=(100, 95, 88))
    d.polygon([(x + 50, y + h - 26), (x + 66, y + h - 40),
               (x + 82, y + h - 26)], fill=(100, 95, 88))
    d.rectangle([x + 100, y + 8, x + 112, y + h - 8], fill=(90, 85, 80))
    flame(d, x + 52, y + h - 24, 26, 30)
    flame(d, x + 106, y + h - 6, 18, 22)
    smoke(d, x + 106, y + 26, 8)


def small_mountain(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 200, 220))
    d.polygon([(x, y + h), (x + 50, y + 8), (x + 100, y + h)],
              fill=(90, 110, 130))
    d.polygon([(x + 60, y + h), (x + 115, y + 16), (x + w, y + h)],
              fill=(70, 90, 110))
    d.polygon([(x + 42, y + 16), (x + 50, y + 8), (x + 58, y + 16),
               (x + 54, y + 22), (x + 46, y + 22)], fill=(255, 255, 255))
    d.line([(x + 20, y + 22), (x + 40, y + 40), (x + 30, y + 30),
            (x + 55, y + 48)], fill=(200, 40, 40), width=2)
    d.line([(x + 55, y + 48), (x + 70, y + 34)], fill=(200, 40, 40), width=2)

SMALL_ART = [small_ballot, small_cricket, small_racecar, small_hoop,
             small_ship, small_power, small_icu, small_search,
             small_plane, small_warning, small_factory, small_mountain]
HERO_ART = [hero_drones, hero_cop31, hero_radar]


# ------------------------------------------------------------------ map
# Simplified continent outlines (lon, lat) — geographic data.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-65, 60), (-55, 47), (-60, 45), (-75, 35), (-80, 25),
     (-85, 15), (-95, 15), (-105, 20), (-115, 30), (-125, 40), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-75, -20), (-80, -5)],
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 58), (18, 56), (25, 60),
     (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (25, 40), (20, 40),
     (15, 44), (8, 44), (0, 40), (-8, 38)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -25), (12, -15), (10, -5), (8, 4), (0, 5), (-8, 5),
     (-15, 10)],
    [(40, 70), (60, 72), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (170, 66), (160, 60), (140, 55), (130, 45), (127, 40),
     (120, 35), (110, 20), (105, 10), (100, 5), (95, 10), (90, 22),
     (80, 15), (75, 8), (70, 20), (60, 25), (55, 28), (50, 30), (45, 35),
     (40, 40)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -17),
     (114, -22)],
]

# (story number, lon, lat, dx, dy) — pins for the 15 illustrated leads
PINS = [
    (1, 30.3, 50.8, 0, 0), (2, 30.7, 36.9, 0, 0), (3, 50.6, 26.2, 0, 0),
    (4, 114.2, 22.3, 0, 0), (5, 174.8, -41.3, 0, 0), (6, -115.1, 36.2, 0, 0),
    (7, -98.5, 29.4, 0, 0), (8, 24.5, 59.8, 0, 0), (9, 51.4, 35.7, 0, 0),
    (10, -47.9, -15.8, 0, 0), (11, -77.0, 38.9, 0, 0),
    (12, 4.35, 50.85, 0, 0), (13, 93.9, 24.8, 0, 0),
    (14, 106.2, -6.1, 0, 0), (15, -75.2, -11.2, 0, 0),
]


def _inside(lon, lat, poly):
    """Ray-casting point-in-polygon for (lon, lat)."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_dotted_map(d, x, y, w, h):
    """Tan dotted world map + numbered red pins for stories 1-15."""
    def proj(lon, lat):
        return (x + (lon + 180) / 360 * w, y + (78 - lat) / 136 * h)
    dot = (172, 146, 96)
    step = 6
    for gy in range(0, h, step):
        for gx in range(0, w, step):
            lon = gx / w * 360 - 180
            lat = 78 - gy / h * 136
            if any(_inside(lon, lat, poly) for poly in CONTINENTS):
                d.ellipse([x + gx - 1.6, y + gy - 1.6, x + gx + 1.6,
                           y + gy + 1.6], fill=dot)
    f_pin = get_font(SANS_B, 8)
    for num, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        px += dx
        py += dy
        r = 6.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=f_pin)
        d.text((px - tw / 2, py - 5.5), t, font=f_pin, fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # 1. top bar (dark navy)
    d.rectangle([0, 0, W, 20], fill=NAVY)
    f_top = get_font(SANS_B, 11)
    d.text((MX, 4), "THE WORLD IN ONE DAY", font=f_top, fill=(255, 255, 255))
    rt = ("36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED "
          "SUNDAY 22 NOVEMBER 2026")
    d.text((W - MX - d.textlength(rt, font=f_top), 4), rt, font=f_top,
           fill=(255, 255, 255))

    # 2. masthead
    size = 64
    while size > 40:
        f_mast = get_font(SERIF_B, size)
        if d.textlength("Sunday 22 November 2026", font=f_mast) <= CW:
            break
        size -= 1
    mt = "Sunday 22 November 2026"
    d.text(((W - d.textlength(mt, font=f_mast)) / 2, 24), mt, font=f_mast,
           fill=INK)

    # 3. subline (red italic)
    f_sub = get_font(SERIF_I, 17)
    sw = d.textlength(SUBLINE, font=f_sub)
    d.text(((W - sw) / 2, 98), SUBLINE, font=f_sub, fill=RED)
    d.line([(MX, 118), (W - MX, 118)], fill=INK, width=1)

    # 4. stat strip: 6 big red numbers + short labels
    col_w = CW / 6
    f_num = get_font(SANS_B, 30)
    f_cap = get_font(SANS, 9)
    for i, (num, cap) in enumerate(STATS):
        bx = MX + i * col_w
        if i:
            d.line([(bx - 5, 124), (bx - 5, 156)], fill=(200, 192, 175),
                   width=1)
        d.text((bx, 122), num, font=f_num, fill=RED)
        draw_text(d, bx, 152, cap, f_cap, col_w - 12, 2, fill=GREY, lh=10)
    d.line([(MX, 164), (W - MX, 164)], fill=INK, width=1)

    # 5. region bar (widths proportional to counts, WORLD min 72px)
    total = sum(c for _, c, _ in REGIONS)
    widths = [CW * c / total for _, c, _ in REGIONS]
    short = 72 - widths[6]
    if short > 0:
        widths[6] = 72
        others = sum(widths[i] for i in (0, 1, 2, 3, 4, 5))
        for i in (0, 1, 2, 3, 4, 5):
            widths[i] -= short * widths[i] / others
    rx = MX
    f_reg = get_font(SANS_B, 11)
    for (label, _, col), rw in zip(REGIONS, widths):
        d.rectangle([rx, 168, rx + rw, 189], fill=col)
        tw = d.textlength(label, font=f_reg)
        d.text((rx + (rw - tw) / 2, 173), label, font=f_reg,
               fill=(255, 255, 255))
        rx += rw

    # 6. THE DAY IN UTC bar (dark navy, 6 timed events)
    d.rectangle([MX, 193, W - MX, 212], fill=NAVY)
    f_utc = get_font(SANS_B, 9)
    f_utcl = get_font(SANS, 9)
    d.text((MX + 6, 198), "THE DAY IN UTC", font=f_utc,
           fill=(255, 255, 255))
    ux = MX + 118
    uw = (W - MX - ux) / 6
    for t, label in UTC_BAR:
        d.text((ux, 198), t, font=f_utc, fill=(255, 210, 90))
        d.text((ux + 34, 198), label, font=f_utcl, fill=(255, 255, 255))
        ux += uw

    # 7. three hero leads
    hw = 328
    hx = [MX, MX + hw + 12, MX + 2 * (hw + 12)]
    f_tag = get_font(SANS_B, 10)
    f_src = get_font(SANS, 9)
    f_kick = get_font(SANS_B, 10)
    f_head = get_font(SERIF_B, 21)
    f_sub2 = get_font(SANS, 11)
    f_cert = get_font(SANS_B, 8)
    for i, hero in enumerate(HEROES):
        tag, piltxt, src, kicker, headline, sub, cert = hero
        x0 = hx[i]
        HERO_ART[i](d, x0, 216, hw, 96)
        # tag top-left, pill top-right, source bottom-left
        d.rectangle([x0, 216, x0 + d.textlength(tag, font=f_tag) + 12, 233],
                    fill=RED)
        d.text((x0 + 6, 219), tag, font=f_tag, fill=(255, 255, 255))
        tag_pill(d, x0 + hw - d.textlength(piltxt, font=f_tag) - 24, 219,
                 piltxt, f_tag, INK, (255, 255, 255))
        tag_pill(d, x0 + 6, 292, src, f_src, (255, 255, 255), (20, 20, 20))
        # text below the picture
        ty = 316
        d.text((x0, ty), kicker, font=f_kick, fill=RED)
        cw = d.textlength(cert, font=f_cert)
        d.text((x0 + hw - cw, ty + 1), cert, font=f_cert, fill=GREY)
        hy_end = draw_text(d, x0, ty + 14, headline, f_head, hw, 2,
                           fill=INK, lh=23)
        draw_text(d, x0, hy_end + 4, sub, f_sub2, hw, 2, fill=(50, 50, 50),
                  lh=13)

    # 8. twelve small leads, two rows of six
    sw_ = 160
    sx = [MX + i * (sw_ + 8) for i in range(6)]
    f_num2 = get_font(SANS_B, 10)
    f_kick2 = get_font(SANS_B, 9)
    f_head2 = get_font(SERIF_B, 13)
    f_sub3 = get_font(SANS, 10)
    for row in range(2):
        iy = 412 if row == 0 else 560
        for j in range(6):
            num, tag, src, kicker, headline, sub, cert = SMALLS[row * 6 + j]
            x0 = sx[j]
            SMALL_ART[row * 6 + j](d, x0, iy, sw_, 52)
            d.rectangle([x0, iy, x0 + d.textlength(tag, font=f_tag) + 10,
                         iy + 15], fill=RED)
            d.text((x0 + 5, iy + 2), tag, font=f_tag,
                   fill=(255, 255, 255))
            # circled story number, top-right
            cx, cy = x0 + sw_ - 12, iy + 12
            d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255),
                      outline=RED, width=2)
            t = str(num)
            tw = d.textlength(t, font=f_num2)
            d.text((cx - tw / 2, cy - 6), t, font=f_num2, fill=RED)
            tag_pill(d, x0 + 5, iy + 32, src, f_src, (255, 255, 255),
                     (20, 20, 20))
            ty = iy + 56
            d.text((x0, ty), kicker, font=f_kick2, fill=RED)
            sh_end = draw_text(d, x0, ty + 12, headline, f_head2, sw_, 3,
                               fill=INK, lh=15)
            draw_text(d, x0, sh_end + 2, sub, f_sub3, sw_, 2,
                      fill=(50, 50, 50), lh=12)

    # 9. map + ALSO list
    hy = 708
    f_h = get_font(SANS_B, 11)
    d.text((MX, hy), "WHERE IT HAPPENED", font=f_h, fill=INK)
    d.text((MX + 148, hy), "pins match story numbers", font=f_src,
           fill=GREY)
    d.text((340, hy), "ALSO ON SUNDAY 22 NOVEMBER \u2014 21 MORE STORIES",
           font=f_h, fill=INK)
    d.line([(MX, hy + 15), (W - MX, hy + 15)], fill=INK, width=1)
    draw_dotted_map(d, MX, hy + 22, 318, 154)
    f_br = get_font(SANS, 9)
    f_brn = get_font(SANS_B, 9)
    for k, (num, text) in enumerate(BRIEFS):
        col = 0 if k < 11 else 1
        bx = 340 if col == 0 else 686
        by = hy + 24 + (k % 11) * 14
        d.text((bx, by), str(num), font=f_brn, fill=RED)
        d.text((bx + 22, by), text, font=f_br, fill=INK)

    # 10. DATE CHECK box (red border) — closed box y=926..981, well
    # below the last ALSO row (ends ~y=884); heading + text inside it.
    d.rectangle([MX, 926, W - MX, 981], outline=RED, width=2)
    f_dc = get_font(SANS_B, 11)
    d.text((MX + 8, 932), "DATE CHECK", font=f_dc, fill=RED)
    draw_text(d, MX + 8, 948, DATE_CHECK[len("DATE CHECK \u2014 "):],
              get_font(SANS, 10), CW - 16, 2, fill=INK, lh=13)

    # 11. sources line, certainty legend + footer
    d.text((MX, 989), SOURCES_LINE, font=get_font(SANS, 9), fill=GREY)
    d.text((MX, 1006), CERTAINTY_LEGEND, font=get_font(SANS, 8), fill=GREY)
    f_ft = get_font(SANS_B, 10)
    ft = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    d.text((W - MX - d.textlength(ft, font=f_ft), 1006), ft, font=f_ft,
           fill=INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    build()
