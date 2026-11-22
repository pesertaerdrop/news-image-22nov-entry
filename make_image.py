#!/usr/bin/env python3
"""Draw the Sunday 22 November 2026 front page: 36 stories, 7 regions.

One 1024x1024 RGB page, drawn entirely with Pillow primitives -- no photos,
no traced artwork, no network. The layout is a dense broadsheet: a navy
top bar, a big serif masthead, a six-number stat strip, a coloured region
bar, a "THE DAY IN UTC" timeline, three hero stories, twelve small leads,
a dotted world map with numbered pins, an ALSO column of 21 more stories,
and a closed DATE CHECK box that names what was deliberately left out.

Every number on the page was checked against the day's wires before the
build; stories that belong to earlier days are named in DATE CHECK instead
of being smuggled into the page. Heroes carry a certainty label
(REPORTED / CLAIM / FORECAST) so the reader can tell a wire fact from one
side's account or an event still to come.

Run:  python3 make_image.py            (writes entry.png next to this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 12                      # side margin
RIGHT = W - MX               # 1012

# ---------------------------------------------------------------- palette
CREAM = (246, 241, 227)
PAPER = (250, 247, 238)
NAVY = (16, 32, 78)
DARK = (18, 18, 18)
RED = (178, 34, 34)
BRICK = (150, 30, 30)
GOLD = (255, 196, 66)
GREY = (110, 110, 110)
LINE = (200, 190, 168)
DOT = (179, 155, 94)

REGION_COLOURS = [
    ("EUROPE 8", (52, 96, 150)),
    ("MIDDLE EAST 4", (178, 34, 34)),
    ("AMERICAS 7", (22, 130, 130)),
    ("ASIA-PACIFIC 9", (150, 130, 30)),
    ("AFRICA 3", (140, 100, 60)),
    ("OCEANIA 3", (70, 80, 100)),
    ("WORLD 2", (110, 110, 110)),
]

# ---------------------------------------------------------------- fonts
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(names, size):
    for name in names:
        path = os.path.join(_FONT_DIR, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def serif_b(size):
    return _load(["DejaVuSerif-Bold.ttf"], size)


def serif_i(size):
    return _load(["DejaVuSerif-Italic.ttf", "DejaVuSerif.ttf"], size)


def sans(size):
    return _load(["DejaVuSans.ttf"], size)


def sans_b(size):
    return _load(["DejaVuSans-Bold.ttf"], size)


# ---------------------------------------------------------------- text tools
def wrap(drw, text, font, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if drw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(drw, x, y, text, font, colour, max_w, lh, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(drw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        drw.text((x, y), line, font=font, fill=colour)
        y += lh
    return y


def chip(drw, x, y, text, font, bg, fg=(255, 255, 255)):
    """Small filled label; returns the x just past its right edge."""
    w = int(drw.textlength(text, font=font)) + 10
    h = font.size + 7
    drw.rectangle([x, y, x + w, y + h], fill=bg)
    drw.text((x + 5, y + 3), text, font=font, fill=fg)
    return x + w


def num_badge(drw, cx, cy, n, r=8):
    """Red circle with a white story number, centred on (cx, cy)."""
    f = sans_b(9)
    drw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                outline=(255, 255, 255), width=1)
    t = str(n)
    tw = drw.textlength(t, font=f)
    drw.text((cx - tw / 2, cy - 5), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- hero scenes
def scene_drones(drw, x, y, w, h):
    """Night skyline under a drone raid: dark sky, lit windows, blasts."""
    drw.rectangle([x, y, x + w, y + h], fill=(14, 22, 46))
    for i in range(26):  # fixed stars, no randomness
        sx = x + (i * 53 + 11) % w
        sy = y + (i * 29 + 7) % (h // 2)
        drw.point((sx, sy), fill=(220, 220, 230))
    # buildings
    bases = [(0, 58, 46, 30), (52, 40, 40, 48), (98, 64, 52, 24),
             (156, 34, 44, 54), (206, 56, 48, 32), (260, 44, 40, 44)]
    for bx, bt, bw, bh in bases:
        drw.rectangle([x + bx, y + bt, x + bx + bw, y + h], fill=(28, 40, 70))
        for wy in range(y + bt + 6, y + h - 6, 10):
            for wx in range(x + bx + 5, x + bx + bw - 5, 10):
                if (wx + wy) % 3 == 0:
                    drw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 200, 90))
    # two blasts
    for ex, ey, r in [(70, 46, 16), (230, 40, 13)]:
        drw.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r],
                    fill=(255, 140, 40))
        drw.polygon([(x + ex - 8, y + ey + 12), (x + ex, y + ey - 14),
                     (x + ex + 8, y + ey + 12)], fill=(255, 210, 80))
    # three drones overhead
    for dx, dy in [(120, 14), (180, 22), (290, 12)]:
        drw.ellipse([x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 2],
                    fill=(10, 10, 14))
        drw.point((x + dx, y + dy), fill=(255, 60, 60))


def scene_cop31(drw, x, y, w, h):
    """Climate hall: a globe, a thermometer, delegates, a clock."""
    drw.rectangle([x, y, x + w, y + h], fill=(205, 225, 238))
    # globe
    gx, gy, gr = x + 58, y + 46, 30
    drw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 140, 200),
                outline=(30, 80, 140), width=2)
    for ex, ey, er in [(gx - 10, gy - 8, 10), (gx + 12, gy + 6, 9),
                       (gx + 2, gy - 16, 6)]:
        drw.ellipse([ex - er, ey - er // 2, ex + er, ey + er // 2],
                    fill=(90, 180, 90))
    # thermometer
    tx = x + 150
    drw.rectangle([tx, y + 12, tx + 12, y + 66], fill=(255, 255, 255),
                  outline=(120, 120, 120), width=1)
    drw.rectangle([tx + 2, y + 34, tx + 10, y + 64], fill=(200, 40, 40))
    drw.ellipse([tx - 3, y + 62, tx + 15, y + 80], fill=(200, 40, 40))
    # clock
    cx, cy, cr = x + 268, y + 30, 20
    drw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
                outline=(40, 40, 40), width=2)
    drw.line([cx, cy, cx, cy - 12], fill=(40, 40, 40), width=2)
    drw.line([cx, cy, cx + 9, cy + 5], fill=(40, 40, 40), width=2)
    # delegates along the bottom
    for i in range(9):
        dx = x + 20 + i * 32
        drw.ellipse([dx, y + h - 26, dx + 12, y + h - 14], fill=(240, 200, 160))
        drw.rectangle([dx - 2, y + h - 14, dx + 14, y + h], fill=(60, 80, 120))


def scene_radar(drw, x, y, w, h):
    """Dusk at a radar site: two dishes, smoke kept inside the frame."""
    for i in range(6):  # dusk bands, orange fading to brown
        drw.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6],
                      fill=(216 - i * 14, 130 - i * 12, 74 - i * 6))
    # low sun
    drw.ellipse([x + w - 52, y + 10, x + w - 20, y + 42], fill=(250, 220, 150))
    # dish one (left, big)
    drw.line([x + 70, y + h - 8, x + 70, y + 34], fill=(240, 240, 240), width=4)
    drw.arc([x + 34, y + 8, x + 106, y + 62], start=200, end=340,
            fill=(245, 245, 245), width=5)
    drw.line([x + 70, y + 34, x + 46, y + 18], fill=(240, 240, 240), width=3)
    # dish two (right, smaller)
    drw.line([x + 220, y + h - 8, x + 220, y + 48], fill=(240, 240, 240), width=4)
    drw.arc([x + 196, y + 26, x + 244, y + 66], start=200, end=340,
            fill=(245, 245, 245), width=4)
    # smoke, centres low enough that no puff leaves the picture
    for sx, sy, sr in [(150, 58, 16), (180, 66, 20), (120, 68, 12)]:
        drw.ellipse([x + sx - sr, y + sy - 8, x + sx + sr, y + sy + 8],
                    fill=(165, 150, 135))
    drw.rectangle([x, y + h - 8, x + w, y + h], fill=(60, 50, 44))


# ---------------------------------------------------------------- small icons
def icon_ballot(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(70, 110, 180))
    drw.rectangle([x + 58, y + 16, x + 106, y + 40], fill=(245, 245, 245))
    drw.rectangle([x + 72, y + 10, x + 92, y + 18], fill=(40, 40, 40))
    drw.line([x + 66, y + 30, x + 76, y + 38, x + 98, y + 20],
             fill=(30, 160, 60), width=4)


def icon_cricket(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(60, 130, 70))
    drw.polygon([(x + 70, y + 6), (x + 82, y + 6), (x + 96, y + 40),
                 (x + 84, y + 40)], fill=(200, 160, 110))
    drw.ellipse([x + 112, y + 10, x + 124, y + 22], fill=(200, 40, 40))
    for sx in (36, 46, 56):
        drw.rectangle([x + sx, y + 28, x + sx + 3, y + 42], fill=(245, 230, 180))


def icon_race(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(35, 35, 48))
    drw.rectangle([x + 44, y + 20, x + 120, y + 34], fill=(220, 40, 40))
    drw.polygon([(x + 60, y + 20), (x + 74, y + 10), (x + 100, y + 10),
                 (x + 108, y + 20)], fill=(240, 240, 240))
    for wx in (58, 104):
        drw.ellipse([x + wx, y + 32, x + wx + 14, y + 44], fill=(15, 15, 15))
    for lx in (18, 26, 34):
        drw.line([x + lx, y + 26, x + lx + 10, y + 26], fill=(255, 220, 90),
                 width=2)


def icon_basket(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(230, 120, 40))
    drw.ellipse([x + 58, y + 6, x + 102, y + 42], fill=(200, 90, 30),
                outline=(120, 50, 10), width=2)
    drw.line([x + 58, y + 24, x + 102, y + 24], fill=(120, 50, 10), width=2)
    drw.line([x + 80, y + 6, x + 80, y + 42], fill=(120, 50, 10), width=2)
    drw.arc([x + 58, y + 6, x + 102, y + 42], start=300, end=60,
            fill=(120, 50, 10), width=2)


def icon_ship(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(25, 55, 95))
    drw.polygon([(x + 34, y + 30), (x + 126, y + 30), (x + 112, y + 42),
                 (x + 48, y + 42)], fill=(180, 60, 40))
    drw.rectangle([x + 66, y + 12, x + 78, y + 30], fill=(220, 220, 220))
    drw.ellipse([x + 60, y + 2, x + 78, y + 14], fill=(120, 120, 120))
    for wx in (20, 60, 100, 140):
        drw.arc([x + wx, y + 40, x + wx + 18, y + 48], start=0, end=180,
                fill=(120, 180, 220), width=2)


def icon_bolt(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(250, 210, 60))
    drw.polygon([(x + 88, y + 4), (x + 62, y + 28), (x + 78, y + 28),
                 (x + 68, y + 44), (x + 98, y + 20), (x + 82, y + 20)],
                fill=(30, 30, 30))


def icon_hospital(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(225, 232, 238))
    drw.rectangle([x + 34, y + 28, x + 126, y + 34], fill=(90, 140, 180))
    drw.ellipse([x + 40, y + 20, x + 54, y + 30], fill=(240, 200, 160))
    drw.rectangle([x + 118, y + 8, x + 142, y + 32], fill=(255, 255, 255),
                  outline=(200, 40, 40), width=2)
    drw.rectangle([x + 128, y + 12, x + 132, y + 28], fill=(200, 40, 40))
    drw.rectangle([x + 122, y + 18, x + 138, y + 22], fill=(200, 40, 40))


def icon_magnify(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(200, 205, 210))
    drw.ellipse([x + 48, y + 6, x + 92, y + 42], fill=(255, 255, 255),
                outline=(30, 30, 30), width=3)
    drw.line([x + 84, y + 34, x + 108, y + 46], fill=(30, 30, 30), width=5)
    for lx in (58, 66, 74):
        drw.arc([x + lx, y + 14, x + lx + 16, y + 34], start=200, end=340,
                fill=(90, 90, 90), width=2)


def icon_plane(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(150, 200, 235))
    drw.polygon([(x + 20, y + 26), (x + 110, y + 18), (x + 140, y + 24),
                 (x + 110, y + 30), (x + 20, y + 30)], fill=(245, 245, 245))
    drw.polygon([(x + 70, y + 18), (x + 82, y + 8), (x + 92, y + 18)],
                fill=(220, 220, 220))
    for cx, cy in [(30, 10), (120, 38)]:
        drw.ellipse([x + cx, y + cy, x + cx + 22, y + cy + 8],
                    fill=(255, 255, 255))


def icon_warn(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(245, 180, 40))
    drw.polygon([(x + 80, y + 6), (x + 118, y + 42), (x + 42, y + 42)],
                fill=(30, 30, 30))
    drw.rectangle([x + 77, y + 18, x + 83, y + 32], fill=(245, 180, 40))
    drw.rectangle([x + 77, y + 35, x + 83, y + 39], fill=(245, 180, 40))


def icon_factory(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(150, 70, 50))
    drw.polygon([(x + 30, y + 44), (x + 30, y + 22), (x + 52, y + 30),
                 (x + 66, y + 18), (x + 84, y + 30), (x + 100, y + 22),
                 (x + 130, y + 22), (x + 130, y + 44)], fill=(60, 40, 36))
    drw.ellipse([x + 108, y + 4, x + 122, y + 14], fill=(120, 120, 120))
    drw.polygon([(x + 58, y + 44), (x + 66, y + 30), (x + 74, y + 44)],
                fill=(255, 160, 40))


def icon_mountains(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(90, 90, 140))
    drw.polygon([(x + 20, y + 44), (x + 70, y + 10), (x + 110, y + 44)],
                fill=(60, 60, 100))
    drw.polygon([(x + 62, y + 16), (x + 70, y + 10), (x + 78, y + 16),
                 (x + 70, y + 20)], fill=(255, 255, 255))
    drw.polygon([(x + 80, y + 44), (x + 120, y + 18), (x + 150, y + 44)],
                fill=(80, 80, 120))
    drw.polygon([(x + 114, y + 23), (x + 120, y + 18), (x + 126, y + 23),
                 (x + 120, y + 27)], fill=(255, 255, 255))


# ---------------------------------------------------------------- data
STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed by air"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total in NZ"),
    ("50", "points, 19 rebounds"),
]

UTC_ITEMS = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections end"),
    ("05:11", "Hamas seeks talks"),
    ("05:30", "Verstappen wins"),
    ("06:00", "COP31 approval due"),
    ("07:30", "Approval slips"),
]

HEROES = [
    dict(num=1, place="KYIV REGION, UKRAINE", topic="WAR",
         label="REPORTED", chip="186 DRONES IN ONE NIGHT",
         source="Ukrainian Air Force", scene=scene_drones,
         head="Russia's 186-drone night wrecks a Kyiv-region block",
         sub="161 of 186 drones downed, 72 jet-powered. A block in Dymer "
             "falls: 3 killed, 14 missing. (Ukrainian Air Force)"),
    dict(num=2, place="ANTALYA, TÜRKIYE", topic="CLIMATE",
         label="REPORTED", chip="COP31: NO DEAL",
         source="COP31 presidency", scene=scene_cop31,
         head="COP31 closes with no deal as fossil fuels stay out",
         sub="'Recalls' Dubai, keeps 35%, drops $120bn, admits 1.5°C will "
             "be overshot. The EU refuses it. (Reuters, BBC)"),
    dict(num=3, place="MANAMA, BAHRAIN", topic="IRAN",
         label="CLAIM", chip="CLAIM VS DENIAL",
         source="IRGC / Bahrain", scene=scene_radar,
         head="Iran says it hit two US radars; Bahrain says no",
         sub="IRGC says it hit two Patriot radars. Bahrain: a civilian "
             "site burned, two injured. (Khaleej Times, Al Jazeera)"),
]

SMALLS = [
    dict(num=4, place="HONG KONG", topic="ELECTION", chip="856 CANDIDATES",
         source="SCMP", icon=icon_ballot,
         head="Hong Kong picks its Election Committee",
         sub="856 candidates, 723 seats; polls 09:00–18:00."),
    dict(num=5, place="WELLINGTON", topic="CRICKET", chip="720/9 DECLARED",
         source="ESPN", icon=icon_cricket,
         head="India post 720/9, a record in New Zealand",
         sub="Rahul 136, Pant 128; hosts 119/2, trailing by 233."),
    dict(num=6, place="LAS VEGAS", topic="FORMULA 1", chip="VERSTAPPEN WINS",
         source="FIA", icon=icon_race,
         head="Verstappen wins the Las Vegas Grand Prix",
         sub="35 lead changes; Norris +0.639, Piastri +1.529."),
    dict(num=7, place="SAN ANTONIO", topic="NBA", chip="50 POINTS",
         source="Reuters", icon=icon_basket,
         head="Wembanyama drops 50 as the Spurs keep rolling",
         sub="50 pts, 19 rebounds, 5 blocks; Spurs win 114–91."),
    dict(num=8, place="GULF OF FINLAND", topic="SEA", chip="SHIP ABLAZE",
         source="Reuters", icon=icon_ship,
         head="Russian cargo ship Sparta II still ablaze",
         sub="Hit by drones Saturday; Finland leads rescue."),
    dict(num=9, place="TEHRAN, IRAN", topic="ENERGY", chip="POWER CUTS",
         source="Wires", icon=icon_bolt,
         head="Iran starts rationing electricity",
         sub="Cuts up to two hours a day as war damage bites."),
    dict(num=10, place="BRASÍLIA, BRAZIL", topic="HEALTH",
         chip="IN INTENSIVE CARE", source="Reuters", icon=icon_hospital,
         head="Bolsonaro in intensive care in Brasília",
         sub="Acute bowel obstruction; stable; surgery possible."),
    dict(num=11, place="WASHINGTON", topic="CYBER", chip="FBI PROBE",
         source="AP", icon=icon_magnify,
         head="FBI investigates apparent hack of its crime database",
         sub="State pauses gun-dealer checks; breach assessed."),
    dict(num=12, place="BRUSSELS", topic="TRAVEL", chip="FLIGHTS GROUNDED",
         source="Wires", icon=icon_plane,
         head="Belgian controllers join Monday's national strike",
         sub="Flights grounded 07:00–21:00; controllers walk out."),
    dict(num=13, place="MANIPUR, INDIA", topic="POISONING", chip="TOLL AT 19",
         source="Xinhua", icon=icon_warn,
         head="Toxic-liquor death toll in Manipur reaches 19",
         sub="600 in hospital, six held; toll up from 16."),
    dict(num=14, place="CIKANDE, INDONESIA", topic="FIRE",
         chip="3 DEAD, 36 MISSING", source="Detiknews", icon=icon_factory,
         head="Cikande factory fire: 3 dead, 36 missing",
         sub="Blaze tore through the Banten plant; search on."),
    dict(num=15, place="JUNÍN, PERU", topic="QUAKE TOLL",
         chip="1 DEAD, 16 HURT", source="Reuters", icon=icon_mountains,
         head="Peru quake toll revised: 1 dead, 16 hurt",
         sub="170 homes damaged in Junín; the count is completed."),
]

ALSO = [
    "Europe: Estonia to close Russia crossings 1 Dec (Reuters)",
    "Europe: Denmark expels Russian attaché (Guardian)",
    "Asia-Pacific: Nepal PM Shah arrives in Delhi (IANS)",
    "Asia-Pacific: Chinese bomber turns back (AP)",
    "Asia-Pacific: Philippines M5.9 quake off Palawan (EMSC)",
    "Asia-Pacific: Japan poll: 92% friendly to S. Korea (IKN)",
    "Asia-Pacific: Taiwan live-fire drill on Kinmen (CNA)",
    "Africa: Somalia expels UAE ambassador (Wires)",
    "Africa: Sudan: RSF accused of killing civilians (Claim)",
    "Africa: Kenya discharges last Ebola patient (Wires)",
    "Oceania: Marles rejects US report on AUKUS (ABC)",
    "Oceania: Melbourne: 70 years since 1956 Olympics (ABC)",
    "Oceania: Cummins keeps Australia's captaincy (Wires)",
    "Americas: Trump seeks 'permanent' Iran deal (Al Jazeera)",
    "Middle East: Eisenkot invites Likud to talks (Straits Times)",
    "Americas: Nvidia faces SEC probe, say reports (Reports)",
    "Middle East: Hamas seeks urgent mediator talks (Al Jazeera)",
    "World: Bitcoin back above $60,000 (Market data)",
    "World: Gold holds near $3,535 (Reuters)",
    "Europe · FORECAST: ATP final: Zverev v Alcaraz (Forecast)",
    "Europe · FORECAST: Liverpool host Man Utd (Forecast)",
]

DATE_CHECK_TEXT = (
    "Wires read to 20:15 UTC, Sun 22 Nov 2026. Each story here was "
    "reported, or still developing, on 22 Nov somewhere in the world. "
    "Left out: the 400-drone barrage (19–20 Nov); Kryvyi Rih (20 Nov); "
    "'El Chapo Isidro' (Fri); Bayelsa boat, 24 dead (Fri); Gaza aid-van "
    "strike (Sat); Poland missiles (19 Nov); Kerch Bridge (earlier); "
    "Shenzhen summit (19 Nov)."
)

SOURCES_LINE = (
    "Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, CNA, "
    "ABC, TOI, Guardian, Kyiv Ind., ISNA, ESPN, FIA, SCMP, Detiknews, "
    "Xinhua, EMSC. Pictures: original, drawn in code."
)

LEGEND_LINE = (
    "CERTAINTY: REPORTED = carried by the day's wires · CLAIM = one side's "
    "account, labelled as such · FORECAST = still to happen when drawn"
)

# dotted-map landmasses: (lon centre, lat centre, lon radius, lat radius)
LAND = [
    (-100, 48, 55, 20), (-155, 65, 18, 8), (-42, 74, 15, 9),
    (-88, 13, 12, 6), (-60, -15, 18, 28), (15, 52, 22, 12),
    (15, 63, 12, 7), (18, 5, 22, 30), (22, -22, 14, 12),
    (45, 28, 12, 10), (100, 58, 70, 16), (79, 21, 9, 12),
    (103, 13, 12, 10), (118, -2, 20, 6), (110, 35, 18, 12),
    (134, -25, 18, 11), (172, -41, 5, 6), (138, 38, 6, 8),
    (-2, 54, 4, 5),
]

# story number -> (lon, lat) for the map pins
PINS = {
    1: (30.5, 50.5), 2: (30.7, 36.9), 3: (50.6, 26.2), 4: (114.2, 22.3),
    5: (174.8, -41.3), 6: (-115.1, 36.2), 7: (-98.5, 29.4),
    8: (24.0, 62.0), 9: (51.4, 35.7), 10: (-47.9, -15.8),
    11: (-77.0, 38.9), 12: (4.4, 50.8), 13: (93.9, 24.7),
    14: (106.3, -6.2), 15: (-75.9, -11.2),
}


def on_land(lon, lat):
    for cx, cy, rx, ry in LAND:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1.0:
            return True
    return False


# ---------------------------------------------------------------- page build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- top bar
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((MX, 5), "THE WORLD IN ONE DAY", font=sans_b(13),
           fill=(255, 255, 255))
    tail = "36 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - MX - d.textlength(tail, font=sans_b(11)), 6), tail,
           font=sans_b(11), fill=(255, 255, 255))

    # ---- masthead + red subline
    mast = "Sunday 22 November 2026"
    f_mast = serif_b(62)
    d.text(((W - d.textlength(mast, font=f_mast)) / 2, 28), mast,
           font=f_mast, fill=DARK)
    sub = ("A night of 186 drones over Ukraine · COP31 closes without a "
           "deal · Iran's radar claim answered by Bahrain's denial")
    f_sub = serif_i(15)
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 98), sub,
           font=f_sub, fill=RED)

    # ---- stat strip
    y0, y1 = 116, 156
    cell = (RIGHT - MX) / len(STATS)
    for i, (num, cap) in enumerate(STATS):
        cx = MX + i * cell
        f_n = sans_b(26)
        d.text((cx + 6, y0), num, font=f_n, fill=RED)
        para(d, cx + 6, y0 + 28, cap, sans(9), DARK, cell - 12, 11,
             max_lines=1)
        if i:
            d.line([cx, y0 + 2, cx, y1 - 2], fill=LINE, width=1)
    d.line([MX, y1 + 2, RIGHT, y1 + 2], fill=DARK, width=1)

    # ---- region bar
    y0, y1 = 158, 176
    total = sum(int(lbl.rsplit(" ", 1)[1]) for lbl, _ in REGION_COLOURS)
    x = MX
    for lbl, col in REGION_COLOURS:
        wseg = (RIGHT - MX) * int(lbl.rsplit(" ", 1)[1]) / total
        d.rectangle([x, y0, x + wseg, y1], fill=col)
        f_r = sans_b(11)
        tw = d.textlength(lbl, font=f_r)
        # keep the label inside its own segment
        tx = min(x + 5, x + wseg - tw - 3)
        d.text((tx, y0 + 3), lbl, font=f_r, fill=(255, 255, 255))
        x += wseg

    # ---- UTC bar (gap shrinks so the last item never runs past the edge)
    y0, y1 = 178, 194
    d.rectangle([MX, y0, RIGHT, y1], fill=NAVY)
    d.text((MX + 6, y0 + 3), "THE DAY IN UTC", font=sans_b(11),
           fill=(255, 255, 255))
    f_t, f_w = sans_b(10), sans(10)
    widths = [d.textlength(tm, font=f_t) + 5 + d.textlength(what, font=f_w)
              for tm, what in UTC_ITEMS]
    avail = RIGHT - (MX + 130)
    gap = max(6, (avail - sum(widths)) // (len(UTC_ITEMS) - 1))
    x = MX + 130
    for (tm, what), wd in zip(UTC_ITEMS, widths):
        d.text((x, y0 + 3), tm, font=f_t, fill=GOLD)
        x += d.textlength(tm, font=f_t) + 5
        d.text((x, y0 + 3), what, font=f_w, fill=(255, 255, 255))
        x += d.textlength(what, font=f_w) + gap

    # ---- three heroes
    col_w, gap = 324, 14
    for i, hero in enumerate(HEROES):
        x = MX + i * (col_w + gap)
        hero["scene"](d, x, 198, col_w, 92)
        chip(d, x, 198, hero["chip"], sans_b(10), RED)
        src = hero["source"]
        sw = d.textlength(src, font=sans(9)) + 10
        d.rectangle([x, 290 - 16, x + sw, 290], fill=(20, 20, 20))
        d.text((x + 5, 290 - 13), src, font=sans(9), fill=(255, 255, 255))
        # kicker + certainty label
        kick = "%d %s · %s" % (hero["num"], hero["place"], hero["topic"])
        d.text((x, 294), kick, font=sans_b(10), fill=RED)
        lab = hero["label"]
        d.text((x + col_w - d.textlength(lab, font=sans_b(9)), 295), lab,
               font=sans_b(9), fill=GREY)
        # headline, then the sub directly below it (no fixed y, no overlap)
        ty = para(d, x, 308, hero["head"], serif_b(20), DARK, col_w, 22,
                  max_lines=3)
        para(d, x, ty + 4, hero["sub"], sans(11), DARK, col_w, 13,
             max_lines=2)

    # ---- twelve small leads, two rows of six
    sw_, sgap = 160, 8
    for i, lead in enumerate(SMALLS):
        row, col = divmod(i, 6)
        x = MX + col * (sw_ + sgap)
        pic_y = 398 + row * 132
        lead["icon"](d, x, pic_y, sw_, 48)
        chip(d, x, pic_y, lead["chip"], sans_b(9), RED)
        num_badge(d, x + sw_ - 12, pic_y + 12, lead["num"])
        src = lead["source"]
        sw = d.textlength(src, font=sans(8)) + 8
        d.rectangle([x, pic_y + 48 - 13, x + sw, pic_y + 48], fill=(20, 20, 20))
        d.text((x + 4, pic_y + 48 - 11), src, font=sans(8),
               fill=(255, 255, 255))
        ty = pic_y + 52
        d.text((x, ty), "%d %s · %s" % (lead["num"], lead["place"],
                                        lead["topic"]),
               font=sans_b(9), fill=RED)
        para(d, x, ty + 13, lead["head"], sans_b(12), DARK, sw_, 14,
             max_lines=3)
        para(d, x, ty + 55, lead["sub"], sans(10), DARK, sw_, 11,
             max_lines=2)

    # ---- map + ALSO
    d.text((MX, 662), "WHERE IT HAPPENED", font=sans_b(11), fill=DARK)
    d.text((MX, 675), "pins match story numbers", font=sans(9), fill=GREY)
    d.text((340, 662), "ALSO ON SUNDAY 22 NOVEMBER — 21 MORE STORIES",
           font=sans_b(11), fill=DARK)
    d.line([MX, 690, RIGHT, 690], fill=DARK, width=1)
    # dotted map: x 16..326, y 696..912, equirectangular
    map_x0, map_y0, map_x1, map_y1 = 16, 696, 326, 912
    for py in range(map_y0, map_y1, 7):
        lat = 84.0 - (py - map_y0) / (map_y1 - map_y0) * 142.0
        for px in range(map_x0, map_x1, 7):
            lon = -180.0 + (px - map_x0) / (map_x1 - map_x0) * 360.0
            if on_land(lon, lat):
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=DOT)
    for n, (lon, lat) in PINS.items():
        px = map_x0 + (lon + 180.0) / 360.0 * (map_x1 - map_x0)
        py = map_y0 + (84.0 - lat) / 142.0 * (map_y1 - map_y0)
        num_badge(d, px, py, n, r=7)
    # ALSO columns: 16..26 left, 27..36 right
    f_also = sans(9)
    for j, brief in enumerate(ALSO):
        col = 0 if j < 11 else 1
        row = j if j < 11 else j - 11
        bx = 340 + col * 340
        by = 698 + row * 21
        n = 16 + j
        d.text((bx, by), "%d" % n, font=sans_b(9), fill=RED)
        d.text((bx + 22, by), brief, font=f_also, fill=DARK)

    # ---- DATE CHECK (closed box; ALSO ends above its top border)
    d.rectangle([MX, 926, RIGHT, 981], outline=RED, width=2)
    d.text((20, 932), "DATE CHECK", font=sans_b(11), fill=RED)
    para(d, 20, 948, DATE_CHECK_TEXT, sans(10), DARK, RIGHT - 28, 13,
         max_lines=2)

    # ---- sources + footer
    d.text((MX, 988), SOURCES_LINE, font=sans(8), fill=GREY)
    d.text((MX, 1005), LEGEND_LINE, font=sans(8), fill=GREY)
    foot = "SUNDAY 22 NOVEMBER 2026 · ONE PAGE"
    d.text((RIGHT - d.textlength(foot, font=sans_b(8)), 1005), foot,
           font=sans_b(8), fill=DARK)

    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    build().save(out, format="PNG")
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
