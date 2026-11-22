"""News-image 20261122 front page — "THE WORLD IN ONE DAY".

One-page broadsheet summing up Sunday 22 November 2026: 35 stories,
6 regions, 3 hero leads, 10 small leads, a dotted world map with
numbered pins, a DATE CHECK box and a sources line. All pictures are
drawn fresh in code with Pillow primitives (flat shapes, no photos, no
network, no embedded images). Deterministic: same bytes on every run.
Output: entry.png, 1024x1024 RGB.

Fix (2026-11-22): the DATE CHECK box is now a closed rectangle that
sits below the ALSO list — the ALSO row spacing is 14px so its last
row ends at y=904, and the box runs y=926..981, clear of the briefs.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MX = 12                      # side margin (matches the reference layout)
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

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def split_lines(d, text, f, max_w):
    """Greedy word wrap to a pixel width."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def fit_text(d, text, f, max_w, max_lines):
    """Wrap; shrink the font until it fits max_lines (floor 8pt)."""
    size = f.size
    while size > 8:
        lines = split_lines(d, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
        f = font(f.path, size)
    return split_lines(d, text, f, max_w), f


def put_text(d, x, y, text, f, max_w, max_lines, fill=INK, lh=None):
    """Draw wrapped text; return the y just below the last line."""
    lines, f2 = fit_text(d, text, f, max_w, max_lines)
    step = lh if lh is not None else int(f2.size * 1.22)
    for line in lines:
        d.text((x, y), line, font=f2, fill=fill)
        y += step
    return y


def pill(d, x, y, text, f, fg, bg, pad_x=6, pad_y=2):
    """Rounded label; returns its right edge."""
    tw = d.textlength(text, font=f)
    th = f.size + 2 * pad_y
    d.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + th], radius=th // 2,
                        fill=bg)
    d.text((x + pad_x, y + pad_y - 1), text, font=f, fill=fg)
    return x + tw + 2 * pad_x


# ------------------------------------------------------------------ data
SUBLINE = ("A climate deal nears at COP31 \u00b7 Kyiv counts the cost of a "
           "400-drone night \u00b7 Iran hits US bases in Bahrain")

STATS = [
    ("~200", "delegations at the COP31 talks"),
    ("03:00", "GMT cut-off to object"),
    ("400+", "drones launched at Ukraine"),
    ("110", "missiles in the same barrage"),
    ("9", "people killed in the barrage"),
    ("2", "US bases struck in Bahrain"),
]

REGIONS = [
    ("EUROPE 9", 9, (38, 70, 139)),
    ("MIDDLE EAST 8", 8, (178, 34, 34)),
    ("AMERICAS 6", 6, (44, 116, 92)),
    ("ASIA-PACIFIC 5", 5, (196, 138, 30)),
    ("AFRICA 1", 1, (121, 70, 37)),
    ("WORLD 6", 6, (124, 92, 168)),
]

# (tag, pill, source, kicker, headline, sub)
HEROES = [
    ("COP31: FINAL HOURS", "~200 nations", "COP31 presidency",
     "1  ANTALYA, TURKEY \u00b7 CLIMATE",
     "COP31 closes in on a deal after the fossil-fuel fight",
     "A fresh package drops after a row over fossil fuels; delegations "
     "get until 03:00 GMT to object. (Reuters, BBC)"),
    ("UKRAINE: NIGHT RAID", "400+ drones", "Kyiv officials",
     "2  KYIV, UKRAINE \u00b7 WAR",
     "A 400-drone, 110-missile night batters Ukraine's cities",
     "One of the war's biggest overnight attacks; nine are killed and "
     "Kyiv's power grid takes another hit. (Al Jazeera)"),
    ("BAHRAIN: UNDER FIRE", "2 bases", "Bahrain authorities",
     "3  MANAMA, BAHRAIN \u00b7 IRAN WAR",
     "Iran strikes US bases in Bahrain; tankers burn in Hormuz",
     "Air defences intercept several missiles; three tankers are hit in "
     "and near the strait. (Al Jazeera, CNA)"),
]

# (number, tag, source, kicker, headline, sub)
SMALLS = [
    (4, "SHIP ON FIRE", "Finnish forces", "GULF OF FINLAND",
     "A Russian freighter catches fire in the Gulf of Finland",
     "Finland says Ukraine was likely behind it. (BBC)"),
    (5, "2 DEAD, 60 HURT", "Officials' count", "KRYVYI RIH",
     "A missile strike kills two in Zelenskyy's home city",
     "A boy of seven and a young paramedic are among the dead. "
     "(Al Jazeera)"),
    (6, "24 DEAD", "Emergency agency", "BAYELSA, NIGERIA",
     "A boat packed with funeral-goers capsizes in Bayelsa",
     "Passengers were on their way to a funeral. (DW, Sky News)"),
    (7, "COALITION TALKS", "Party statement", "JERUSALEM",
     "Eisenkot opens coalition talks with Likud",
     "He seeks the broadest possible government. (Straits Times)"),
    (8, "3 KILLED", "Witnesses", "GAZA",
     "An air strike kills three in a food-aid vehicle",
     "Three Palestinians die in an air attack. (Al Jazeera, Reuters)"),
    (9, "11 DEAD", "Officials' count", "SINALOA, MEXICO",
     "FBI's most-wanted 'El Chapo Isidro' is captured",
     "FBI top-ten fugitive held after a shoot-out. (Sky News, BBC)"),
    (10, "POWER CUTS", "Officials", "TEHRAN, IRAN",
     "Iran rations power as the grid strains",
     "War damage hits the energy network. (Straits Times)"),
    (11, "SEC PROBE", "Media report", "WASHINGTON",
     "Nvidia faces a US accounting inquiry",
     "The SEC inquiry is at an early stage. (Straits Times)"),
    (12, "BOLSONARO: ICU", "Hospital", "BRASILIA, BRAZIL",
     "Bolsonaro lies in intensive care in Brasilia",
     "Ex-president stable, breathing on his own. (Al Jazeera, Reuters)"),
    (13, "AUKUS ROW", "Minister", "CANBERRA",
     "Marles dismisses a US report on AUKUS boats",
     "He says the budget office is wrong. (ABC, Reuters)"),
]

# (number, one-line brief) — numbers 14..35, two columns of 11
BRIEFS = [
    (14, "US: FBI looks into apparent hack of its crime database (BBC)"),
    (15, "US: Teen gamer and his mother help FBI rescue a girl (BBC)"),
    (16, "US: Midterm loss corners Vance as 2028 field widens (ST)"),
    (17, "Saudi Arabia: Air defences down a missile (Investing.com)"),
    (18, "Lebanon: Aoun demands Israeli withdrawal (Al Jazeera)"),
    (19, "Iran: President warns of a hard winter (ISNA)"),
    (20, "Hormuz: Lewis Pugh swims strait as tanker is struck (BBC)"),
    (21, "Moldova: Reports a Russian airspace breach (Kyiv Ind.)"),
    (22, "Belgium: Air traffic to halt in 23 Nov national strike (ST)"),
    (23, "Germany: IG Metall widens car and shipyard strikes (Reuters)"),
    (24, "Portugal: Thousands march in Lisbon on living costs (Reuters)"),
    (25, "Denmark: Expels Russian attaché in rapper plot (Guardian)"),
    (26, "Bangladesh: 50+ Awami League homes set on fire (TOI)"),
    (27, "Australia: Fred Nile, ex-NSW MP, dies aged 92 (ABC)"),
    (28, "Australia: Bystanders pull driver from burning car (ABC)"),
    (29, "Melbourne: 70 years since 1956 Olympics opened (ABC)"),
    (30, "Trade: EU and Indonesia sign deal after 10 years (DW)"),
    (31, "Rugby: England beat New Zealand 37-12 (Reuters)"),
    (32, "Rugby: France beat Argentina 45-17, reach final (Reuters)"),
    (33, "Football: Arsenal 2-2 Newcastle, Leeds 4-1 Chelsea (BBC)"),
    (34, "Tennis: Zverev v Alcaraz in today's ATP Finals final (TOI)"),
    (35, "Football: Liverpool host Man Utd today (Al Jazeera)"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Wires read to 04:45 UTC on Sunday 22 November 2026. "
    "Each story here was reported, or still developing, on 22 November "
    "somewhere in the world. Kept out as other days' news: the Peru quake "
    "(20 Nov local), Russian missiles in Poland (19 Nov), the Kerch Bridge "
    "strikes (earlier in the week) and the Shenzhen summit (19 Nov).")

SOURCES_LINE = (
    "Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, "
    "CNA, ABC Australia, Times of India, The Guardian, Kyiv Independent, "
    "ISNA. Every story names its outlet. Pictures and map: original, "
    "drawn in code.")


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


def hero_ukraine(d, x, y, w, h):
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


def hero_bahrain(d, x, y, w, h):
    """Dusk over the gulf: orange sky, tanks, a tanker, flames, smoke."""
    for i in range(h):  # dusk: amber to deep plum
        t = i / h
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((240, 150, 60), (90, 40, 70)))
        d.line([(x, y + i), (x + w, y + i)], fill=c)
    d.ellipse([x + w - 70, y + 10, x + w - 30, y + 50],
              fill=(255, 220, 140))  # low sun
    sea = y + h - 26
    d.rectangle([x, sea, x + w, y + h], fill=(24, 48, 84))
    # storage tanks, left
    for tx in (x + 22, x + 62, x + 102):
        d.rectangle([tx, sea - 34, tx + 30, sea], fill=(235, 230, 220),
                    outline=(120, 110, 100), width=1)
        d.polygon([(tx, sea - 34), (tx + 15, sea - 44), (tx + 30, sea - 34)],
                  fill=(200, 195, 185))
    # tanker, right
    sx = x + w - 130
    d.rectangle([sx, sea - 16, sx + 110, sea - 2], fill=(30, 30, 34))
    d.rectangle([sx + 70, sea - 30, sx + 92, sea - 16], fill=(30, 30, 34))
    d.rectangle([sx + 8, sea - 8, sx + 102, sea], fill=(140, 30, 30))
    flame(d, sx + 30, sea - 14, 22, 26)
    flame(d, sx + 90, sea - 14, 18, 22)
    smoke(d, sx + 30, sea - 52, 10)
    smoke(d, sx + 90, sea - 46, 9)


# -- small-lead pictures (each ~196x56, flat, few shapes) --------------
def small_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 90))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(16, 40, 66))
    d.polygon([(x + 20, y + h - 18), (x + 150, y + h - 18),
               (x + 165, y + h - 4), (x + 8, y + h - 4)], fill=(150, 30, 30))
    d.rectangle([x + 60, y + h - 34, x + 110, y + h - 18], fill=(200, 195, 185))
    flame(d, x + 90, y + h - 32, 26, 30)
    smoke(d, x + 90, y + 8, 9)


def small_city(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 118, 110))
    base = y + h
    for i, (bw, bh) in enumerate(((36, 40), (30, 48), (38, 34), (30, 44))):
        bx = x + 8 + i * 48
        d.rectangle([bx, base - bh, bx + bw, base], fill=(70, 68, 64))
        for wy in range(base - bh + 6, base - 4, 10):
            for wx in range(bx + 4, bx + bw - 3, 9):
                if (wx * 7 + wy * 3) % 5 == 0:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 210, 120))
    flame(d, x + 120, base - 30, 22, 26)
    smoke(d, x + 120, base - 52, 9)


def small_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 190, 210))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(40, 110, 160))
    d.polygon([(x + 40, y + h - 20), (x + 160, y + h - 20),
               (x + 148, y + h - 6), (x + 52, y + h - 6)], fill=(120, 70, 30))
    for px in (70, 95, 120, 145):
        d.ellipse([x + px - 5, y + h - 34, x + px + 5, y + h - 22],
                  fill=(232, 190, 150))
    d.rectangle([x + 100, y + 6, x + 104, y + h - 22], fill=(90, 60, 30))
    d.polygon([(x + 104, y + 6), (x + 140, y + 26), (x + 104, y + 26)],
              fill=(240, 235, 220))


def small_talks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 205, 175))
    d.rectangle([x + 10, y + h - 18, x + w - 10, y + h - 8], fill=(120, 72, 32))
    for px, c in ((40, (38, 70, 139)), (80, (178, 34, 34)),
                  (120, (44, 116, 92)), (160, (196, 138, 30))):
        d.ellipse([x + px - 7, y + h - 34, x + px + 7, y + h - 20],
                  fill=(232, 190, 150))
        d.rectangle([x + px - 11, y + h - 20, x + px + 11, y + h - 18],
                    fill=c)
    d.rectangle([x + 70, y + 8, x + 126, y + 20], fill=(255, 255, 255),
                outline=(150, 140, 120), width=1)


def small_aid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 190, 170))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(140, 130, 115))
    d.rectangle([x + 50, y + h - 36, x + 140, y + h - 14], fill=(240, 240, 235))
    d.rectangle([x + 140, y + h - 30, x + 165, y + h - 14], fill=(200, 60, 50))
    d.ellipse([x + 70, y + h - 12, x + 84, y + h + 2], fill=(30, 30, 30))
    d.ellipse([x + 140, y + h - 12, x + 154, y + h + 2], fill=(30, 30, 30))
    flame(d, x + 100, y + h - 34, 20, 24)
    smoke(d, x + 100, y + 6, 8)


def small_desert(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 200, 150))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(200, 160, 100))
    d.ellipse([x + 150, y + 6, x + 182, y + 38], fill=(255, 220, 140))
    d.rectangle([x + 30, y + h - 34, x + 90, y + h - 16], fill=(90, 90, 88))
    d.rectangle([x + 40, y + h - 44, x + 70, y + h - 34], fill=(120, 120, 118))
    for px in (110, 135, 160):
        d.ellipse([x + px - 4, y + h - 26, x + px + 4, y + h - 16],
                  fill=(40, 40, 40))


def small_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 22, 44))
    base = y + h
    for i, (bw, bh) in enumerate(((34, 34), (28, 44), (36, 30), (30, 40))):
        bx = x + 10 + i * 46
        d.rectangle([bx, base - bh, bx + bw, base], fill=(10, 12, 26))
        for wy in range(base - bh + 6, base - 4, 11):
            for wx in range(bx + 4, bx + bw - 3, 9):
                if (wx + wy) % 4 == 0:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 200, 90))
    d.line([(x + 150, y + 6), (x + 150, y + h - 6)], fill=(120, 120, 120),
           width=2)
    d.line([(x + 130, y + 14), (x + 172, y + 14)], fill=(120, 120, 120),
           width=2)
    d.polygon([(x + 158, y + 22), (x + 146, y + 40), (x + 154, y + 40),
               (x + 148, y + 56), (x + 166, y + 34), (x + 158, y + 34)],
              fill=(255, 220, 60))


def small_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 40))
    d.rectangle([x + 14, y + 10, x + w - 50, y + h - 10], fill=(24, 34, 56))
    pts = [(x + 22, y + 40), (x + 50, y + 30), (x + 78, y + 34),
           (x + 106, y + 18), (x + 128, y + 44)]
    d.line(pts, fill=(60, 200, 110), width=3)
    d.line([pts[-1], (x + 138, y + 50)], fill=(220, 60, 50), width=3)
    d.ellipse([x + w - 34, y + 6, x + w - 6, y + 34], fill=None,
              outline=(255, 255, 255), width=3)
    d.line([(x + w - 32, y + 32), (x + w - 44, y + 44)], fill=(255, 255, 255),
           width=3)


def small_icu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 235, 235))
    d.rectangle([x + 20, y + h - 22, x + 120, y + h - 12], fill=(200, 210, 210))
    d.rectangle([x + 26, y + h - 34, x + 70, y + h - 22], fill=(240, 245, 245),
                outline=(150, 160, 160), width=1)
    d.ellipse([x + 30, y + h - 40, x + 44, y + h - 30], fill=(232, 190, 150))
    d.rectangle([x + 130, y + 8, x + 182, y + 34], fill=(30, 40, 50))
    d.line([(x + 134, y + 22), (x + 144, y + 22), (x + 150, y + 12),
            (x + 156, y + 30), (x + 162, y + 18), (x + 172, y + 22),
            (x + 178, y + 22)], fill=(80, 220, 120), width=2)


def small_sub(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 48, 84))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(12, 28, 52))
    d.ellipse([x + 30, y + 16, x + 170, y + 40], fill=(40, 60, 90))
    d.rectangle([x + 85, y + 6, x + 115, y + 18], fill=(40, 60, 90))
    for wx in range(x + 44, x + 160, 14):
        d.ellipse([wx, y + 25, wx + 5, y + 30], fill=(255, 220, 120))
    d.line([(x + 20, y + 46), (x + 180, y + 46)], fill=(120, 150, 190),
           width=1)

SMALL_ART = [small_ship, small_city, small_boat, small_talks, small_aid,
             small_desert, small_power, small_chart, small_icu, small_sub]
HERO_ART = [hero_cop31, hero_ukraine, hero_bahrain]


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

# (story number, lon, lat, dx, dy) — offsets spread pins that share a spot
PINS = [
    (1, 30.7, 36.9, 0, 0), (2, 30.5, 50.4, 0, 0), (3, 50.6, 26.2, 10, -6),
    (4, 24.5, 59.8, 0, 0), (5, 33.4, 47.9, 10, 8), (6, 6.0, 4.8, 0, 0),
    (7, 35.2, 31.8, 0, -9), (8, 34.5, 31.5, -11, 7), (9, -107.4, 24.8, 0, 0),
    (10, 51.4, 35.7, 0, 0), (11, -77.0, 38.9, 0, 0), (12, -47.9, -15.8, 0, 0),
    (13, 149.1, -35.3, 0, 0), (14, -77.0, 38.9, -12, 6),
    (15, -122.7, 45.5, 0, 0), (16, -77.0, 38.9, 12, -6),
    (17, 46.7, 24.6, -10, 8), (18, 35.5, 33.9, 11, -7),
    (19, 51.4, 35.7, 12, 8), (20, 56.5, 26.6, 0, 0), (21, 28.8, 47.0, -10, 8),
    (22, 4.35, 50.85, 10, -6), (23, 10.0, 53.5, 0, 0), (24, -9.1, 38.7, 0, 0),
    (25, 12.6, 55.7, 10, -8), (26, 90.4, 23.8, 0, 0), (27, 151.2, -33.9, 0, 0),
    (28, 149.1, -35.3, -10, 8), (29, 145.0, -37.8, 0, 0),
    (30, 106.8, -6.2, 0, 0), (31, -0.1, 51.5, 0, 0), (32, 2.35, 48.85, -10, 8),
    (33, -0.1, 51.5, 10, 8), (34, 7.7, 45.1, 0, 0), (35, -2.99, 53.4, -10, -8),
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
    """Tan dotted world map + numbered red pins."""
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
    f_pin = font(SANS_B, 8)
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
    f_top = font(SANS_B, 11)
    d.text((MX, 4), "THE WORLD IN ONE DAY", font=f_top, fill=(255, 255, 255))
    rt = ("35 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED "
          "SUNDAY 22 NOVEMBER 2026")
    d.text((W - MX - d.textlength(rt, font=f_top), 4), rt, font=f_top,
           fill=(255, 255, 255))

    # 2. masthead
    size = 64
    while size > 40:
        f_mast = font(SERIF_B, size)
        if d.textlength("Sunday 22 November 2026", font=f_mast) <= CW:
            break
        size -= 1
    mt = "Sunday 22 November 2026"
    d.text(((W - d.textlength(mt, font=f_mast)) / 2, 24), mt, font=f_mast,
           fill=INK)

    # 3. subline (red italic)
    f_sub = font(SERIF_I, 17)
    sw = d.textlength(SUBLINE, font=f_sub)
    d.text(((W - sw) / 2, 98), SUBLINE, font=f_sub, fill=RED)
    d.line([(MX, 118), (W - MX, 118)], fill=INK, width=1)

    # 4. stat strip: 6 big red numbers + short labels
    col_w = CW / 6
    f_num = font(SANS_B, 30)
    f_cap = font(SANS, 9)
    for i, (num, cap) in enumerate(STATS):
        bx = MX + i * col_w
        if i:
            d.line([(bx - 5, 124), (bx - 5, 156)], fill=(200, 192, 175),
                   width=1)
        d.text((bx, 122), num, font=f_num, fill=RED)
        put_text(d, bx, 152, cap, f_cap, col_w - 12, 2, fill=GREY, lh=10)
    d.line([(MX, 164), (W - MX, 164)], fill=INK, width=1)

    # 5. region bar (widths proportional to counts, Africa min 88px)
    total = sum(c for _, c, _ in REGIONS)
    widths = [CW * c / total for _, c, _ in REGIONS]
    short = 88 - widths[4]
    if short > 0:
        widths[4] = 88
        others = sum(widths[i] for i in (0, 1, 2, 3, 5))
        for i in (0, 1, 2, 3, 5):
            widths[i] -= short * widths[i] / others
    rx = MX
    f_reg = font(SANS_B, 11)
    for (label, _, col), rw in zip(REGIONS, widths):
        d.rectangle([rx, 168, rx + rw, 189], fill=col)
        tw = d.textlength(label, font=f_reg)
        d.text((rx + (rw - tw) / 2, 173), label, font=f_reg,
               fill=(255, 255, 255))
        rx += rw

    # 6. three hero leads
    hw = 328
    hx = [MX, MX + hw + 12, MX + 2 * (hw + 12)]
    f_tag = font(SANS_B, 10)
    f_src = font(SANS, 9)
    f_kick = font(SANS_B, 10)
    f_head = font(SERIF_B, 21)
    f_sub2 = font(SANS, 11)
    for i, hero in enumerate(HEROES):
        tag, piltxt, src, kicker, headline, sub = hero
        x0 = hx[i]
        HERO_ART[i](d, x0, 193, hw, 104)
        # tag top-left, pill top-right, source bottom-left
        d.rectangle([x0, 193, x0 + d.textlength(tag, font=f_tag) + 12, 210],
                    fill=RED)
        d.text((x0 + 6, 196), tag, font=f_tag, fill=(255, 255, 255))
        pill(d, x0 + hw - d.textlength(piltxt, font=f_tag) - 24, 196, piltxt,
             f_tag, INK, (255, 255, 255))
        pill(d, x0 + 6, 272, src, f_src, (255, 255, 255), (20, 20, 20))
        # text below the picture
        ty = 302
        d.text((x0, ty), kicker, font=f_kick, fill=RED)
        put_text(d, x0, ty + 14, headline, f_head, hw, 2, fill=INK, lh=23)
        put_text(d, x0, ty + 62, sub, f_sub2, hw, 2, fill=(50, 50, 50),
                 lh=13)

    # 7. ten small leads, two rows of five
    sw_ = 196
    sx = [MX + i * (sw_ + 8) for i in range(5)]
    f_num2 = font(SANS_B, 10)
    f_kick2 = font(SANS_B, 9)
    f_head2 = font(SERIF_B, 13)
    f_sub3 = font(SANS, 10)
    for row in range(2):
        iy = 392 if row == 0 else 564
        for j in range(5):
            num, tag, src, kicker, headline, sub = SMALLS[row * 5 + j]
            x0 = sx[j]
            SMALL_ART[row * 5 + j](d, x0, iy, sw_, 56)
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
            pill(d, x0 + 5, iy + 36, src, f_src, (255, 255, 255),
                 (20, 20, 20))
            ty = iy + 62
            d.text((x0, ty), kicker, font=f_kick2, fill=RED)
            put_text(d, x0, ty + 12, headline, f_head2, sw_, 3, fill=INK,
                     lh=15)
            put_text(d, x0, ty + 58, sub, f_sub3, sw_, 2, fill=(50, 50, 50),
                     lh=12)

    # 8. map + ALSO list
    # FIX: ALSO rows spaced 14px (was 15px) so the last row ends at y=904,
    # clear above the DATE CHECK box that starts at y=926.
    hy = 740
    f_h = font(SANS_B, 11)
    d.text((MX, hy), "WHERE IT HAPPENED", font=f_h, fill=INK)
    d.text((MX + 148, hy), "pins match story numbers", font=f_src,
           fill=GREY)
    d.text((340, hy), "ALSO ON SUNDAY 22 NOVEMBER \u2014 22 MORE STORIES",
           font=f_h, fill=INK)
    d.line([(MX, hy + 15), (W - MX, hy + 15)], fill=INK, width=1)
    draw_dotted_map(d, MX, hy + 22, 318, 146)
    f_br = font(SANS, 10)
    f_brn = font(SANS_B, 10)
    for k, (num, text) in enumerate(BRIEFS):
        col = 0 if k < 11 else 1
        bx = 340 if col == 0 else 686
        by = hy + 24 + (k % 11) * 14
        d.text((bx, by), str(num), font=f_brn, fill=RED)
        d.text((bx + 22, by), text, font=f_br, fill=INK)

    # 9. DATE CHECK box (red border) — FIXED: closed box y=926..981, well
    # below the last ALSO row (ends ~y=914); heading + text inside it.
    d.rectangle([MX, 926, W - MX, 981], outline=RED, width=2)
    f_dc = font(SANS_B, 11)
    d.text((MX + 8, 932), "DATE CHECK", font=f_dc, fill=RED)
    put_text(d, MX + 8, 948, DATE_CHECK[len("DATE CHECK \u2014 "):],
             font(SANS, 10), CW - 16, 2, fill=INK, lh=13)

    # 10. sources line + footer
    d.text((MX, 989), SOURCES_LINE, font=font(SANS, 9), fill=GREY)
    f_ft = font(SANS_B, 10)
    d.text((MX, 1006), "THE WORLD IN ONE DAY", font=f_ft, fill=INK)
    ft = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    d.text((W - MX - d.textlength(ft, font=f_ft), 1006), ft, font=f_ft,
           fill=INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    build()
