#!/usr/bin/env python3
"""The Sunday Globe - one-page summary of Sunday 22 November 2026 world news.

Single-file, stdlib-only program. Renders a 1024x1024 PNG newspaper front
page to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). Deterministic:
no randomness, no clock, no network. The 5x7 pixel font below was drawn
by hand for this entry, glyph by glyph.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 pixels, '#' = ink, '.' = empty.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
}

FONT.update({
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", ".....", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "•": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
})

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 233)
PAPER2 = (238, 231, 214)
INK = (18, 20, 24)
GRAY = (92, 94, 98)
RULE = (30, 30, 34)
RED = (172, 28, 36)
BLUE = (24, 66, 124)
TEAL = (12, 96, 92)
GOLD = (176, 124, 22)
SKY = (168, 200, 226)
SEA = (52, 96, 140)
SAND = (226, 205, 160)
WHITE = (255, 255, 255)
BLACK = (8, 8, 10)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill and d2 <= r * r:
                    self.set(xx, yy, c)
                elif not fill and r * r - 2 * r <= d2 <= r * r:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(xs[i], yy, xs[i + 1] - xs[i] + 1, 1, c)


def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- text
def text_w(s, scale):
    return (len(s) * 6 - 1) * scale if s else 0


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    cv.rect(cx + gx * scale, y + gy * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_center(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_chars):
    words = s.split()
    lines = []
    cur = ""
    for w_ in words:
        if not cur:
            cur = w_
        elif len(cur) + 1 + len(w_) <= max_chars:
            cur += " " + w_
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- art
def _lcg(seed):
    state = [seed]

    def nxt(n):
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return state[0] % n

    return nxt


def ill_tanker(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    sea_y = y + int(h * 0.62)
    cv.rect(x, sea_y, w, y + h - sea_y, SEA)
    # distant industrial shore on the right
    shore_x = x + int(w * 0.66)
    cv.rect(shore_x, sea_y - 26, w - (shore_x - x), 26, (70, 66, 60))
    cv.rect(shore_x + 12, sea_y - 52, 16, 28, (52, 50, 48))
    cv.rect(shore_x + 44, sea_y - 66, 12, 42, (52, 50, 48))
    cv.rect(shore_x + 74, sea_y - 44, 22, 20, (60, 57, 52))
    # flame and smoke from the plant
    cv.circle(shore_x + 50, sea_y - 74, 9, (232, 116, 28), True)
    cv.circle(shore_x + 50, sea_y - 82, 6, (246, 178, 60), True)
    for i, (dx, dy, r) in enumerate(((58, -92, 10), (70, -104, 13), (86, -112, 16))):
        cv.circle(shore_x + dx, sea_y + dy, r, (104, 102, 100), True)
    # tanker hull and superstructure
    hx = x + 18
    hy = sea_y - 16
    cv.poly([(hx, hy), (hx + 190, hy), (hx + 172, hy + 26), (hx + 22, hy + 26)], (26, 28, 34))
    cv.rect(hx + 8, hy + 20, 176, 6, RED)
    cv.rect(hx + 128, hy - 30, 34, 30, (232, 230, 224))
    cv.rect(hx + 136, hy - 40, 18, 10, (52, 54, 60))
    for i, c in enumerate(((198, 84, 44), (44, 110, 168), (60, 150, 96), (198, 150, 44), (120, 70, 150))):
        cv.rect(hx + 12 + i * 22, hy - 14, 20, 12, c)
    cv.line(hx + 30, hy - 2, hx + 30, hy - 34, (26, 28, 34), 3)
    # waves
    rnd = _lcg(42)
    for _ in range(26):
        wx = x + 6 + rnd(w - 30)
        wy = sea_y + 8 + rnd(h - (sea_y - y) - 14)
        cv.rect(wx, wy, 12, 2, (210, 226, 240))


def ill_ukraine(cv, x, y, w, h):
    cv.rect(x, y, w, h, (18, 24, 44))
    rnd = _lcg(7)
    for _ in range(46):
        cv.set(x + rnd(w), y + rnd(int(h * 0.6)), (200, 208, 226))
    # missile trails with glowing heads
    for (sx, sy, ex, ey) in ((x + 30, y + 8, x + 150, y + 88),
                             (x + 120, y + 4, x + 205, y + 80),
                             (x + 250, y + 10, x + 190, y + 84)):
        cv.line(sx, sy, ex, ey, (150, 156, 170), 2)
        cv.line(sx, sy, ex, ey, (240, 200, 120), 1)
        cv.circle(ex, ey, 4, (250, 170, 60), True)
    # drone silhouettes
    for (dx, dy) in ((x + 70, y + 44), (x + 268, y + 52)):
        cv.rect(dx - 8, dy, 17, 3, (160, 166, 180))
        cv.rect(dx - 2, dy - 5, 5, 13, (160, 166, 180))
        cv.circle(dx - 9, dy + 1, 2, (160, 166, 180), True)
        cv.circle(dx + 9, dy + 1, 2, (160, 166, 180), True)
    # skyline
    base = y + h
    bx = x
    heights = (52, 74, 44, 88, 60, 96, 50, 70, 40, 82, 56)
    i = 0
    while bx < x + w - 20:
        bw = 26 + (i * 7) % 14
        bh = heights[i % len(heights)]
        cv.rect(bx, base - bh, bw, bh, (6, 8, 12))
        rnd2 = _lcg(100 + i)
        for _ in range(bh // 9):
            wx = bx + 3 + rnd2(bw - 7)
            wy = base - bh + 4 + rnd2(bh - 9)
            cv.rect(wx, wy, 3, 4, (246, 205, 92))
        bx += bw + 3
        i += 1
    # explosion glow behind skyline
    cv.circle(x + 208, base - 92, 12, (238, 130, 40), True)
    cv.circle(x + 208, base - 92, 7, (250, 196, 90), True)


def ill_cop(cv, x, y, w, h):
    cv.rect(x, y, w, h, (214, 230, 240))
    # sun with rays, top left
    cv.circle(x + 34, y + 30, 15, (246, 178, 60), True)
    for (ex, ey) in ((x + 34, y + 4), (x + 60, y + 12), (x + 8, y + 12),
                     (x + 62, y + 44), (x + 6, y + 44), (x + 34, y + 56)):
        cv.line(x + 34, y + 30, ex, ey, (240, 160, 50), 3)
    # globe
    gx, gy, gr = x + 118, y + h // 2 + 8, 56
    cv.circle(gx, gy, gr, SEA, True)
    cv.circle(gx - 22, gy - 18, 15, (74, 156, 92), True)
    cv.circle(gx + 18, gy - 26, 11, (74, 156, 92), True)
    cv.circle(gx + 6, gy + 14, 17, (84, 166, 100), True)
    cv.circle(gx - 30, gy + 22, 10, (84, 166, 100), True)
    cv.rect(gx - gr, gy - gr, gr * 2, 8, WHITE)
    for off in (-28, 0, 28):
        cv.line(gx + off, gy - gr + 4, gx + off, gy + gr - 4, (120, 168, 205), 2)
    cv.line(gx - gr + 4, gy, gx + gr - 4, gy, (120, 168, 205), 2)
    # thermometer, right side, mercury near the top
    tx = x + w - 62
    cv.rect(tx, y + 16, 16, h - 52, WHITE)
    cv.frame(tx, y + 16, 16, h - 52, INK, 2)
    cv.rect(tx + 4, y + 26, 8, h - 62, RED)
    cv.circle(tx + 8, y + h - 24, 15, RED, True)
    cv.circle(tx + 8, y + h - 24, 15, INK, False)
    for i in range(5):
        cv.rect(tx + 20, y + 26 + i * 20, 9, 2, INK)
    # heat waves above the globe
    for wx in (gx - 34, gx - 6, gx + 22):
        for s in range(3):
            cv.line(wx + s * 8, y + 22, wx + 4 + s * 8, y + 12, (214, 84, 44), 2)


# ---------------------------------------------------------------- content
LEADS = [
    ("MIDDLE EAST - CONFLICT", RED, ill_tanker,
     "IRAN STRIKES BAHRAIN; TANKERS HIT AT HORMUZ",
     "BAHRAIN SAYS AN IRANIAN ATTACK SET A CIVILIAN PLANT ABLAZE. TWO "
     "TANKERS HIT NEAR HORMUZ; OIL NEAR $90."),
    ("EUROPE - WAR", BLUE, ill_ukraine,
     "110 MISSILES HIT UKRAINE; NATO VOWS",
     "THE YEAR'S BIGGEST BARRAGE: 110 MISSILES, 400 DRONES. OBJECTS "
     "CAME DOWN IN POLAND; NATO VOWS TO DEFEND EVERY INCH."),
    ("GLOBAL - CLIMATE", TEAL, ill_cop,
     "COP31 TALKS DEADLOCKED IN OVERTIME",
     "ANTALYA SUMMIT RUNS INTO A SECOND DAY OF OVERTIME, SPLIT OVER "
     "FOSSIL FUELS AND CLIMATE AID. EU: A GOOD DEAL OR NO DEAL."),
]

REGIONS = [
    ("AMERICAS", BLUE, [
        "MEXICO SEIZES CARTEL BOSS; 11 DIE IN RAID",
        "FLORIDA FLOODS: RIVER TOPS 73-YEAR MARK",
        "MAN CONVICTED OF ARSON OVER 2025 PALISADES FIRE",
        "SEATTLE AIRPORT ARRESTS ON JET BRIDGE DRAW OUTCRY",
        "BOLSONARO HOSPITALISED WITH BLOCKED BOWEL",
    ]),
    ("EUROPE", TEAL, [
        "DRONES SET RUSSIAN CARGO SHIP ABLAZE OFF FINLAND",
        "KYIV OFFERS LOCAL TRUCES FOR 15 VILLAGES",
        "KYIV WANTS PEACE PLEDGES ON PAPER",
        "FINLAND CURBS FLIGHTS AND SHIPPING OVER DRONE RISK",
        "GERMAN MARCHES: SCHOOLS YES, DRAFT NO",
    ]),
    ("MIDDLE EAST", (150, 100, 10), [
        "SAUDI-LED FORCE STOPS 3 HOUTHI MISSILES AT RIYADH",
        "GAZA STRIKE KILLS 3 AID WORKERS",
        "ISRAELI FORCES STRIKE TOWNS IN SOUTHERN LEBANON",
        "FIRE AT BASRA POWER PLANT KILLS 4, INJURES 35",
        "IRAN PLANS ROLLING BLACKOUTS AMID WAR DAMAGE",
    ]),
    ("ASIA-PACIFIC", RED, [
        "TAIWAN STOCKS CRASH 17.5%; FUND ACTS",
        "INDONESIA FIRE: 36 MISSING, 3 DEAD",
        "KOREA MINISTER QUITS OVER AI CHEATING",
        "TOXIC LIQUOR KILLS 11 IN MANIPUR; 180 IN HOSPITAL",
        "MYANMAR JUNTA SLAMS ASEAN DECISION",
    ]),
    ("AFRICA & GLOBAL", (90, 70, 140), [
        "LIBYA PIPELINE BLOCKADE LOSSES TOP $30.7 MILLION",
        "GAS EXPLOSION ROCKS BUS STATION IN LEKKI, LAGOS",
        "EBOLA TOLL PASSES 5,700 AMID DOUBTS",
        "KENYA PAPERS LEAD ON 2027 ELECTION TENSIONS",
        "UN TALKS ON AUTONOMOUS WEAPONS END IN DEADLOCK",
    ]),
    ("MONEY, SCIENCE & SPORT", (40, 110, 60), [
        "US STOCKS FALL INTO CORRECTION IN AI SELL-OFF",
        "RIEMANN PROOF CLAIMED WITH AI HELP",
        "ONE-SHOT CRISPR THERAPY CUTS BAD CHOLESTEROL 52%",
        "ALCARAZ TO FACE ZVEREV IN TURIN FINAL",
        "FRANCE BEAT ARGENTINA TO REACH FINAL VS SPRINGBOKS",
    ]),
]

TIMELINE = [
    ("00:29", "LIBYA COUNTS PIPELINE LOSSES"),
    ("02:39", "N. KOREA DELAYS MARATHON"),
    ("02:41", "RUTTE: NATO DEFENDS POLAND"),
    ("03:56", "INDONESIA FACTORY FIRE SEARCH"),
    ("04:01", "MYANMAR SLAMS ASEAN RULING"),
    ("05:27", "KOREA MINISTER QUITS"),
    ("06:00", "ARAB NEWS: BAHRAIN BLAMES IRAN"),
    ("08:00", "UKRAINE TALLIES RECORD BARRAGE"),
]


# ---------------------------------------------------------------- layout
def render():
    cv = Canvas(W, H, PAPER)
    # masthead
    draw_center(cv, W // 2, 12, "THE SUNDAY GLOBE", 8, INK)
    cv.rect(16, 76, W - 32, 3, RULE)
    cv.rect(16, 82, W - 32, 1, RULE)
    draw_center(cv, W // 2, 90, "SUNDAY, 22 NOVEMBER 2026", 4, RED)
    draw_center(cv, W // 2, 124, "33 STORIES - SIX REGIONS - THE WHOLE DAY ON ONE PAGE", 2, GRAY)
    cv.rect(16, 142, W - 32, 2, RULE)

    # leads: three columns
    col_w = 321
    col_x = (16, 351, 686)
    for i, (kicker, kc, art, head, summ) in enumerate(LEADS):
        x = col_x[i]
        draw_text(cv, x, 150, kicker, 2, kc)
        sub = Canvas(col_w, 118, PAPER)
        art(sub, 0, 0, col_w, 118)
        for row in range(118):
            src = row * col_w * 3
            dst = ((170 + row) * cv.w + x) * 3
            cv.px[dst:dst + col_w * 3] = sub.px[src:src + col_w * 3]
        cv.frame(x, 170, col_w, 118, INK, 2)
        yy = 298
        for ln in wrap(head, 17):
            draw_text(cv, x, yy, ln, 3, INK)
            yy += 25
        yy += 4
        for ln in wrap(summ, 26):
            draw_text(cv, x, yy, ln, 2, (52, 54, 58))
            yy += 19
        if i < 2:
            cv.rect(x + col_w + 6, 150, 1, 322, (196, 190, 172))

    # region grid: 3 columns x 2 rows
    box_w, box_h = 322, 206
    for idx, (name, color, stories) in enumerate(REGIONS):
        bx = 16 + (idx % 3) * (box_w + 12)
        by = 484 + (idx // 3) * (box_h + 8)
        cv.rect(bx, by, box_w, 26, color)
        hs = 3 if text_w(name, 3) <= box_w - 20 else 2
        draw_text(cv, bx + 10, by + (26 - 7 * hs) // 2, name, hs, WHITE)
        yy = by + 34
        for st in stories:
            cv.rect(bx + 2, yy + 4, 6, 6, color)
            lines = wrap(st, 25)
            for ln in lines[:2]:
                draw_text(cv, bx + 16, yy, ln, 2, INK)
                yy += 15
            yy += 4

    # timeline strip
    cv.rect(16, 912, W - 32, 2, RULE)
    draw_text(cv, 16, 920, "THE DAY IN UTC", 2, RED)
    draw_text(cv, 220, 920, "- HOUR BY HOUR", 2, GRAY)
    for i, (tm, label) in enumerate(TIMELINE):
        tx = 16 + (i // 4) * 504
        ty = 942 + (i % 4) * 19
        draw_text(cv, tx, ty, tm, 2, RED)
        draw_text(cv, tx + 66, ty, label, 2, INK)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    save_png(render(), os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
