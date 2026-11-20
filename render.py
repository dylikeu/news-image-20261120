#!/usr/bin/env python3
"""Render 'The World in One Day - Friday 20 November 2026'.

One-page newspaper front page: 42 stories, 7 regions, big date masthead,
stylised world map with 12 numbered locations, DATE CHECK box, markets strip.
Draws with Pillow only; output is a 1024x1024 PNG under 1 MiB.
Run:  python3 render.py [output.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)      # newsprint cream
INK = (26, 26, 26)           # near-black ink
RED = (176, 42, 32)          # headline red
BLUE = (31, 78, 121)         # deep blue
GREY = (110, 105, 95)        # muted grey
LIGHT = (233, 226, 212)      # light panel
RULE = (26, 26, 26)
MAP_LAND = (196, 205, 190)   # pale sage land
MAP_SEA = (226, 232, 228)    # pale sea

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap, returns list of lines that fit max_w."""
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centre(draw, x0, x1, y, s, f, fill=INK):
    w = text_w(draw, s, f)
    draw.text(((x0 + x1 - w) / 2, y), s, font=f, fill=fill)


# ---------------------------------------------------------------- stories
# (number, region, headline) -- every story happened, or was first reported,
# on Friday 20 November 2026. Regions: NA, LATAM, EUR, ME, AFR, APAC, WORLD.
STORIES = [
    (1, "NA", "White House fires cyber chief"),
    (2, "NA", "Senate passes energy bill, 62-33"),
    (3, "NA", "Trump pardons baseball star Pete Rose"),
    (4, "NA", "Texas executes Dennes; Florida sets record"),
    (5, "NA", "US sanctions Comancheros and 'Ndrangheta"),
    (6, "NA", "US loses measles-free status; FDA pick out"),
    (7, "NA", "California subpoenas Nvidia"),
    (8, "LATAM", "Bukele registers for third term"),
    (9, "LATAM", "Haiti forces kill 34 gang suspects in raid"),
    (10, "LATAM", "Brazil bank sells $1bn to slow dollar slide"),
    (11, "LATAM", "Brazil recognises Raoni ancestral lands"),
    (12, "LATAM", "Colombia marches against tax reform plans"),
    (13, "LATAM", "Hegseth signs US-Venezuela military deal"),
    (14, "EUR", "Berlin: Europe ready for Russia talks"),
    (15, "EUR", "Ukraine hits Crimea Bridge a third time"),
    (16, "EUR", "UK-EU set to agree youth mobility scheme"),
    (17, "EUR", "Italy strikes nationwide over living costs"),
    (18, "EUR", "Youth strike in 25+ nations over costs"),
    (19, "EUR", "COP31 draft drops fossil-fuel phase-out"),
    (20, "EUR", "Denmark ratifies Greenland security deal"),
    (21, "EUR", "Sánchez admits mistakes in TV debate"),
    (22, "ME", "Houthi missile hits Riyadh finance tower"),
    (23, "ME", "Hormuz tanker attacks intensify; mine blast"),
    (24, "ME", "Israeli troops cross Gaza's Yellow Line"),
    (25, "ME", "Iraq orders Iran-backed militia to leave"),
    (26, "ME", "Mosque torched in northern Israel"),
    (27, "AFR", "Sudan drone strike kills 10 at gold mine"),
    (28, "AFR", "Senegal boat sinks; 4 dead, dozens missing"),
    (29, "AFR", "Strikes reported on Ethiopia-Eritrea border"),
    (30, "AFR", "Somalia expels UAE ambassador"),
    (31, "AFR", "Zimbabwe destroys 250,000 landmines"),
    (32, "AFR", "Malawi fuel crisis turns violent"),
    (33, "APAC", "Japan inflation up; BoJ rate hike on track"),
    (34, "APAC", "IAEA: North Korea expanding enrichment"),
    (35, "APAC", "Seoul court orders retrial of ex-PM Han"),
    (36, "APAC", "Takaichi gets cool APEC welcome in China"),
    (37, "APAC", "Philippines, Chile sign free-trade deal"),
    (38, "APAC", "Pakistan kills 22 militants in NW raids"),
    (39, "APAC", "Bangladesh unrest before Hasina return"),
    (40, "APAC", "Mongolia's president resigns"),
    (41, "WORLD", "IMF: global debt near 100% of GDP"),
    (42, "WORLD", "GTA 6 sales top $2.3bn, a record launch"),
]

LEADS = [
    ("MARKETS", "AI sell-off sweeps Asia",
     "Nikkei -4.8%, Taiwan -6.4%, Korea -5.2%; SoftBank -16% as AI doubts "
     "spread. Worst week since 2020."),
    ("CLIMATE", "COP31 draft drops fossil-fuel phase-out",
     "Antalya text drops net-zero dates as talks enter final day; Pacific "
     "states demand a phase-out."),
    ("UKRAINE", "Berlin: Europe ready for talks with Russia",
     "Allies agree united position; US envoy floats NATO-style guarantee; "
     "Merz criticises Shenzhen format."),
]

# (number, title, deck) -- illustrated panels, numbers match STORIES.
PANELS = [
    (7, "NVIDIA PROBE", "California subpoenas Nvidia",
     "AG probes whether AI chips reached China"),
    (42, "GTA 6", "$2.3bn in first days",
     "Biggest entertainment launch ever"),
    (8, "BUKELE", "Third term bid",
     "Registers with electoral court"),
    (16, "UK-EU", "Youth mobility deal",
     "Summit set to approve scheme"),
    (24, "GAZA", "Troops cross Yellow Line",
     "First incursion since truce"),
    (33, "JAPAN", "Inflation highest this year",
     "BoJ December hike on track"),
    (27, "SUDAN", "Drone kills 10 at mine",
     "RSF strikes called war crimes"),
    (41, "IMF DEBT", "Debt near 100% of GDP",
     "Highest since WWII, IMF warns"),
]

# (lon, lat, number) -- places marked on the map.
DOTS = [
    (139.7, 35.7, 1),    # Tokyo - markets
    (114.1, 22.5, 2),    # Shenzhen - APEC
    (13.4, 52.5, 3),     # Berlin - Ukraine talks
    (32.0, 51.0, 4),     # Kyiv - Crimea Bridge (nudged east so dots don't collide)
    (47.0, 24.0, 5),     # Riyadh - Houthi strike
    (34.5, 31.5, 6),     # Gaza - Yellow Line (true spot; drawn displaced, see LEADERS)
    (36.8, -1.3, 7),     # Nairobi - Kenya minerals deal
    (29.5, 12.5, 8),     # S. Kordofan - Sudan strike
    (-47.9, -15.8, 9),   # Brasilia - real slide
    (-89.2, 13.7, 10),   # San Salvador - Bukele
    (-77.0, 38.9, 11),   # Washington - cyber chief fired
    (31.0, 35.0, 12),    # Antalya - COP31 (nudged so it clears Kyiv/Gaza)
]

# Display displacement for dots too close to a neighbour: number -> (lon, lat)
# to draw at, with a thin leader line back to the true spot.
LEADERS = {6: (36.5, 26.5)}

# Rough continent outlines, (lon, lat). Stylised, not to scale.
NORTH_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
                 (-135, 57), (-130, 54), (-125, 49), (-124, 42), (-120, 34),
                 (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17),
                 (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-79, 9),
                 (-82, 13), (-85, 16), (-88, 18), (-90, 21), (-91, 19),
                 (-96, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
                 (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
                 (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55),
                 (-64, 58), (-68, 55), (-72, 58), (-78, 62), (-85, 66),
                 (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
                 (-155, 71), (-162, 70), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68),
             (-25, 70), (-20, 74), (-25, 76), (-35, 77), (-50, 76),
             (-58, 74), (-60, 70), (-58, 64)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
                 (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
                 (-74, -50), (-70, -54), (-66, -55), (-68, -50), (-65, -45),
                 (-62, -41), (-57, -38), (-52, -33), (-48, -28), (-41, -23),
                 (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
                 (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
                 (-72, 12), (-75, 10), (-79, 9)]
AFRICA = [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
          (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
          (32, 31), (34, 28), (35, 23), (37, 18), (39, 15), (41, 11),
          (43, 11), (46, 11), (51, 12), (51, 10), (48, 5), (45, 2),
          (41, -2), (40, -6), (39, -12), (36, -18), (33, -26), (30, -32),
          (26, -34), (20, -35), (17, -32), (15, -27), (13, -18), (12, -12),
          (13, -6), (9, -1), (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8),
          (-17, 12), (-17, 15)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
          (-2, 50), (0, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 58),
          (12, 56), (18, 56), (21, 55), (24, 58), (21, 59), (24, 60),
          (18, 60), (12, 60), (5, 60), (5, 62), (10, 64), (14, 67),
          (18, 69), (25, 71), (30, 70), (32, 68), (35, 66), (40, 64),
          (44, 62), (48, 60), (50, 58), (48, 55), (44, 52), (40, 50),
          (38, 47), (35, 45), (30, 46), (28, 44), (24, 42), (23, 40),
          (22, 37), (26, 36), (28, 38), (30, 41), (33, 42), (36, 42),
          (39, 41), (41, 41), (38, 39), (36, 36), (33, 36), (30, 36),
          (27, 37), (23, 36), (20, 39), (19, 42), (16, 44), (14, 45),
          (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36),
          (-9, 37), (-10, 36)]
ASIA = [(30, 36), (36, 36), (42, 35), (44, 38), (48, 38), (50, 40),
        (54, 38), (56, 40), (60, 42), (63, 44), (66, 45), (70, 44),
        (74, 43), (78, 44), (82, 46), (86, 48), (90, 50), (94, 52),
        (98, 52), (102, 52), (106, 53), (110, 54), (114, 54), (118, 55),
        (122, 56), (126, 58), (130, 59), (134, 59), (138, 60), (142, 59),
        (146, 59), (150, 60), (155, 60), (158, 59), (162, 60), (162, 56),
        (158, 52), (156, 50), (152, 48), (148, 44), (144, 42), (142, 40),
        (140, 38), (138, 35), (135, 33), (132, 31), (130, 30), (127, 28),
        (124, 26), (122, 24), (120, 22), (118, 20), (116, 18), (114, 16),
        (112, 14), (110, 12), (108, 10), (106, 8), (104, 6), (102, 4),
        (100, 2), (98, 6), (96, 10), (94, 14), (92, 16), (90, 20),
        (88, 22), (86, 20), (84, 18), (82, 16), (80, 14), (78, 10),
        (76, 8), (74, 12), (72, 16), (70, 20), (68, 22), (66, 24),
        (64, 25), (62, 25), (60, 25), (58, 25), (56, 26), (54, 26),
        (52, 28), (50, 29), (48, 30), (46, 30), (44, 31), (42, 33),
        (40, 36), (38, 36), (36, 36)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 39), (142, 42), (144, 44), (142, 44), (140, 42), (139, 38),
         (137, 35), (135, 33), (132, 32), (130, 31)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (1, 51), (-3, 50), (-5, 50)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33),
             (129, -32), (132, -32), (135, -35), (137, -38), (140, -38),
             (142, -39), (145, -38), (147, -39), (150, -37), (153, -32),
             (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
             (140, -17), (136, -15), (135, -12), (132, -11), (130, -13),
             (127, -14), (124, -15), (122, -17), (120, -20), (116, -21),
             (114, -22)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
               (174, -41), (171, -43), (168, -46), (167, -45)]
INDONESIA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (110, -7),
             (114, -8), (114, -10), (110, -8), (106, -6), (102, -4),
             (99, 0), (96, 3), (95, 5)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              ASIA, JAPAN, BRITAIN, AUSTRALIA, NEW_ZEALAND, INDONESIA]


# ---------------------------------------------------------------- drawing
def hline(draw, x0, x1, y, fill=RULE, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, fill=RULE, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def kicker(draw, x, y, s, f, fill=RED):
    draw.text((x, y), s, font=f, fill=fill)


def headline_block(draw, x, y, w, kicker_s, head, deck, head_size=25,
                   deck_size=12):
    """Kicker + headline (wrapped, up to 3 lines) + deck (up to 3 lines)."""
    kf = font(SANS_B, 11)
    hf = font(SERIF_B, head_size)
    df = font(SANS, deck_size)
    kicker(draw, x, y, kicker_s, kf)
    y += 16
    lines = wrap(draw, head, hf, w)
    for ln in lines[:3]:
        draw.text((x, y), ln, font=hf, fill=INK)
        y += head_size + 2
    y += 2
    for ln in wrap(draw, deck, df, w)[:3]:
        draw.text((x, y), ln, font=df, fill=(60, 58, 52))
        y += deck_size + 4
    return y


def draw_masthead(draw):
    x0, x1 = 24, 1000
    draw.text((x0, 12), "THE WORLD IN ONE DAY", font=font(SERIF_B, 30),
              fill=INK)
    right = "No. 325  •  PRICE: FREE"
    draw.text((x1 - text_w(draw, right, font(SANS_B, 11)), 22), right,
              font=font(SANS_B, 11), fill=GREY)
    centre(draw, x0, x1, 48, "Friday, 20 November 2026",
           font(SERIF_B, 46), fill=RED)
    centre(draw, x0, x1, 102,
           "42 STORIES  •  7 REGIONS  •  ONE FRONT PAGE",
           font(SANS_B, 14))
    hline(draw, x0, x1, 128, width=3)
    hline(draw, x0, x1, 132, width=1)


def draw_leads(draw):
    y0, y1 = 142, 282
    cols = [(24, 328), (360, 664), (696, 1000)]
    for (x0, x1), (kick, head, deck) in zip(cols, LEADS):
        headline_block(draw, x0, y0, x1 - x0, kick, head, deck,
                       head_size=25, deck_size=12)
    vline(draw, 344, y0 + 4, y1 - 4, fill=GREY)
    vline(draw, 680, y0 + 4, y1 - 4, fill=GREY)
    hline(draw, 24, 1000, 290, width=2)


def project(lon, lat, mx0, my0, sx, sy, lat_top=80.0):
    return (mx0 + (lon + 180.0) * sx, my0 + (lat_top - lat) * sy)


def draw_map(draw):
    mx0, my0, mw, mh = 24, 300, 668, 176
    mx1, my1 = mx0 + mw, my0 + mh
    draw.rectangle([mx0, my0, mx1, my1], fill=MAP_SEA, outline=RULE, width=1)
    sx = mw / 360.0
    sy = mh / 140.0  # lat 80 .. -60
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, sx, sy) for lon, lat in poly]
        draw.polygon(pts, fill=MAP_LAND, outline=(120, 128, 118))
    # graticule
    for lon in range(-150, 181, 30):
        x = mx0 + (lon + 180.0) * sx
        draw.line([(x, my0), (x, my1)], fill=(210, 217, 212), width=1)
    # numbered dots
    df = font(SANS_B, 10)
    for lon, lat, n in DOTS:
        if n in LEADERS:
            dlon, dlat = LEADERS[n]
            tx, ty = project(lon, lat, mx0, my0, sx, sy)
            cx, cy = project(dlon, dlat, mx0, my0, sx, sy)
            draw.line([(tx, ty), (cx, cy)], fill=RED, width=1)
            draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED)
        else:
            cx, cy = project(lon, lat, mx0, my0, sx, sy)
        r = 8
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        s = str(n)
        draw.text((cx - text_w(draw, s, df) / 2, cy - 7), s, font=df,
                  fill=(255, 255, 255))
    draw.text((mx0 + 6, my1 - 16), "STYLISED WORLD MAP — 12 PLACES IN THE NEWS",
              font=font(SANS_B, 9), fill=GREY)
    # legend column at right of the map
    lx = 712
    draw.text((lx, 300), "ON THE MAP", font=font(SANS_B, 12), fill=RED)
    legend = [
        ("1", "Tokyo — markets crash"),
        ("2", "Shenzhen — APEC summit"),
        ("3", "Berlin — Ukraine talks"),
        ("4", "Kyiv — Crimea Bridge hit"),
        ("5", "Riyadh — missile strike"),
        ("6", "Gaza — Yellow Line crossed"),
        ("7", "Nairobi — minerals deal"),
        ("8", "S. Kordofan — drone strike"),
        ("9", "Brasilia — real slides"),
        ("10", "San Salvador — Bukele"),
        ("11", "Washington — cyber chief out"),
        ("12", "Antalya — COP31 talks"),
    ]
    lf = font(SANS, 11)
    y = 320
    for n, label in legend:
        draw.text((lx, y), n + ".", font=font(SANS_B, 11), fill=RED)
        draw.text((lx + 26, y), label, font=lf, fill=INK)
        y += 14
    hline(draw, 24, 1000, 486, width=2)


# ---------------------------------------------------------------- panels
def icon(draw, kind, x, y, s=44):
    """Tiny pictogram in a s x s box at (x, y)."""
    if kind == "chip":
        draw.rectangle([x + 8, y + 8, x + s - 8, y + s - 8], outline=BLUE,
                       width=3)
        draw.rectangle([x + 16, y + 16, x + s - 16, y + s - 16], fill=BLUE)
        for px in (x + 14, x + s // 2, x + s - 14):
            draw.line([(px, y + 2), (px, y + 8)], fill=BLUE, width=2)
            draw.line([(px, y + s - 8), (px, y + s - 2)], fill=BLUE, width=2)
        for py in (y + 14, y + s // 2, y + s - 14):
            draw.line([(x + 2, py), (x + 8, py)], fill=BLUE, width=2)
            draw.line([(x + s - 8, py), (x + s - 2, py)], fill=BLUE, width=2)
    elif kind == "dollar":
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=RED,
                     width=3)
        f = font(SERIF_B, 26)
        draw.text((x + s // 2 - text_w(draw, "$", f) / 2, y + 8), "$",
                  font=f, fill=RED)
    elif kind == "ballot":
        draw.rectangle([x + 6, y + 16, x + s - 6, y + s - 6], outline=INK,
                       width=2)
        draw.line([(x + 12, y + 16), (x + s - 12, y + 16)], fill=INK, width=3)
        draw.line([(x + 10, y + 4), (x + 16, y + 14)], fill=RED, width=2)
        draw.line([(x + 16, y + 14), (x + s - 8, y + 2)], fill=RED, width=2)
        draw.line([(x + 12, y + 26), (x + s - 12, y + 26)], fill=GREY, width=1)
        draw.line([(x + 12, y + 32), (x + s - 12, y + 32)], fill=GREY, width=1)
    elif kind == "flags":
        draw.rectangle([x + 4, y + 10, x + s // 2 + 2, y + s - 10],
                       fill=BLUE)
        draw.line([(x + 4, y + s // 2), (x + s // 2 + 2, y + s // 2)],
                  fill=(255, 255, 255), width=3)
        draw.line([(x + s // 4, y + 10), (x + s // 4, y + s - 10)],
                  fill=(255, 255, 255), width=3)
        draw.rectangle([x + s // 2 - 2, y + 10, x + s - 4, y + s - 10],
                       fill=(0, 40, 90))
        for ang in range(0, 360, 30):
            import math
            cx = x + s // 2 + (s // 4 - 2) + 8 * math.cos(math.radians(ang))
            cy = y + s // 2 + 8 * math.sin(math.radians(ang))
            draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1],
                         fill=(255, 210, 0))
    elif kind == "dashed":
        for i in range(5):
            x0 = x + 4 + i * 8
            draw.line([(x0, y + s // 2), (x0 + 5, y + s // 2)], fill=(200, 160, 0),
                      width=4)
        draw.polygon([(x + s - 10, y + 8), (x + s - 10, y + s - 8),
                      (x + 4, y + s // 2)], fill=RED)
    elif kind == "yen":
        f = font(SERIF_B, 26)
        draw.text((x + 4, y + 10), "¥", font=f, fill=INK)
        draw.polygon([(x + s - 12, y + 6), (x + s - 6, y + 6),
                      (x + s - 9, y + 20)], fill=RED)
        draw.line([(x + s - 9, y + 6), (x + s - 9, y + 30)], fill=RED, width=3)
    elif kind == "drone":
        cx, cy = x + s // 2, y + s // 2
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            ex, ey = cx + dx * 13, cy + dy * 13
            draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], outline=INK,
                         width=2)
            draw.line([(cx, cy), (ex, ey)], fill=INK, width=2)
        draw.rectangle([cx - 6, cy - 4, cx + 6, cy + 4], fill=BLUE)
    elif kind == "globe":
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=BLUE,
                     width=2)
        draw.ellipse([x + s // 2 - 7, y + 4, x + s // 2 + 7, y + s - 4],
                     outline=BLUE, width=1)
        draw.line([(x + 4, y + s // 2), (x + s - 4, y + s // 2)], fill=BLUE,
                  width=1)
        f = font(SANS_B, 13)
        draw.text((x + s - 16, y + s - 16), "%", font=f, fill=RED)


PANEL_ICONS = {7: "chip", 42: "dollar", 8: "ballot", 16: "flags",
               24: "dashed", 33: "yen", 27: "drone", 41: "globe"}


def draw_panels(draw):
    x0, x1 = 20, 1004
    gap = 12
    pw = (x1 - x0 - 3 * gap) // 4
    ph, vgap = 64, 8
    y0 = 496
    for i, (num, kick, head, deck) in enumerate(PANELS):
        row, col = divmod(i, 4)
        px = x0 + col * (pw + gap)
        py = y0 + row * (ph + vgap)
        draw.rectangle([px, py, px + pw, py + ph], fill=LIGHT,
                       outline=(200, 193, 176), width=1)
        icon(draw, PANEL_ICONS[num], px + 6, py + 10)
        tx = px + 56
        tw = px + pw - 8 - tx
        draw.text((tx, py + 5), "%d  %s" % (num, kick),
                  font=font(SANS_B, 10), fill=RED)
        hf = font(SERIF_B, 14)
        lines = wrap(draw, head, hf, tw)
        yy = py + 20
        for ln in lines[:2]:
            draw.text((tx, yy), ln, font=hf, fill=INK)
            yy += 16
        df = font(SANS, 10)
        for ln in wrap(draw, deck, df, tw)[:1]:
            draw.text((tx, yy + 1), ln, font=df, fill=(60, 58, 52))
    hline(draw, 20, 1004, 646, width=2)


# ---------------------------------------------------------------- briefs
def fit_font(draw, s, path, start, minimum, max_w):
    size = start
    while size > minimum and text_w(draw, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def draw_briefs(draw):
    draw.text((20, 652), "THE DAY IN BRIEF — ALL 42 STORIES",
              font=font(SANS_B, 12), fill=RED)
    cols_x = [20, 352, 684]
    col_w = 318
    row_h = 18
    y0 = 672
    bf = font(SANS, 12)
    nf = font(SANS_B, 12)
    for idx, (num, region, head) in enumerate(STORIES):
        col, row = divmod(idx, 14)
        x = cols_x[col]
        y = y0 + row * row_h
        draw.text((x, y), str(num), font=nf, fill=RED)
        nx = x + (26 if num < 10 else 32)
        f = fit_font(draw, head, SANS, 12, 10, col_w - (nx - x) - 4)
        draw.text((nx, y), head, font=f, fill=INK)
    hline(draw, 20, 1004, 924, width=2)


# ---------------------------------------------------------------- bottom
def draw_bottom(draw):
    # DATE CHECK box
    bx0, bx1 = 20, 640
    by0, by1 = 932, 1006
    draw.rectangle([bx0, by0, bx1, by1], outline=RED, width=2)
    draw.text((bx0 + 10, by0 + 6), "DATE CHECK",
              font=font(SANS_B, 13), fill=RED)
    df = font(SANS, 11)
    lines = [
        "Every story on this page happened, or was first reported, on Friday 20 Nov 2026.",
        "NOT 20 Nov news, so left out: the ICJ genocide ruling, the Shenzhen summit,",
        "the Anthropic IPO close (all Thu 19 Nov); Kenya's last Ebola discharge (11 Nov);",
        "F1 Las Vegas practice (19 Nov).",
    ]
    y = by0 + 24
    for ln in lines:
        draw.text((bx0 + 10, y), ln, font=df, fill=INK)
        y += 12
    # BY THE NUMBERS box
    nx0, nx1 = 656, 1004
    draw.rectangle([nx0, by0, nx1, by1], fill=LIGHT, outline=RULE, width=1)
    draw.text((nx0 + 10, by0 + 6), "BY THE NUMBERS",
              font=font(SANS_B, 13), fill=INK)
    nf = font(SANS_B, 11)
    nums = [
        "S&P 500 -2.0% (Thu)  •  Nasdaq -2.3%",
        "Nikkei -4.8%  •  Taiex -6.4%  •  Kospi -5.2%",
        "SoftBank -16%  •  Gold -4.2%  •  Brent $90.05",
        "US 10-year yield above 5%  •  Yen near 159/$",
    ]
    y = by0 + 24
    for ln in nums:
        draw.text((nx0 + 10, y), ln, font=nf, fill=INK)
        y += 13
    # footer
    ff = font(SANS, 9)
    foot = ("Sources: BBC, Reuters, AP, AFP, The Guardian, national outlets — "
            "full list in the repo SOURCES.md.  •  Figures as reported 20 Nov 2026.")
    draw.text((20, 1012), foot, font=ff, fill=GREY)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "news.png"
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_leads(draw)
    draw_map(draw)
    draw_panels(draw)
    draw_briefs(draw)
    draw_bottom(draw)
    img.save(out, "PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
