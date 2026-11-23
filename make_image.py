"""Draw the Sunday 22 November 2026 front page: 25 stories, 7 regions.

One page, 1024x1024, built only from Pillow primitives. No photos, no
traced artwork, no network. The world map is drawn from hand-written
continent outlines in longitude/latitude, filled in warm tan with a
thin darker edge, so the land reads as a real world map at a glance.
Story pins sit on the map at the true place each numbered story
happened (two pins are nudged a few pixels for legibility, see PINS).

Run:  python3 make_image.py   (writes entry.png next to this file)
The output is deterministic: same bytes on every run.
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (253, 248, 233)      # warm newsprint cream
INK = (22, 22, 22)           # near-black text
RED = (178, 34, 34)          # headlines, pins, date-check edge
NAVY = (18, 32, 62)          # top bar, UTC bar
GOLD = (232, 184, 64)        # UTC times
GREY = (96, 96, 90)          # captions, sources
FAINT = (120, 110, 95)       # thin rules
LAND = (198, 170, 120)       # filled continents
LAND_EDGE = (122, 96, 58)    # continent outline
SKY = (24, 34, 64)           # hero 1 night sky
SEA = (140, 170, 205)        # hero 2 sea / light blue panels
SAND = (214, 164, 96)        # hero 3 desert dusk

# --- fonts ---------------------------------------------------------------
FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# --- text helpers --------------------------------------------------------
def wrap(draw, text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_w, leading, max_lines=None):
    """Draw wrapped text; return the y just below the last line."""
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centre(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


# --- map projection ------------------------------------------------------
# Map drawing area (left column of the bottom block).
MAP_X0, MAP_X1 = 12, 430
MAP_TOP = 672
# Equirectangular, longitude -168..+192 across the full width; latitude
# -58..+84. A mild vertical stretch (1.2x) fills the tall map area
# without bending the continents out of recognition.
LON0, LON1 = -168.0, 192.0
LAT_TOP, LAT_BOT = 84.0, -58.0
SX = (MAP_X1 - MAP_X0) / (LON1 - LON0)
SY = SX * 1.2
MAP_H = (LAT_TOP - LAT_BOT) * SY


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) * SX
    y = MAP_TOP + (LAT_TOP - lat) * SY
    return (x, y)


def poly(points):
    return [project(lon, lat) for lon, lat in points]


# --- continent outlines (lon, lat), hand-drawn from geography -----------
NORTH_AMERICA = [
    (-166, 68), (-160, 59), (-153, 58), (-146, 60), (-138, 59), (-131, 55),
    (-126, 49), (-124, 42), (-120, 35), (-114, 29), (-110, 24), (-106, 21),
    (-100, 17), (-95, 16), (-90, 14), (-86, 12), (-83, 9), (-80, 8),
    (-77, 8), (-74, 10), (-71, 12), (-66, 11), (-62, 10), (-58, 8),
    (-54, 6), (-51, 4), (-50, 0), (-46, -2), (-40, -4), (-35, -8),
    (-37, -13), (-39, -18), (-41, -23), (-46, -26), (-49, -30), (-53, -33),
    (-57, -36), (-60, -39), (-64, -42), (-66, -47), (-68, -51), (-69, -54),
    (-71, -53), (-73, -48), (-73, -40), (-73, -32), (-71, -24), (-70, -18),
    (-74, -14), (-78, -9), (-81, -3), (-80, 2), (-77, 6), (-81, 9),
    (-85, 12), (-88, 15), (-89, 18), (-92, 19), (-96, 19), (-97, 24),
    (-95, 29), (-90, 29), (-86, 30), (-83, 30), (-81, 26), (-80, 31),
    (-78, 34), (-75, 37), (-73, 40), (-70, 42), (-67, 44), (-63, 45),
    (-60, 46), (-58, 49), (-56, 51), (-60, 54), (-64, 59), (-68, 58),
    (-73, 60), (-78, 62), (-83, 66), (-88, 66), (-93, 68), (-98, 68),
    (-104, 68), (-110, 68), (-117, 69), (-124, 70), (-131, 70), (-138, 70),
    (-145, 70), (-152, 71), (-159, 71), (-164, 69),
]

SOUTH_AMERICA = [
    (-77, 8), (-74, 11), (-70, 12), (-65, 11), (-61, 9), (-57, 7),
    (-53, 5), (-51, 3), (-50, 0), (-45, -2), (-39, -5), (-35, -8),
    (-37, -13), (-39, -18), (-42, -23), (-47, -26), (-51, -30), (-54, -34),
    (-57, -38), (-61, -41), (-65, -44), (-67, -49), (-69, -52), (-70, -54),
    (-72, -52), (-73, -47), (-73, -40), (-73, -33), (-71, -25), (-70, -18),
    (-73, -14), (-77, -10), (-80, -5), (-81, 0), (-79, 4),
]

AFRICA = [
    (-6, 35), (-2, 35), (2, 37), (6, 37), (10, 37), (11, 34), (15, 32),
    (20, 32), (25, 32), (30, 31), (32, 31), (34, 28), (35, 24), (37, 20),
    (39, 16), (41, 12), (44, 11), (48, 11), (51, 11), (48, 6), (45, 1),
    (42, -3), (40, -8), (39, -13), (37, -18), (35, -23), (33, -27),
    (31, -29), (28, -33), (24, -34), (20, -35), (17, -33), (15, -28),
    (13, -20), (12, -14), (12, -8), (10, -2), (9, 3), (6, 4), (0, 5),
    (-5, 5), (-10, 6), (-14, 9), (-17, 12), (-17, 15), (-15, 20),
    (-14, 25), (-10, 29), (-6, 32),
]

EUROPE = [
    (-9, 37), (-9, 42), (-4, 44), (-1, 46), (-4, 48), (-2, 49), (1, 51),
    (3, 53), (6, 54), (8, 57), (10, 59), (6, 60), (5, 62), (8, 63),
    (12, 65), (16, 68), (21, 70), (26, 71), (30, 70), (34, 68), (38, 66),
    (42, 65), (40, 62), (37, 60), (34, 58), (30, 59), (27, 59), (24, 58),
    (21, 56), (19, 54), (16, 54), (13, 55), (11, 56), (9, 55), (6, 53),
    (4, 52), (1, 51), (-2, 50), (-4, 48), (-5, 46), (-2, 44), (0, 43),
    (2, 42), (5, 43), (8, 44), (11, 44), (13, 45), (16, 44), (18, 42),
    (19, 40), (16, 39), (14, 40), (12, 42), (10, 40), (8, 38), (6, 37),
    (3, 38), (0, 39), (-3, 37), (-6, 36),
]

BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 58), (0, 54), (1, 51), (-2, 50)]

ASIA = [
    (35, 68), (42, 68), (50, 68), (58, 69), (66, 69), (74, 72), (82, 73),
    (90, 75), (98, 76), (106, 77), (114, 74), (122, 72), (130, 72),
    (138, 72), (146, 72), (154, 70), (160, 68), (166, 66), (172, 66),
    (178, 65), (178, 62), (172, 60), (165, 59), (160, 56), (156, 51),
    (152, 46), (146, 44), (142, 42), (140, 39), (138, 36), (135, 34),
    (132, 33), (130, 31), (127, 34), (126, 38), (123, 39), (121, 37),
    (120, 34), (122, 30), (121, 27), (118, 24), (113, 22), (109, 18),
    (108, 13), (105, 9), (103, 7), (101, 6), (99, 9), (98, 13), (96, 16),
    (93, 18), (91, 22), (88, 22), (86, 20), (83, 18), (80, 15), (80, 10),
    (77, 8), (75, 11), (73, 16), (71, 20), (68, 22), (65, 25), (62, 25),
    (58, 25), (56, 26), (53, 27), (51, 28), (49, 30), (46, 30), (43, 29),
    (41, 27), (39, 23), (38, 19), (36, 15), (35, 12), (38, 12), (42, 12),
    (45, 12), (48, 14), (51, 15), (54, 17), (57, 19), (59, 22), (58, 24),
    (56, 26), (53, 26), (50, 26), (48, 28), (47, 30), (44, 30), (42, 31),
    (39, 32), (36, 36), (35, 34), (33, 31), (30, 36), (28, 36), (27, 37),
    (30, 37), (33, 39), (36, 42), (39, 45), (42, 48), (45, 51), (48, 54),
    (51, 57), (54, 60), (57, 62), (59, 65), (55, 68), (48, 68), (42, 68),
]

JAPAN = [
    (130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 38),
    (141, 40), (142, 42), (144, 44), (142, 43), (141, 40), (140, 37),
    (138, 35), (136, 34), (134, 33), (131, 32),
]

SUMATRA = [
    (95, 5), (97, 4), (99, 2), (101, 0), (103, -2), (105, -4), (106, -6),
    (104, -5), (102, -2), (100, 0), (97, 3),
]

BORNEO = [
    (109, 1), (111, 2), (113, 4), (116, 6), (118, 4), (119, 1), (118, -1),
    (116, -3), (113, -3), (110, -2),
]

JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8), (107, -8), (105, -7)]

NEW_GUINEA = [
    (131, -1), (134, -2), (137, -3), (140, -5), (143, -6), (146, -7),
    (147, -9), (144, -8), (141, -8), (138, -7), (135, -5), (132, -3),
]

PHILIPPINES = [(120, 18), (121, 16), (122, 14), (121, 11), (122, 10), (124, 11), (123, 14), (122, 17)]

AUSTRALIA = [
    (114, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
    (130, -32), (133, -32), (136, -35), (139, -36), (141, -38), (144, -38),
    (146, -39), (149, -37), (151, -34), (153, -30), (153, -27), (151, -24),
    (148, -20), (145, -15), (142, -11), (141, -13), (139, -17), (136, -15),
    (134, -12), (132, -12), (130, -13), (127, -14), (124, -16), (121, -19),
    (117, -21),
]

NZ_NORTH = [(173, -35), (175, -37), (177, -38), (178, -38), (176, -40), (174, -41), (173, -39), (173, -36)]
NZ_SOUTH = [(167, -45), (169, -43), (171, -42), (173, -41), (174, -42), (172, -44), (169, -46), (167, -46)]

LAND_POLYS = [
    NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EUROPE, BRITAIN, ASIA, JAPAN,
    SUMATRA, BORNEO, JAVA, NEW_GUINEA, PHILIPPINES, AUSTRALIA, NZ_NORTH,
    NZ_SOUTH,
]

# --- pins: (story number, lon, lat) --------------------------------------
# Pins 8 and 9 are drawn a few degrees north-west of their true spot so
# they do not collide with pins 1 and 3; both stay in the right sea /
# country (Baltic Sea for the Gulf of Finland, Iran for Tehran).
PINS = [
    (1, 30.5, 50.5), (2, 30.7, 36.9), (3, 50.6, 26.2), (4, 114.2, 22.3),
    (5, 174.8, -41.3), (6, -115.1, 36.2), (7, -98.5, 29.4),
    (8, 21.0, 62.0), (9, 47.0, 39.0), (10, -47.9, -15.8),
    (11, -77.0, 38.9), (12, 4.35, 50.85), (13, 93.9, 24.8),
    (14, 106.4, -6.2), (15, -75.2, -11.2),
]


# --- map -----------------------------------------------------------------
def draw_map(draw):
    """Filled continents + numbered story pins."""
    for pts in LAND_POLYS:
        pg = poly(pts)
        draw.polygon(pg, fill=LAND)
        draw.line(pg + [pg[0]], fill=LAND_EDGE, width=1)
    for num, lon, lat in PINS:
        x, y = project(lon, lat)
        r = 8
        draw.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=1)
        label = str(num)
        fnt = font(SANS_B, 9 if num < 10 else 8)
        tw = draw.textlength(label, font=fnt)
        th = draw.textbbox((0, 0), label, font=fnt)
        draw.text((x - tw / 2, y - (th[3] - th[1]) / 2 - th[1]), label, font=fnt, fill=(255, 255, 255))


# --- hero scenes ---------------------------------------------------------
def hero_drones(draw, x, y, w, h):
    """Night skyline under an orange drone glow (Kyiv region, story 1)."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    for sx, sy, sr in [(x + 52, y + 22, 17), (x + 258, y + 30, 24), (x + 150, y + 12, 3)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(232, 150, 52))
    for bx, bw, bh in [(x + 6, 26, 52), (x + 44, 38, 66), (x + 96, 22, 44),
                       (x + 132, 34, 58), (x + 182, 26, 50), (x + 224, 40, 62),
                       (x + 276, 30, 56)]:
        draw.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(10, 14, 30))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            for wx in range(bx + 6, bx + bw - 6, 12):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 200, 90))
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(8, 10, 22))


def hero_cop31(draw, x, y, w, h):
    """Globe, thermometer and a conference table (Antalya, story 2)."""
    draw.rectangle([x, y, x + w, y + h], fill=(178, 208, 232))
    gx, gy, gr = x + 52, y + 44, 30
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 190), outline=(255, 255, 255), width=2)
    draw.ellipse([gx - 16, gy - 18, gx + 2, gy - 2], fill=(110, 190, 110))
    draw.ellipse([gx + 4, gy + 6, gx + 18, gy + 20], fill=(110, 190, 110))
    tx = x + 168
    draw.rounded_rectangle([tx - 7, y + 14, tx + 7, y + 62], radius=7, fill=(255, 255, 255), outline=RED, width=2)
    draw.ellipse([tx - 11, y + 58, tx + 11, y + 80], fill=RED)
    draw.rectangle([tx - 3, y + 34, tx + 3, y + 66], fill=RED)
    cx, cy = x + 252, y + 42
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=(90, 90, 90), width=2)
    draw.line([cx, cy, cx + 9, cy - 7], fill=(90, 90, 90), width=2)
    draw.line([cx, cy, cx - 6, cy + 3], fill=(90, 90, 90), width=2)
    draw.rectangle([x, y + h - 26, x + w, y + h - 18], fill=(120, 84, 56))
    for hx in range(x + 28, x + w - 20, 44):
        draw.ellipse([hx - 9, y + h - 44, hx + 9, y + h - 26], fill=(240, 210, 180))
        draw.rectangle([hx - 12, y + h - 26, hx + 12, y + h - 18], fill=(70, 70, 78))


def hero_radar(draw, x, y, w, h):
    """Radar dishes in desert dusk, smoke on the horizon (Bahrain, story 3)."""
    draw.rectangle([x, y, x + w, y + h], fill=(206, 138, 74))
    draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(168, 104, 58))
    mx, my, mr = x + w - 42, y + 26, 16
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(240, 214, 160))
    for dx, base in [(x + 60, y + h - 30), (x + 200, y + h - 22)]:
        draw.line([dx, base, dx + 26, base - 34], fill=(245, 240, 228), width=4)
        draw.arc([dx - 4, base - 62, dx + 56, base - 6], start=200, end=340, fill=(245, 240, 228), width=4)
        draw.line([dx + 26, base - 34, dx + 26, base], fill=(245, 240, 228), width=3)
    for sx, sy, sr in [(x + 120, y + h - 46, 14), (x + 150, y + h - 40, 10), (x + 96, y + h - 40, 9)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 138, 128))


# --- small icons ---------------------------------------------------------
def icon_ballot(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    draw.rectangle([x + 18, y + 26, x + w - 18, y + h - 8], fill=(255, 255, 255), outline=(60, 90, 150), width=2)
    draw.line([x + 34, y + 44, x + 52, y + 58], fill=(30, 140, 70), width=5)
    draw.line([x + 52, y + 58, x + 88, y + 22], fill=(30, 140, 70), width=5)


def icon_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 140, 80))
    draw.rectangle([x + 30, y + 14, x + 44, y + h - 12], fill=(222, 184, 120), outline=(120, 90, 40), width=1)
    draw.ellipse([x + 92, y + 22, x + 104, y + 34], fill=(200, 40, 40), outline=(255, 255, 255), width=1)
    for i in range(3):
        draw.line([x + 60 + i * 14, y + 52, x + 66 + i * 14, y + 52], fill=(240, 230, 200), width=3)


def icon_race(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 44, 52))
    draw.rectangle([x + 22, y + 34, x + w - 22, y + 50], fill=(200, 30, 30))
    draw.polygon([(x + 62, y + 34), (x + 78, y + 22), (x + 104, y + 22), (x + 112, y + 34)], fill=(200, 30, 30))
    for wx in (x + 38, x + 122):
        draw.ellipse([wx - 11, y + 48, wx + 11, y + 66], fill=(15, 15, 15), outline=(200, 200, 200), width=2)


def icon_basket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(224, 122, 42))
    cx, cy, r = x + w // 2, y + h // 2 + 2, 26
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 110, 40), outline=(120, 60, 20), width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=(120, 60, 20), width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=(120, 60, 20), width=2)
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=300, end=60, fill=(120, 60, 20), width=2)


def icon_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(150, 190, 220))
    draw.polygon([(x + 24, y + 48), (x + w - 24, y + 48), (x + w - 40, y + 56), (x + 40, y + 56)], fill=(150, 40, 40))
    draw.rectangle([x + 66, y + 30, x + 92, y + 48], fill=(220, 220, 210))
    for fx, fy in [(x + 118, y + 18), (x + 128, y + 12)]:
        draw.ellipse([fx - 8, fy - 6, fx + 8, fy + 6], fill=(200, 90, 30))
    draw.rectangle([x, y + 56, x + w, y + h], fill=(70, 120, 170))


def icon_bolt(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(250, 230, 120))
    draw.polygon([(x + 92, y + 8), (x + 58, y + 40), (x + 80, y + 40), (x + 62, y + 64), (x + 100, y + 30), (x + 78, y + 30)], fill=(20, 20, 20))


def icon_care(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 240, 238))
    draw.rectangle([x + 58, y + 16, x + 102, y + 56], fill=(255, 255, 255), outline=RED, width=3)
    draw.rectangle([x + 76, y + 24, x + 84, y + 48], fill=RED)
    draw.rectangle([x + 66, y + 34, x + 94, y + 42], fill=RED)
    draw.rectangle([x, y + h - 10, x + w, y + h], fill=RED)


def icon_search(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 235, 230))
    draw.ellipse([x + 42, y + 14, x + 92, y + 64], outline=(30, 30, 30), width=5)
    draw.line([x + 84, y + 56, x + 112, y + 78], fill=(30, 30, 30), width=6)
    draw.text((x + 52, y + 30), "XX", font=font(SANS_B, 16), fill=(30, 30, 30))


def icon_plane(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(170, 205, 235))
    draw.polygon([(x + 20, y + 44), (x + 120, y + 30), (x + 140, y + 36), (x + 120, y + 44)], fill=(255, 255, 255))
    draw.polygon([(x + 70, y + 30), (x + 84, y + 16), (x + 96, y + 30)], fill=(255, 255, 255))
    draw.polygon([(x + 70, y + 46), (x + 84, y + 60), (x + 96, y + 44)], fill=(255, 255, 255))


def icon_warn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 40, 44))
    draw.polygon([(x + 80, y + 12), (x + 138, y + 62), (x + 22, y + 62)], fill=(240, 190, 30))
    draw.rectangle([x + 76, y + 30, x + 84, y + 48], fill=(20, 20, 20))
    draw.ellipse([x + 76, y + 52, x + 84, y + 60], fill=(20, 20, 20))


def icon_factory(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(210, 200, 180))
    draw.rectangle([x + 18, y + 26, x + 34, y + 62], fill=(90, 80, 70))
    draw.polygon([(x + 40, y + 62), (x + 40, y + 38), (x + 66, y + 38), (x + 80, y + 50), (x + 94, y + 50), (x + 108, y + 38), (x + 138, y + 38), (x + 138, y + 62)], fill=(70, 66, 62))
    for sx, sy, sr in [(x + 118, y + 18, 9), (x + 130, y + 12, 7)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 115, 108))


def icon_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 224, 200))
    pts = [(x + 10, y + 40), (x + 30, y + 40), (x + 42, y + 22), (x + 54, y + 56),
           (x + 66, y + 30), (x + 78, y + 48), (x + 90, y + 40), (x + 110, y + 40),
           (x + 122, y + 26), (x + 134, y + 52), (x + 150, y + 40)]
    draw.line(pts, fill=RED, width=3)


# --- story data (25 stories, facts verified 22 Nov) ------------------------
HEROES = [
    dict(
        banner="186 DRONES IN ONE NIGHT", art=hero_drones,
        kicker="1  KYIV REGION, UKRAINE · WAR", tag="REPORTED",
        head="Russia's 186-drone night wrecks a Kyiv-region block",
        sub="161 of 186 drones downed, 72 jet-powered. A block in Dymer falls: 3 killed, 14 missing. (Ukrainian Air Force)",
    ),
    dict(
        banner="COP31: NO DEAL", art=hero_cop31,
        kicker="2  ANTALYA, TÜRKIYE · CLIMATE", tag="REPORTED",
        head="COP31 closes with no deal as fossil fuels stay out",
        sub="'Recalls' Dubai, keeps 35%, drops $120bn, admits 1.5°C will be overshot. The EU refuses it. (Reuters, BBC)",
    ),
    dict(
        banner="CLAIM VS DENIAL", art=hero_radar,
        kicker="3  MANAMA, BAHRAIN · IRAN", tag="CLAIM",
        head="Iran says it hit two US radars; Bahrain says no",
        sub="IRGC says it hit two Patriot radars. Bahrain: a civilian site burned, two injured. (Khaleej Times, Al Jazeera)",
    ),
]

SMALLS = [
    dict(n=4, banner="856 CANDIDATES", art=icon_ballot, kicker="HONG KONG · ELECTION",
         head="Hong Kong picks its Election Committee",
         sub="856 candidates, 723 seats; polls 09:00–18:00.", src="SCMP"),
    dict(n=5, banner="720/9 DECLARED", art=icon_cricket, kicker="WELLINGTON · CRICKET",
         head="India post 720/9, a record in New Zealand",
         sub="Rahul 136, Pant 128; hosts 119/2, trailing by 233.", src="ESPN"),
    dict(n=6, banner="VERSTAPPEN WINS", art=icon_race, kicker="LAS VEGAS · FORMULA 1",
         head="Verstappen wins the Las Vegas Grand Prix",
         sub="35 lead changes; Norris +0.639, Piastri +1.529.", src="FIA"),
    dict(n=7, banner="50 POINTS", art=icon_basket, kicker="SAN ANTONIO · NBA",
         head="Wembanyama drops 50, Spurs keep rolling",
         sub="50 pts, 19 rebounds, 5 blocks; Spurs win 114–91.", src="Reuters"),
    dict(n=8, banner="SHIP ABLAZE", art=icon_ship, kicker="GULF OF FINLAND · SEA",
         head="Russian cargo ship Sparta II still ablaze",
         sub="Hit by drones Saturday; Finland leads rescue.", src="Reuters"),
    dict(n=9, banner="POWER CUTS", art=icon_bolt, kicker="TEHRAN, IRAN · ENERGY",
         head="Iran starts rationing electricity",
         sub="Cuts up to two hours a day as war damage bites.", src="Wires"),
    dict(n=10, banner="IN INTENSIVE CARE", art=icon_care, kicker="BRASÍLIA, BRAZIL · HEALTH",
         head="Bolsonaro in intensive care in Brasilia",
         sub="Acute bowel obstruction; stable; surgery possible.", src="Reuters"),
    dict(n=11, banner="FBI PROBE", art=icon_search, kicker="WASHINGTON · CYBER",
         head="FBI probes hack of its crime database",
         sub="State pauses gun-dealer checks; breach assessed.", src="AP"),
    dict(n=12, banner="FLIGHTS GROUNDED", art=icon_plane, kicker="BRUSSELS · TRAVEL",
         head="Belgian controllers join Monday strike",
         sub="Flights grounded 07:00–21:00; controllers walk out.", src="Wires"),
    dict(n=13, banner="TOLL AT 19", art=icon_warn, kicker="MANIPUR, INDIA · POISONING",
         head="Toxic-liquor death toll in Manipur reaches 19",
         sub="600 in hospital, six held; toll up from 16.", src="Xinhua"),
    dict(n=14, banner="3 DEAD, 36 MISSING", art=icon_factory, kicker="CIKANDE, INDONESIA · FIRE",
         head="Cikande factory fire: 3 dead, 36 missing",
         sub="Blaze tore through the Banten plant; search on.", src="Detiknews"),
    dict(n=15, banner="1 DEAD, 16 HURT", art=icon_quake, kicker="JUNÍN, PERU · QUAKE TOLL",
         head="Peru quake toll: 1 dead, 16 hurt",
         sub="170 homes damaged in Junín; the count is completed.", src="Reuters"),
]

ALSO = [
    (16, "Europe: Estonia to close Russia crossings 1 Dec (Reuters)"),
    (17, "Asia-Pacific: Chinese bomber turns back (AP)"),
    (18, "Asia-Pacific: Philippines M5.9 quake off Palawan (EMSC)"),
    (19, "Asia-Pacific: Taiwan live-fire drill on Kinmen (CNA)"),
    (20, "Africa: Sudan: RSF accused of killing civilians (Claim)"),
    (21, "Oceania: Marles rejects US report on AUKUS (ABC)"),
    (22, "Americas: Trump seeks 'permanent' Iran deal (Al Jazeera)"),
    (23, "Middle East: Hamas seeks urgent mediator talks (Al Jazeera)"),
    (24, "World: Bitcoin back above $60,000 (Market data)"),
    (25, "Europe · FORECAST: ATP final: Zverev v Alcaraz (Forecast)"),
]

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed by air"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total in NZ"),
    ("50", "points, 19 rebounds"),
]

REGIONS = [
    ("EUROPE 6", 170, (30, 60, 110)),
    ("MIDDLE EAST 3", 150, (0, 128, 128)),
    ("AMERICAS 6", 160, (198, 82, 40)),
    ("ASIA-PACIFIC 7", 190, (42, 128, 72)),
    ("AFRICA 1", 110, (140, 100, 60)),
    ("OCEANIA 1", 110, (110, 80, 160)),
    ("WORLD 1", 110, (70, 70, 70)),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"), ("03:00", "COP31 objections"),
    ("05:11", "Hamas talks"), ("05:30", "Verstappen wins"),
    ("06:00", "COP31 approval"), ("07:30", "Approval slips"),
]

DATE_CHECK = (
    "Wires read to 20:15 UTC, Sun 22 Nov 2026. Each story here was reported, "
    "or still developing, on 22 Nov somewhere in the world. Left out: the "
    "400-drone barrage (19–20 Nov); Kryvyi Rih (20 Nov); 'El Chapo Isidro' "
    "(Fri); Bayelsa boat, 24 dead (Fri); Gaza aid-van strike (Sat); Poland "
    "missiles (19 Nov); Kerch Bridge (earlier); Shenzhen summit (19 Nov)."
)


# --- page ----------------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((12, 4), "THE WORLD IN ONE DAY", font=font(SANS_B, 11), fill=(255, 255, 255))
    right = "25 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - 12 - d.textlength(right, font=font(SANS_B, 11)), 4), right,
           font=font(SANS_B, 11), fill=(255, 255, 255))

    # masthead + subline
    d.text((12, 26), "Sunday 22 November 2026", font=font(SERIF_B, 58), fill=INK)
    centre(d, W // 2, 92,
           "A night of 186 drones over Ukraine · COP31 closes without a deal · "
           "Iran's radar claim answered by Bahrain's denial",
           font(SANS, 14), RED)

    # stat strip
    sx = 12
    for i, (num, cap) in enumerate(STATS):
        col_w = 166 if i < 5 else 170
        d.text((sx, 108), num, font=font(SERIF_B, 26), fill=RED)
        d.text((sx, 138), cap, font=font(SANS, 9), fill=GREY)
        if i < 5:
            d.line([sx + col_w - 8, 110, sx + col_w - 8, 146], fill=FAINT, width=1)
        sx += col_w

    # region bar
    rx = 12
    for label, rw, col in REGIONS:
        d.rectangle([rx, 148, rx + rw, 162], fill=col)
        centre(d, rx + rw // 2, 150, label, font(SANS_B, 10), (255, 255, 255))
        rx += rw

    # UTC bar
    d.rectangle([12, 166, 1012, 184], fill=NAVY)
    d.text((20, 169), "THE DAY IN UTC", font=font(SANS_B, 11), fill=(255, 255, 255))
    ux = 150
    for t, label in UTC_EVENTS:
        d.text((ux, 169), t, font=font(SANS_B, 11), fill=GOLD)
        ux += d.textlength(t, font=font(SANS_B, 11)) + 6
        d.text((ux, 169), label, font=font(SANS, 11), fill=(255, 255, 255))
        ux += d.textlength(label, font=font(SANS, 11)) + 20

    # heroes
    hx0 = [12, 342, 672]
    for i, hero in enumerate(HEROES):
        x = hx0[i]
        w = 320
        hero["art"](d, x, 190, w, 88)
        d.rectangle([x, 190, x + 200, 208], fill=RED)
        d.text((x + 6, 192), hero["banner"], font=font(SANS_B, 11), fill=(255, 255, 255))
        d.text((x, 282), hero["kicker"], font=font(SANS_B, 10), fill=INK)
        tag = hero["tag"]
        d.text((x + w - d.textlength(tag, font=font(SANS_B, 10)), 282), tag,
               font=font(SANS_B, 10), fill=RED if tag == "CLAIM" else GREY)
        text_block(d, x, 296, hero["head"], font(SERIF_B, 20), INK, w, 21, max_lines=2)
        text_block(d, x, 340, hero["sub"], font(SANS, 10), INK, w, 12, max_lines=2)

    # small leads, two rows of six
    for row in range(2):
        y0 = 368 if row == 0 else 502
        for col in range(6):
            s = SMALLS[row * 6 + col]
            x = 12 + col * 168
            w = 160
            s["art"](d, x, y0, w, 60)
            d.rectangle([x, y0, x + 150, y0 + 16], fill=RED)
            d.text((x + 5, y0 + 1), s["banner"], font=font(SANS_B, 9), fill=(255, 255, 255))
            bx, by, br = x + w - 9, y0 + 9, 9
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED, outline=(255, 255, 255), width=1)
            lab = str(s["n"])
            fnt = font(SANS_B, 9 if s["n"] < 10 else 8)
            tw = d.textlength(lab, font=fnt)
            d.text((bx - tw / 2, by - 6), lab, font=fnt, fill=(255, 255, 255))
            d.text((x, y0 + 64), s["kicker"], font=font(SANS_B, 9), fill=INK)
            src = s["src"]
            sf = font(SANS_B, 8)
            tw = d.textlength(src, font=sf)
            d.rectangle([x + 3, y0 + 48, x + 3 + tw + 8, y0 + 58], fill=(20, 20, 20))
            d.text((x + 7, y0 + 49), src, font=sf, fill=(255, 255, 255))
            text_block(d, x, y0 + 78, s["head"], font(SERIF_B, 12), INK, w, 13, max_lines=2)
            text_block(d, x, y0 + 106, s["sub"], font(SANS, 10), INK, w, 11, max_lines=2)

    # divider
    d.line([12, 634, 1012, 634], fill=INK, width=1)

    # bottom titles
    d.text((12, 640), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=INK)
    d.text((12, 654), "pins match story numbers", font=font(SANS, 9), fill=GREY)
    d.text((445, 640), "ALSO ON SUNDAY 22 NOVEMBER — 10 MORE STORIES",
           font=font(SANS_B, 12), fill=INK)

    # map (filled continents + pins) + caption
    draw_map(d)
    centre(d, (MAP_X0 + MAP_X1) // 2, 884,
           "Fifteen stories, pinned where they happened.",
           font(SERIF, 11), GREY)

    # ALSO column
    ay = 668
    for num, brief in ALSO:
        d.text((445, ay), str(num), font=font(SANS_B, 11), fill=RED)
        d.text((470, ay), brief, font=font(SANS, 11), fill=INK)
        ay += 23

    # DATE CHECK box
    d.rectangle([12, 926, 1012, 981], outline=RED, width=2)
    d.text((20, 931), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    text_block(d, 20, 947, DATE_CHECK, font(SANS, 10), INK, 984, 13, max_lines=2)

    # sources, legend, footer
    d.text((12, 986),
           "Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, CNA, ABC, TOI, Guardian, "
           "Kyiv Ind., ISNA, ESPN, FIA, SCMP, Detiknews, Xinhua, EMSC. Pictures: original, drawn in code.",
           font=font(SANS, 8), fill=GREY)
    d.text((12, 996),
           "CERTAINTY: REPORTED = carried by the day's wires · CLAIM = one side's account, labelled as such · "
           "FORECAST = still to happen when drawn",
           font=font(SANS, 8), fill=GREY)
    foot = "SUNDAY 22 NOVEMBER 2026 · ONE PAGE"
    d.text((W - 12 - d.textlength(foot, font=font(SANS_B, 9)), 1006), foot,
           font=font(SANS_B, 9), fill=INK)

    img.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}")
    sys.exit(0)
