"""Draw the Sunday 22 November 2026 front page: 25 stories, 7 regions.

One page, one image, 1024x1024. Three heroes, twelve small leads, ten
more stories in the ALSO column, a dotted world map with numbered pins,
a UTC timeline, a stat strip, and a DATE CHECK box that names what was
deliberately kept out. Everything is drawn with Pillow primitives —
no photographs, no traced artwork, no network.

Run it once and it writes entry.png next to this file. The output is
deterministic: the same input always produces the same bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (247, 243, 232)      # warm newsprint cream
INK = (26, 26, 26)           # near-black text
NAVY = (22, 34, 63)          # top bar
NAVY_SOFT = (38, 52, 84)     # UTC bar
RED = (178, 34, 34)          # accent, DATE CHECK border
GREY = (110, 110, 105)
LIGHT_LINE = (205, 198, 180)
MAP_DOT = (178, 158, 110)

# region colours, left to right
REGION_COLOURS = [
    (46, 92, 138),    # europe — steel blue
    (14, 120, 110),   # middle east — teal
    (196, 110, 20),   # americas — ochre
    (58, 140, 70),    # asia-pacific — green
    (140, 90, 40),    # africa — brown
    (110, 80, 140),   # oceania — purple
    (90, 90, 90),     # world — grey
]

# --- fonts ---------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


# --- text helpers --------------------------------------------------------
def shrink_to_fit(draw, text, family, start, max_w):
    """Largest font of this family (<= start) that fits max_w."""
    size = start
    f = family(size)
    while size > 6 and draw.textlength(text, font=f) > max_w:
        size -= 1
        f = family(size)
    return f


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


# --- artwork: hero scenes ------------------------------------------------
def scene_drones(draw, x, y, w, h):
    """Night skyline under an orange drone glow."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 26, 48))
    for sx, sy, r in [(0.12, 0.18, 2), (0.30, 0.10, 2), (0.55, 0.14, 2),
                      (0.72, 0.08, 2), (0.88, 0.20, 2), (0.45, 0.28, 1),
                      (0.66, 0.30, 1), (0.22, 0.32, 1)]:
        px, py = x + int(sx * w), y + int(sy * h)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(240, 240, 220))
    for cx, cy, r in [(0.24, 0.30, 15), (0.70, 0.24, 18)]:
        px, py = x + int(cx * w), y + int(cy * h)
        draw.ellipse([px - r - 6, py - r - 6, px + r + 6, py + r + 6],
                     fill=(120, 70, 20))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(240, 140, 40))
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 210, 120))
    base = y + h
    blocks = [(0.00, 0.55, 0.16, 0.95), (0.17, 0.42, 0.30, 0.95),
              (0.32, 0.60, 0.45, 0.95), (0.47, 0.38, 0.60, 0.95),
              (0.62, 0.58, 0.74, 0.95), (0.76, 0.45, 0.88, 0.95),
              (0.89, 0.62, 1.00, 0.95)]
    for bx0, by0, bx1, by1 in blocks:
        draw.rectangle([x + bx0 * w, y + by0 * h, x + bx1 * w, base],
                       fill=(8, 12, 26))
        for wy in (0.55, 0.68, 0.81):
            for wx in (0.06, 0.14):
                if bx0 + wx < bx1:
                    wxp = x + (bx0 + wx) * w
                    wyp = y + wy * h
                    if wyp < base - 6:
                        draw.rectangle([wxp, wyp, wxp + 4, wyp + 5],
                                       fill=(250, 200, 90))


def scene_cop31(draw, x, y, w, h):
    """Conference hall: globe, thermometer, clock, delegates."""
    draw.rectangle([x, y, x + w, y + h], fill=(208, 226, 238))
    gx, gy, gr = x + int(0.20 * w), y + int(0.34 * h), 22
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 180))
    draw.ellipse([gx - 12, gy - 14, gx + 2, gy - 2], fill=(90, 170, 100))
    draw.ellipse([gx - 2, gy + 4, gx + 14, gy + 16], fill=(90, 170, 100))
    draw.ellipse([gx + 7, gy - 16, gx + 18, gy - 5], fill=(120, 190, 110))
    tx = x + int(0.52 * w)
    draw.rectangle([tx - 5, y + 10, tx + 5, y + h - 30], fill=(255, 255, 255),
                   outline=(120, 120, 120))
    draw.rectangle([tx - 3, y + 22, tx + 3, y + h - 32], fill=(200, 40, 40))
    draw.ellipse([tx - 8, y + h - 36, tx + 8, y + h - 20], fill=(200, 40, 40))
    cx, cy, cr = x + int(0.82 * w), y + int(0.26 * h), 13
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
                 outline=(60, 60, 60))
    draw.line([cx, cy, cx + 7, cy - 5], fill=(60, 60, 60), width=2)
    draw.line([cx, cy, cx - 2, cy + 8], fill=(60, 60, 60), width=2)
    base = y + h
    for i in range(7):
        px = x + int((0.06 + i * 0.14) * w)
        draw.ellipse([px - 5, base - 22, px + 5, base - 12], fill=(60, 60, 70))
        draw.rectangle([px - 8, base - 12, px + 8, base], fill=(90, 90, 110))
    draw.rectangle([x, base - 2, x + w, base], fill=(120, 90, 60))


def scene_radar(draw, x, y, w, h):
    """Dusk desert: radar dishes, smoke, low sun."""
    draw.rectangle([x, y, x + w, y + h], fill=(196, 120, 60))
    draw.rectangle([x, y + int(0.55 * h), x + w, y + h], fill=(150, 80, 40))
    sx, sy, sr = x + int(0.86 * w), y + int(0.30 * h), 14
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(250, 210, 130))
    for dx, dy in [(0.22, 0.42), (0.55, 0.38)]:
        px, py = x + int(dx * w), y + int(dy * h)
        draw.line([px, py, px, y + int(0.72 * h)], fill=(240, 235, 220),
                  width=4)
        draw.arc([px - 24, py - 24, px + 24, py + 6], 180, 360,
                 fill=(245, 240, 225), width=5)
        draw.line([px - 22, py - 11, px + 22, py - 11],
                  fill=(245, 240, 225), width=3)
    for cx, cy, r in [(0.38, 0.52, 11), (0.48, 0.47, 13), (0.60, 0.55, 10)]:
        px, py = x + int(cx * w), y + int(cy * h)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(210, 190, 175))


# --- artwork: small icons ------------------------------------------------
def icon_ballot(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(52, 98, 160))
    draw.rectangle([x + 8, y + 8, x + w - 8, y + h - 8], fill=(240, 240, 235))
    draw.line([x + 16, y + h - 18, x + 26, y + h - 10, x + 42, y + 12],
              fill=(40, 160, 80), width=5)


def icon_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 140, 70))
    draw.rectangle([x + 14, y + 8, x + w - 14, y + h - 8], fill=(120, 90, 50))
    for sx in (0.38, 0.48, 0.58):
        px = x + int(sx * w)
        draw.line([px, y + 12, px, y + 28], fill=(250, 240, 200), width=3)
    draw.line([x + int(0.70 * w), y + 12, x + int(0.82 * w), y + 34],
              fill=(180, 140, 90), width=5)


def icon_race(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 44, 52))
    draw.rectangle([x, y + int(0.55 * h), x + w, y + h], fill=(70, 72, 80))
    for i in range(8):
        cx = x + i * int(w / 8)
        draw.rectangle([cx, y + 3, cx + 8, y + 9],
                       fill=(255, 255, 255) if i % 2 == 0 else (20, 20, 20))
    draw.rounded_rectangle([x + 18, y + int(0.48 * h), x + w - 18,
                            y + int(0.72 * h)], radius=7, fill=(200, 40, 40))
    draw.ellipse([x + 28, y + int(0.70 * h), x + 38, y + int(0.80 * h)],
                 fill=(20, 20, 20))
    draw.ellipse([x + w - 38, y + int(0.70 * h), x + w - 28,
                  y + int(0.80 * h)], fill=(20, 20, 20))


def icon_basketball(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 120, 40))
    cx, cy, r = x + w // 2, y + h // 2, 19
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 140, 50),
                 outline=(120, 60, 20), width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=(120, 60, 20), width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=(120, 60, 20), width=2)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(120, 60, 20),
             width=2)


def icon_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(120, 160, 190))
    draw.rectangle([x, y + int(0.62 * h), x + w, y + h], fill=(50, 90, 130))
    draw.polygon([(x + 14, y + int(0.62 * h)), (x + w - 14, y + int(0.62 * h)),
                  (x + w - 26, y + int(0.78 * h)), (x + 26, y + int(0.78 * h))],
                 fill=(170, 50, 40))
    draw.rectangle([x + int(0.42 * w), y + 10, x + int(0.58 * w),
                    y + int(0.62 * h)], fill=(90, 90, 95))
    for cx, cy, r in [(0.50, 0.20, 6), (0.58, 0.14, 8)]:
        px, py = x + int(cx * w), y + int(cy * h)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(220, 215, 205))


def icon_power(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 30, 38))
    draw.polygon([(x + int(0.58 * w), y + 5), (x + int(0.34 * w),
                  y + int(0.55 * h)), (x + int(0.50 * w), y + int(0.55 * h)),
                  (x + int(0.40 * w), y + h - 5), (x + int(0.68 * w),
                  y + int(0.45 * h)), (x + int(0.52 * w), y + int(0.45 * h))],
                 fill=(250, 210, 40))


def icon_hospital(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(200, 60, 50))
    draw.rectangle([x + 10, y + 8, x + w - 10, y + h - 8], fill=(245, 245, 240))
    draw.rectangle([x + int(0.46 * w), y + 12, x + int(0.54 * w), y + h - 12],
                   fill=(200, 60, 50))
    draw.rectangle([x + 14, y + int(0.44 * h), x + w - 14,
                    y + int(0.56 * h)], fill=(200, 60, 50))


def icon_fbi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(230, 225, 210))
    draw.rectangle([x + 12, y + 8, x + w - 12, y + h - 8], fill=(255, 255, 250),
                   outline=(150, 150, 140))
    draw.ellipse([x + 20, y + 12, x + 46, y + 38], outline=(40, 40, 40), width=4)
    draw.line([x + 42, y + 34, x + 56, y + 48], fill=(40, 40, 40), width=4)
    draw.text((x + 62, y + 14), "XX", font=sans_b(15), fill=(40, 40, 40))


def icon_flights(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(150, 190, 225))
    for cx, cy, r in [(0.25, 0.25, 11), (0.70, 0.20, 13), (0.50, 0.70, 11)]:
        px, py = x + int(cx * w), y + int(cy * h)
        draw.ellipse([px - r, py - 5, px + r, py + 5], fill=(255, 255, 255))
    draw.polygon([(x + 20, y + int(0.55 * h)), (x + w - 20, y + int(0.45 * h)),
                  (x + w - 20, y + int(0.55 * h)), (x + 20, y + int(0.65 * h))],
                 fill=(240, 240, 235))


def icon_poison(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 55, 50))
    draw.polygon([(x + w // 2, y + 7), (x + w - 12, y + h - 9),
                  (x + 12, y + h - 9)], fill=(240, 200, 40),
                 outline=(20, 20, 20))
    draw.text((x + w // 2 - 5, y + int(0.40 * h)), "!", font=sans_b(18),
              fill=(20, 20, 20))


def icon_factory(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(90, 95, 105))
    draw.rectangle([x + 10, y + int(0.45 * h), x + w - 10, y + h - 7],
                   fill=(50, 52, 58))
    draw.rectangle([x + 18, y + 9, x + 26, y + int(0.45 * h)], fill=(60, 60, 66))
    draw.rectangle([x + 32, y + 16, x + 40, y + int(0.45 * h)], fill=(60, 60, 66))
    for cx, cy, r in [(0.22, 0.13, 5), (0.28, 0.09, 7)]:
        px, py = x + int(cx * w), y + int(cy * h)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(200, 195, 185))
    draw.polygon([(x + int(0.55 * w), y + h - 7), (x + int(0.65 * w), y + 24),
                  (x + int(0.75 * w), y + h - 7)], fill=(240, 140, 40))


def icon_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(190, 170, 140))
    draw.rectangle([x, y + int(0.60 * h), x + w, y + h], fill=(120, 95, 70))
    draw.line([x + 10, y + int(0.60 * h), x + int(0.35 * w), y + int(0.78 * h),
               x + int(0.55 * w), y + int(0.62 * h), x + int(0.80 * w),
               y + int(0.82 * h), x + w - 10, y + int(0.66 * h)],
              fill=(60, 45, 30), width=3)
    draw.polygon([(x + 20, y + 11), (x + 34, y + 11), (x + 34, y + 28),
                  (x + 20, y + 28)], fill=(150, 60, 50))
    draw.polygon([(x + w - 34, y + 15), (x + w - 20, y + 15),
                  (x + w - 20, y + 32), (x + w - 34, y + 32)], fill=(150, 60, 50))


# --- the dotted world map ------------------------------------------------
# Continents as ellipses in normalised (u, v): u 0..1 left to right,
# v 0..1 top to bottom of the map box.
LAND = [
    (0.17, 0.24, 0.11, 0.11), (0.07, 0.20, 0.05, 0.07),
    (0.23, 0.40, 0.035, 0.05), (0.31, 0.11, 0.035, 0.05),
    (0.25, 0.55, 0.055, 0.10), (0.26, 0.72, 0.03, 0.08),
    (0.47, 0.19, 0.055, 0.07), (0.435, 0.15, 0.018, 0.03),
    (0.49, 0.44, 0.07, 0.11), (0.51, 0.62, 0.05, 0.08),
    (0.555, 0.63, 0.015, 0.035),
    (0.66, 0.20, 0.13, 0.11), (0.70, 0.10, 0.13, 0.055),
    (0.655, 0.37, 0.045, 0.07), (0.74, 0.40, 0.05, 0.055),
    (0.78, 0.52, 0.055, 0.028), (0.875, 0.26, 0.022, 0.05),
    (0.845, 0.68, 0.06, 0.055), (0.925, 0.74, 0.018, 0.035),
]


def on_land(u, v):
    for cu, cv, ru, rv in LAND:
        if ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2 <= 1.0:
            return True
    return False


# story pins, normalised (u, v) on the same map box
PINS = {
    1: (0.53, 0.16), 2: (0.55, 0.24), 3: (0.585, 0.30),
    4: (0.80, 0.33), 5: (0.93, 0.75), 6: (0.10, 0.30),
    7: (0.145, 0.36), 8: (0.50, 0.12), 9: (0.60, 0.28),
    10: (0.28, 0.55), 11: (0.16, 0.28), 12: (0.46, 0.15),
    13: (0.72, 0.36), 14: (0.77, 0.50), 15: (0.22, 0.55),
}


def draw_world_map(draw, x, y, w, h):
    step = 10
    for gy in range(y + 4, y + h - 2, step):
        for gx in range(x + 4, x + w - 2, step):
            u = (gx - x) / w
            v = (gy - y) / h
            if on_land(u, v):
                draw.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=MAP_DOT)
    for num, (u, v) in PINS.items():
        px, py = x + int(u * w), y + int(v * h)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=(255, 255, 255))
        label = str(num)
        tw = draw.textlength(label, font=sans_b(9))
        draw.text((px - tw / 2, py - 6), label, font=sans_b(9),
                  fill=(255, 255, 255))


# --- content -------------------------------------------------------------
HEROES = [
    {
        "tag": "186 DRONES IN ONE NIGHT",
        "kicker": "1  KYIV REGION, UKRAINE  ·  WAR",
        "headline": "Russia's 186-drone night wrecks a Kyiv-region block",
        "sub": "161 of 186 drones downed, 72 jet-powered. A block in "
               "Dymer falls: 3 killed, 14 missing. (Ukrainian Air Force)",
        "cert": "REPORTED",
        "scene": scene_drones,
    },
    {
        "tag": "COP31: NO DEAL",
        "kicker": "2  ANTALYA, TÜRKIYE  ·  CLIMATE",
        "headline": "COP31 closes with no deal as fossil fuels stay out",
        "sub": "'Recalls' Dubai, keeps 35%, drops $120bn, admits 1.5°C "
               "will be overshot. The EU refuses it. (Reuters, BBC)",
        "cert": "REPORTED",
        "scene": scene_cop31,
    },
    {
        "tag": "CLAIM VS DENIAL",
        "kicker": "3  MANAMA, BAHRAIN  ·  IRAN",
        "headline": "Iran says it hit two US radars; Bahrain says no",
        "sub": "IRGC says it hit two Patriot radars. Bahrain: a civilian "
               "site burned, two injured. (Khaleej Times, Al Jazeera)",
        "cert": "CLAIM",
        "scene": scene_radar,
    },
]

SMALLS = [
    ("856 CANDIDATES", "SCMP", "4  HONG KONG  ·  ELECTION",
     "Hong Kong picks its Election Committee",
     "856 candidates, 723 seats; polls 09:00–18:00.", icon_ballot),
    ("720/9 DECLARED", "ESPN", "5  WELLINGTON  ·  CRICKET",
     "India post 720/9, a record in New Zealand",
     "Rahul 136, Pant 128; hosts 119/2, trailing by 233.", icon_cricket),
    ("VERSTAPPEN WINS", "FIA", "6  LAS VEGAS  ·  FORMULA 1",
     "Verstappen wins the Las Vegas Grand Prix",
     "35 lead changes; Norris +0.639, Piastri +1.529.", icon_race),
    ("50 POINTS", "Reuters", "7  SAN ANTONIO  ·  NBA",
     "Wembanyama drops 50, Spurs keep rolling",
     "50 pts, 19 rebounds, 5 blocks; Spurs win 114–91.", icon_basketball),
    ("SHIP ABLAZE", "Reuters", "8  GULF OF FINLAND  ·  SEA",
     "Russian cargo ship Sparta II still ablaze",
     "Hit by drones Saturday; Finland leads rescue.", icon_ship),
    ("POWER CUTS", "Wires", "9  TEHRAN, IRAN  ·  ENERGY",
     "Iran starts rationing electricity",
     "Cuts up to two hours a day as war damage bites.", icon_power),
    ("IN INTENSIVE CARE", "Reuters", "10  BRASÍLIA, BRAZIL  ·  HEALTH",
     "Bolsonaro in intensive care in Brasília",
     "Acute bowel obstruction; stable; surgery possible.", icon_hospital),
    ("FBI PROBE", "AP", "11  WASHINGTON  ·  CYBER",
     "FBI probes hack of its crime database",
     "State pauses gun-dealer checks; breach assessed.", icon_fbi),
    ("FLIGHTS GROUNDED", "Wires", "12  BRUSSELS  ·  TRAVEL",
     "Belgian controllers join Monday strike",
     "Flights grounded 07:00–21:00; controllers walk out.", icon_flights),
    ("TOLL AT 19", "Xinhua", "13  MANIPUR, INDIA  ·  POISONING",
     "Toxic-liquor death toll in Manipur reaches 19",
     "600 in hospital, six held; toll up from 16.", icon_poison),
    ("3 DEAD, 36 MISSING", "Detiknews", "14  CIKANDE, INDONESIA  ·  FIRE",
     "Cikande factory fire: 3 dead, 36 missing",
     "Blaze tore through the Banten plant; search on.", icon_factory),
    ("1 DEAD, 16 HURT", "Reuters", "15  JUNÍN, PERU  ·  QUAKE TOLL",
     "Peru quake toll: 1 dead, 16 hurt",
     "170 homes damaged in Junín; the count is completed.", icon_quake),
]

ALSO = [
    ("Europe", "Estonia to close Russia crossings 1 Dec", "Reuters"),
    ("Asia-Pacific", "Chinese bomber turns back", "AP"),
    ("Asia-Pacific", "Philippines M5.9 quake off Palawan", "EMSC"),
    ("Asia-Pacific", "Taiwan live-fire drill on Kinmen", "CNA"),
    ("Africa", "Sudan: RSF accused of killing civilians", "Claim"),
    ("Oceania", "Marles rejects US report on AUKUS", "ABC"),
    ("Americas", "Trump seeks 'permanent' Iran deal", "Al Jazeera"),
    ("Middle East", "Hamas seeks urgent mediator talks", "Al Jazeera"),
    ("World", "Bitcoin back above $60,000", "Market data"),
    ("Europe · FORECAST", "ATP final: Zverev v Alcaraz", "Forecast"),
]

REGIONS = [
    ("EUROPE 6", 6), ("MIDDLE EAST 3", 3), ("AMERICAS 6", 6),
    ("ASIA-PACIFIC 7", 7), ("AFRICA 1", 1), ("OCEANIA 1", 1),
    ("WORLD 1", 1),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"), ("03:00", "COP31 objections"),
    ("05:11", "Hamas talks"), ("05:30", "Verstappen wins"),
    ("06:00", "COP31 approval"), ("07:30", "Approval slips"),
]

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed by air"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total in NZ"),
    ("50", "points, 19 rebounds"),
]

DATE_CHECK_TEXT = (
    "Wires read to 20:15 UTC, Sun 22 Nov 2026. Each story here was "
    "reported, or still developing, on 22 Nov somewhere in the world. "
    "Left out: the 400-drone barrage (19–20 Nov); Kryvyi Rih (20 Nov); "
    "'El Chapo Isidro' (Fri); Bayelsa boat, 24 dead (Fri); Gaza aid-van "
    "strike (Sat); Poland missiles (19 Nov); Kerch Bridge (earlier); "
    "Shenzhen summit (19 Nov)."
)

SOURCES = ("Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, "
           "CNA, ABC, TOI, Guardian, Kyiv Ind., ISNA, ESPN, FIA, SCMP, "
           "Detiknews, Xinhua, EMSC. Pictures: original, drawn in code.")

LEGEND = ("CERTAINTY: REPORTED = carried by the day's wires · CLAIM = one "
          "side's account, labelled as such · FORECAST = still to happen "
          "when drawn")


# --- build ---------------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # top bar
    draw.rectangle([0, 0, W, 20], fill=NAVY)
    draw.text((12, 4), "THE WORLD IN ONE DAY", font=sans_b(10),
              fill=(255, 255, 255))
    right = "25 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    tw = draw.textlength(right, font=sans_b(10))
    draw.text((W - 12 - tw, 4), right, font=sans_b(10), fill=(255, 255, 255))

    # masthead
    mast = shrink_to_fit(draw, "Sunday 22 November 2026", serif_b, 74, 1000)
    mw = draw.textlength("Sunday 22 November 2026", font=mast)
    draw.text(((W - mw) / 2, 22), "Sunday 22 November 2026", font=mast,
              fill=INK)

    # red subline
    subline = ("A night of 186 drones over Ukraine  ·  COP31 closes without "
               "a deal  ·  Iran's radar claim answered by Bahrain's denial")
    sf = shrink_to_fit(draw, subline, serif, 17, 1000)
    sw = draw.textlength(subline, font=sf)
    draw.text(((W - sw) / 2, 92), subline, font=sf, fill=RED)

    # stat strip
    col_w = 1000 / 6
    for i, (num, cap) in enumerate(STATS):
        cx = 12 + i * col_w
        if i:
            draw.line([cx - 6, 112, cx - 6, 156], fill=LIGHT_LINE, width=1)
        draw.text((cx, 108), num, font=serif_b(30), fill=RED)
        cap_lines = wrap(draw, cap, sans(9), col_w - 12)
        draw_lines(draw, cap_lines[:2], cx, 140, sans(9), INK, 11)

    # region bar
    total = sum(n for _, n in REGIONS)
    bar_x, bar_y, bar_w, bar_h = 12, 160, 1000, 18
    widths = [max(60, int(n / total * bar_w)) for _, n in REGIONS]
    over = sum(widths) - bar_w
    idx = max(range(len(widths)), key=lambda i: widths[i])
    widths[idx] -= over
    x = bar_x
    for (label, _), wseg, colour in zip(REGIONS, widths, REGION_COLOURS):
        draw.rectangle([x, bar_y, x + wseg, bar_y + bar_h], fill=colour)
        lf = sans_b(10)
        lw = draw.textlength(label, font=lf)
        draw.text((x + (wseg - lw) / 2, bar_y + 3), label, font=lf,
                  fill=(255, 255, 255))
        x += wseg

    # UTC bar
    draw.rectangle([12, 182, 1012, 200], fill=NAVY_SOFT)
    draw.text((18, 185), "THE DAY IN UTC", font=sans_b(10),
              fill=(255, 220, 120))
    ux = 150
    for t, ev in UTC_EVENTS:
        draw.text((ux, 185), t, font=sans_b(10), fill=(255, 220, 120))
        tw = draw.textlength(t, font=sans_b(10))
        draw.text((ux + tw + 5, 185), ev, font=sans(10),
                  fill=(255, 255, 255))
        ux += tw + 5 + draw.textlength(ev, font=sans(10)) + 26

    # heroes: y 206–365
    hero_y = 206
    col_w = 325
    gap = 12
    for i, hero in enumerate(HEROES):
        hx = 12 + i * (col_w + gap)
        draw.rectangle([hx, hero_y, hx + col_w, hero_y + 16],
                       fill=(140, 30, 30))
        draw.text((hx + 6, hero_y + 2), hero["tag"], font=sans_b(10),
                  fill=(255, 255, 255))
        hero["scene"](draw, hx, hero_y + 16, col_w, 64)
        ky = hero_y + 16 + 64 + 4
        draw.text((hx, ky), hero["kicker"], font=sans_b(9), fill=INK)
        cw = draw.textlength(hero["cert"], font=sans_b(9))
        draw.text((hx + col_w - cw, ky), hero["cert"], font=sans_b(9),
                  fill=GREY)
        hf = serif_b(20)
        hl = wrap(draw, hero["headline"], hf, col_w)
        hy = ky + 13
        draw_lines(draw, hl[:2], hx, hy, hf, INK, 22)
        suf = sans(10)
        sl = wrap(draw, hero["sub"], suf, col_w)
        draw_lines(draw, sl[:2], hx, hy + 44, suf, INK, 12)

    # small leads, two rows of six: rows start y 375 and 508
    small_w = 160
    small_gap = 8
    for r, ry in enumerate([375, 508]):
        for c in range(6):
            tag, src, kicker, head, sub, icon = SMALLS[r * 6 + c]
            sx = 12 + c * (small_w + small_gap)
            draw.rectangle([sx, ry, sx + small_w, ry + 15], fill=(140, 30, 30))
            tf = shrink_to_fit(draw, tag, sans_b, 10, small_w - 8)
            draw.text((sx + 4, ry + 2), tag, font=tf, fill=(255, 255, 255))
            icon(draw, sx, ry + 15, small_w, 46)
            num = str(r * 6 + c + 4)
            draw.ellipse([sx + small_w - 22, ry + 19, sx + small_w - 6,
                          ry + 35], fill=RED, outline=(255, 255, 255))
            nw = draw.textlength(num, font=sans_b(9))
            draw.text((sx + small_w - 14 - nw / 2, ry + 22), num,
                      font=sans_b(9), fill=(255, 255, 255))
            draw.text((sx + 4, ry + 15 + 46 - 12), src, font=sans_b(8),
                      fill=(255, 255, 255))
            ky = ry + 15 + 46 + 3
            kf = shrink_to_fit(draw, kicker, sans_b, 9, small_w)
            draw.text((sx, ky), kicker, font=kf, fill=INK)
            hf = serif_b(12)
            hl = wrap(draw, head, hf, small_w)
            draw_lines(draw, hl[:2], sx, ky + 12, hf, INK, 14)
            suf = sans(9)
            sl = wrap(draw, sub, suf, small_w)
            draw_lines(draw, sl[:2], sx, ky + 12 + 28, suf, INK, 11)

    # bottom block divider + headings
    draw.line([12, 641, 1012, 641], fill=INK, width=1)
    draw.text((12, 647), "WHERE IT HAPPENED", font=sans_b(11), fill=INK)
    draw.text((12, 662), "pins match story numbers", font=sans(9), fill=GREY)
    draw.text((448, 647), "ALSO ON SUNDAY 22 NOVEMBER — 10 MORE STORIES",
              font=sans_b(11), fill=INK)
    draw.line([440, 647, 440, 912], fill=LIGHT_LINE, width=1)

    # enlarged dotted map, left
    draw_world_map(draw, 12, 680, 418, 232)

    # ALSO list, single column, generous leading
    ay = 680
    for i, (region, brief, src) in enumerate(ALSO):
        num = 16 + i
        line = "%d  %s: %s (%s)" % (num, region, brief, src)
        draw.text((448, ay), line, font=sans(11), fill=INK)
        ay += 23

    # DATE CHECK box — closed red rectangle, proven geometry
    draw.rectangle([12, 926, 1012, 981], outline=RED, width=2)
    draw.text((20, 931), "DATE CHECK", font=sans_b(10), fill=RED)
    dc = wrap(draw, DATE_CHECK_TEXT, sans(9), 972)
    draw_lines(draw, dc[:2], 20, 946, sans(9), INK, 12)

    # sources, legend, footer
    draw.text((12, 986), SOURCES, font=sans(8), fill=GREY)
    draw.text((12, 998), LEGEND, font=sans(8), fill=GREY)
    foot = "SUNDAY 22 NOVEMBER 2026  ·  ONE PAGE"
    fw = draw.textlength(foot, font=sans_b(9))
    draw.text((W - 12 - fw, 998), foot, font=sans_b(9), fill=INK)

    img.save(OUT)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
