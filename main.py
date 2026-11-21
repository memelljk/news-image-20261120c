#!/usr/bin/env python3
"""The Full Ledger - 20 November 2026 in one image.
Python 3 standard library only. No network, no clock, fixed seed.
Renders entry.png (1024x1024) deterministically and prints STORY_COUNT.
All letterforms are drawn in code from the bitmap font table below.
"""
import math
import os
import random
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
INK = (26, 24, 20)
PAPER = (246, 241, 230)
PAPER2 = (238, 230, 214)
GREY = (96, 92, 84)
FAINT = (178, 170, 152)
RED = (178, 38, 32)
BLUE = (30, 74, 140)
SKY = (116, 164, 205)
TEAL = (24, 110, 104)
GOLD = (196, 148, 38)
GREEN = (52, 118, 58)
WHITE = (252, 250, 244)

REGION_COLORS = {
    "EUROPE": (30, 74, 140),
    "ASIA": (178, 38, 32),
    "AMERICAS": (24, 110, 104),
    "MIDDLE EAST": (146, 96, 20),
    "AFRICA": (52, 118, 58),
    "OCEANIA": (104, 62, 140),
    "GLOBAL": (70, 70, 74),
}

# ---------------------------------------------------------------- stories
# (region, headline, deck, source) -- heroes first, flagged separately below.
HEROES = [
    ("ASIA", "CYCLONE AKVAN MAKES LANDFALL",
     "Severe cyclone hits Odisha-Andhra coast; 300,000 evacuated, 423 teams.",
     "The Hindu"),
    ("EUROPE", "KYIV BRIDGES HIT IN BIGGEST BARRAGE",
     "400+ drones, 110 missiles; 3 Dnipro bridges struck, 8 killed, power cut.",
     "BBC"),
    ("ASIA", "ASIA'S AI SELL-OFF DEEPENS",
     "Taiwan plunges 2,200 pts below 37,000; Nikkei sinks 4.8% as chips slide.",
     "Wires"),
    ("EUROPE", "UK-EU RESET, A DECADE AFTER BREXIT",
     "100,000 youth places each way; Erasmus+ back 2027; food checks end.",
     "BBC"),
]

STORIES = HEROES + [
    # EUROPE (7 more -> 9)
    ("EUROPE", "MISSILES DOWN IN POLAND",
     "Two Kh-101s and a jet drone fall in Lublin and Subcarpathia; no casualties.", "OneTurn"),
    ("EUROPE", "EUROPE READY TO TALK",
     "Four powers agree binding security guarantees tied to a future ceasefire.", "BBC"),
    ("EUROPE", "ESTONIA SEALS ITS BORDER",
     "Tallinn closes the Russian border for six months; Moscow cries Iron Curtain.", "Wires"),
    ("EUROPE", "ITALY FINES META EUR 805M",
     "Rome penalises Meta over Android photo access in record privacy sanction.", "Wires"),
    ("EUROPE", "HUNGARY LIFTS ITS VETO",
     "Budapest clears EU accession clusters 4 and 5 talks with Ukraine.", "Europa Press"),
    ("EUROPE", "KHARKIV COUNTERPUNCH",
     "Ukraine says 14 settlements and 200 sq km freed in Operation Bear Trap.", "UNITED24"),
    ("EUROPE", "FAIRFORD TWO FACE TRIAL",
     "Two men charged over RAF Fairford incursion face trial in November 2027.", "Wires"),
    # ASIA (8 more -> 10)
    ("ASIA", "WORLD COURT: MYANMAR GENOCIDE",
     "ICJ rules 9-6 for The Gambia; first state held responsible for genocide.", "BBC"),
    ("ASIA", "ONE TABLE IN SHENZHEN",
     "Trump, Xi and Putin hold first three-way summit of the nuclear powers.", "KLZ"),
    ("ASIA", "SENSEX SWIMS UPSTREAM",
     "Sensex +1.21% and Nifty +1.14% defy the global rout in Mumbai trade.", "Wires"),
    ("ASIA", "KOREA'S TRILLION YEAR",
     "Annual exports pass $1 trillion for the first time in Korean history.", "Wires"),
    ("ASIA", "YUNUS HOME TORCHED",
     "Fire at ancestral home of Bangladesh's Muhammad Yunus; arson suspected.", "Wires"),
    ("ASIA", "INDIA-JAPAN 2+2 TALKS",
     "Japanese forces to train on Indian firing ranges from 2027, Tokyo agrees.", "Wires"),
    ("ASIA", "HAYABUSA2 LIMPS ON",
     "Engine trouble forces Japan to abandon the asteroid-landing plan.", "Space"),
    ("ASIA", "NORTH KOREA ENRICHES",
     "IAEA says North Korea is expanding its uranium enrichment programme.", "IAEA"),
    # AMERICAS (14)
    ("AMERICAS", "ANTHROPIC'S $81.3B IPO",
     "Largest IPO on record: opens $111.50, closes $97.17, up 17% on debut.", "AFP"),
    ("AMERICAS", "FIFTH STRAIGHT FALL",
     "S&P 500 -2% into correction; Dow sheds 1,101 pts as AI sell-off bites.", "OneTurn"),
    ("AMERICAS", "US-VENEZUELA TIES RESTORED",
     "Washington and Caracas restore military ties after Maduro's ouster.", "Wires"),
    ("AMERICAS", "FLORIDA UNDER WATER",
     "St. Johns River flooding; Cocoa at record flood stage, more rain due.", "Wires"),
    ("AMERICAS", "SENATE SPEEDS PERMITS 62-33",
     "Bipartisan overhaul passes to speed energy projects and power lines.", "KLZ"),
    ("AMERICAS", "IRAN WAR-POWERS BID FAILS",
     "Senate rejects halt to Iran war 48-51 in first vote since midterms.", "Wires"),
    ("AMERICAS", "TRUMP PUSHES IRAN CALL TO 2027",
     "No new major strikes signalled; decision after Jan 1, Trump says.", "Reuters"),
    ("AMERICAS", "A PARDON FOR PETE ROSE",
     "Trump posthumously pardons the baseball legend Pete Rose.", "BBC"),
    ("AMERICAS", "ELLA LANGLEY SWEEPS CMAS",
     "Entertainer, Female Vocalist, Song and Single of the Year in one night.", "Wires"),
    ("AMERICAS", "F1 LANDS IN LAS VEGAS",
     "Teams fight for the prize-money jackpot under the Strip lights.", "Wires"),
    ("AMERICAS", "HAITI RAID: 34 KILLED",
     "Police say 34 gang members killed in a raid on the capital.", "Wires"),
    ("AMERICAS", "FLORIDA'S 20TH EXECUTION",
     "State carries out a record 20th execution of the year.", "Wires"),
    ("AMERICAS", "CYBER CHIEF OUT",
     "White House replaces national cyber director amid tech outages.", "DW"),
    ("AMERICAS", "BUKELE BIDS FOR TERM THREE",
     "El Salvador's Bukele files for a third term; vote set for 28 Feb 2027.", "AP"),
    # MIDDLE EAST (4)
    ("MIDDLE EAST", "HOOTHI MISSILES AIMED AT RIYADH",
     "Coalition intercepts missiles bound for Riyadh; PIF tower damaged.", "TASS"),
    ("MIDDLE EAST", "GAZA LINE CROSSED",
     "Israeli forces cross the Yellow Line in central Gaza; ceasefire frays.", "Wires"),
    ("MIDDLE EAST", "IRAQ MOVES SOUTH",
     "Forces deploy in Jurf al-Sakhar under deal on oil-smuggling network.", "France 24"),
    ("MIDDLE EAST", "HORMUZ SHOCK DEEPENS",
     "IEA calls strait disruption the largest energy-supply shock on record.", "IEA"),
    # AFRICA (5)
    ("AFRICA", "SENEGAL BOAT TRAGEDY",
     "Dozens missing as boat with 100 migrants sinks; four bodies found.", "BBC"),
    ("AFRICA", "HORN OF AFRICA ON EDGE",
     "Ethiopia and Eritrea mass troops; Somalia expels UAE ambassador.", "Wires"),
    ("AFRICA", "MALAWI'S FUEL CHAOS",
     "Fuel crisis brings roads and markets to a standstill nationwide.", "Wires"),
    ("AFRICA", "RHINOS HOME, GIRAFFES MOVED",
     "Rescued rhinos and relocated giraffes mark conservation wins.", "Wires"),
    ("AFRICA", "NIGERIA: END SUICIDE JAIL",
     "Tinubu asks Senate to end jail terms for attempted suicide.", "BBC"),
    # OCEANIA (1)
    ("OCEANIA", "WELLINGTON TEST, DAY 1",
     "New Zealand 243/5 vs India; Henry Nicholls 113 not out at Basin Reserve.", "Wires"),
    # GLOBAL (7)
    ("GLOBAL", "VOYAGER'S LIGHT-DAY",
     "NASA: Voyager 1 now a full light-day from Earth, farthest object ever.", "NASA"),
    ("GLOBAL", "IMF DEBT ALARM",
     "Global public debt nears 100% of world GDP, IMF warns ministers.", "IMF"),
    ("GLOBAL", "AI'S POWER BILL",
     "IEA warns AI data centres could push emissions sharply higher by 2030.", "IEA"),
    ("GLOBAL", "VAN GOGH SELLS FOR $190.4M",
     "Record price for a Van Gogh canvas after row over Nazi-era history.", "BBC"),
    ("GLOBAL", "YOUTH TAKE THE STREETS",
     "Young people in 25+ countries strike over costs and militarisation.", "Wires"),
    ("GLOBAL", "GTA 6 OUTSELLS A GALAXY",
     "GTA 6 sales pass The Odyssey's $1.80B global box-office run.", "Wires"),
    ("GLOBAL", "COP31 RUNS OVERTIME",
     "Antalya climate summit passes deadline; draft omits fossil fuels.", "Wires"),
]

NUMBERS = [
    ("$81.3B", "ANTHROPIC IPO"),
    ("300,000", "EVACUATED: AKVAN"),
    ("400+110", "DRONES+MISSILES"),
    ("-2,200", "TAIWAN PTS"),
    ("100,000", "YOUTH PLACES"),
    ("$190.4M", "VAN GOGH"),
    ("9-6", "ICJ VOTE"),
    ("$1T", "KOREA EXPORTS"),
]

PANEL_KIND = {
    "WORLD COURT: MYANMAR GENOCIDE": "gavel",
    "ONE TABLE IN SHENZHEN": "flags",
    "ANTHROPIC'S $81.3B IPO": "bell",
    "FLORIDA UNDER WATER": "flood",
    "HOOTHI MISSILES AIMED AT RIYADH": "tower",
    "SENEGAL BOAT TRAGEDY": "boat",
    "WELLINGTON TEST, DAY 1": "cricket",
    "VOYAGER'S LIGHT-DAY": "probe",
    "VAN GOGH SELLS FOR $190.4M": "swirl",
}
HERO_KINDS = ["cyclone", "bridges", "chart", "reset"]

# ---------------------------------------------------------------- font
# 5x7 bitmap letterforms, drawn by hand in this file.
_F = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "<": ("...##", "..#..", ".#...", "#....", ".#...", "..#..", "...##"),
    ">": ("##...", "..#..", "...#.", "....#", "...#.", "..#..", "##..."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}
ROW_MAP = (0, 1, 2, 3, 3, 4, 5, 5, 6, 6)  # 7 glyph rows -> 10 px (cap ~10)


def text_w(s, bold=False):
    # draw_text advances 6px/char plain, 7px/char bold (scale_x=1)
    return len(s) * (7 if bold else 6)


def draw_text(px, x, y, s, color, bold=False, scale_x=1):
    """Draw text; cap height 10px at scale 1, 20px at scale 2 (y)."""
    cx = x
    for ch in s.upper():
        g = _F.get(ch, _F["?"])
        for ry in range(10):
            row = g[ROW_MAP[ry]]
            for rx in range(5):
                if row[rx] == "#":
                    for sx in range(scale_x):
                        put(px, cx + rx * scale_x + sx, y + ry, color)
                        if bold:
                            put(px, cx + rx * scale_x + sx + 1, y + ry, color)
        cx += (5 * scale_x + 1) + (1 if bold else 0)
    return cx - x


def draw_text_big(px, x, y, s, color, sx=3, sy=3):
    cx = x
    for ch in s.upper():
        g = _F.get(ch, _F["?"])
        for ry in range(7):
            for rx in range(5):
                if g[ry][rx] == "#":
                    rect(px, cx + rx * sx, y + ry * sy, sx, sy, color)
        cx += 5 * sx + sx
    return cx - x


def wrap(s, max_chars):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
def new_canvas():
    return bytearray(bytes(PAPER) * (W * H))


def put(px, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i:i + 3] = bytes(c)


def rect(px, x, y, w, h, c):
    for yy in range(max(0, y), min(H, y + h)):
        base = (yy * W + max(0, x)) * 3
        n = min(W, x + w) - max(0, x)
        if n > 0:
            px[base:base + n * 3] = bytes(c) * n


def line(px, x0, y0, x1, y1, c, thick=1):
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        x = x0 + dx * i // steps
        y = y0 + dy * i // steps
        for t in range(thick):
            put(px, x, y + t, c)


def circle(px, cx, cy, r, c, fill=False):
    for a in range(0, 360, 2):
        rad = math.radians(a)
        if fill:
            for rr in range(0, r, 2):
                put(px, int(cx + rr * math.cos(rad)), int(cy + rr * math.sin(rad)), c)
        else:
            put(px, int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad)), c)
            put(px, int(cx + (r - 1) * math.cos(rad)), int(cy + (r - 1) * math.sin(rad)), c)


def tri(px, x, y, s, c):
    for i in range(s):
        line(px, x + s // 2, y, x + i, y + s, c)


# ---------------------------------------------------------------- scenes
def scene(px, kind, x, y, w, h, seed):
    rng = random.Random(seed)
    # sky / ground bands shared by most scenes
    if kind == "cyclone":
        rect(px, x, y, w, h, (38, 70, 110))
        for r in range(30, 6, -5):
            circle(px, x + w // 2, y + h // 3, r, (210, 225, 240))
        circle(px, x + w // 2, y + h // 3, 5, (20, 40, 70), fill=True)
        rect(px, x, y + h - 16, w, 16, (30, 110, 90))
        for i in range(3):  # buses
            bx = x + 8 + i * (w // 3)
            rect(px, bx, y + h - 14, 26, 9, GOLD)
            rect(px, bx + 3, y + h - 12, 20, 4, SKY)
        tri(px, x + w - 26, y + 6, 14, GOLD)
        draw_text(px, x + w - 21, y + 9, "!", INK, bold=True)
    elif kind == "bridges":
        rect(px, x, y, w, h, (24, 28, 48))
        for i in range(14):
            put(px, x + rng.randrange(w), y + rng.randrange(h // 2), (220, 220, 200))
        rect(px, x, y + h - 22, w, 22, (28, 60, 96))  # river
        for b in range(3):
            bx = x + 6 + b * (w // 3)
            rect(px, bx, y + h - 34, w // 3 - 12, 5, (200, 190, 170))
            rect(px, bx + 4, y + h - 22, 4, 12, GREY)
            if b == 1:
                line(px, bx + 8, y + h - 30, bx + 22, y + h - 18, RED, 3)
        for i in range(4):  # missile trails
            line(px, x + 10 + i * 30, y + 4, x + 40 + i * 30, y + 26, (255, 170, 60), 2)
        rect(px, x, y + h - 40, w, 6, (12, 14, 24))  # skyline silhouette
    elif kind == "chart":
        rect(px, x, y, w, h, (18, 20, 26))
        for gx in range(x, x + w, 16):
            line(px, gx, y, gx, y + h, (44, 48, 56))
        for gy in range(y, y + h, 14):
            line(px, x, gy, x + w, gy, (44, 48, 56))
        pts = [(0, 8), (22, 14), (44, 12), (66, 30), (88, 52), (110, 66)]
        for i in range(len(pts) - 1):
            line(px, x + pts[i][0], y + pts[i][1], x + pts[i + 1][0], y + pts[i + 1][1], RED, 3)
        for i in range(5):  # falling chips
            cx0 = x + 12 + i * 24
            rect(px, cx0, y + 44 + (i % 3) * 8, 12, 10, TEAL)
            line(px, cx0 + 6, y + 54 + (i % 3) * 8, cx0 + 6, y + 62 + (i % 3) * 8, GOLD)
    elif kind == "reset":
        rect(px, x, y, w, h, SKY)
        rect(px, x, y + h - 14, w, 14, (70, 90, 70))
        # EU flag block
        rect(px, x + 8, y + 8, 44, 30, BLUE)
        for a in range(12):
            rad = math.radians(a * 30)
            put(px, int(x + 30 + 11 * math.cos(rad)), int(y + 23 + 11 * math.sin(rad)), GOLD)
            put(px, int(x + 31 + 11 * math.cos(rad)), int(y + 23 + 11 * math.sin(rad)), GOLD)
        # Union Jack block (diagonal + crosses)
        ux, uy = x + w - 54, y + 8
        rect(px, ux, uy, 46, 30, (24, 40, 110))
        line(px, ux, uy, ux + 46, uy + 30, WHITE, 3)
        line(px, ux + 46, uy, ux, uy + 30, WHITE, 3)
        line(px, ux, uy, ux + 46, uy + 30, RED, 1)
        line(px, ux + 46, uy, ux, uy + 30, RED, 1)
        rect(px, ux + 19, uy, 8, 30, WHITE)
        rect(px, ux, uy + 11, 46, 8, WHITE)
        rect(px, ux + 21, uy, 4, 30, RED)
        rect(px, ux, uy + 13, 46, 4, RED)
        line(px, x + 20, y + h - 14, x + w - 20, y + h - 22, (120, 90, 50), 4)  # bridge
    elif kind == "gavel":
        rect(px, x, y, w, h, (52, 44, 70))
        rect(px, x + 6, y + 8, 20, 26, GOLD)  # scales post
        line(px, x + 2, y + 12, x + 30, y + 12, GOLD, 2)
        line(px, x + 46, y + 30, x + 78, y + 12, (200, 160, 90), 5)  # gavel
        rect(px, x + 72, y + 6, 14, 10, (150, 100, 50))
        rect(px, x + 30, y + h - 12, 50, 5, (150, 100, 50))
        draw_text(px, x + 34, y + 10, "9-6", GOLD, bold=True)
    elif kind == "flags":
        rect(px, x, y, w, h, (40, 60, 90))
        cols = [RED, (240, 240, 240), BLUE]
        for i, c in enumerate(cols):
            fx = x + 10 + i * 34
            line(px, fx, y + 6, fx, y + h - 8, GREY, 2)
            rect(px, fx + 2, y + 8, 24, 15, c)
        rect(px, x, y + h - 10, w, 10, (30, 40, 34))  # skyline base
        for i in range(5):
            rect(px, x + 6 + i * 22, y + h - 22 - (i % 3) * 5, 12, 14 + (i % 3) * 5, (24, 32, 40))
    elif kind == "bell":
        rect(px, x, y, w, h, (16, 34, 30))
        circle(px, x + 26, y + 18, 11, GOLD)
        rect(px, x + 22, y + 6, 8, 6, GOLD)
        pts = [(44, 34), (60, 26), (74, 28), (90, 12)]
        for i in range(len(pts) - 1):
            line(px, x + pts[i][0], y + pts[i][1], x + pts[i + 1][0], y + pts[i + 1][1], GREEN, 3)
        draw_text(px, x + 44, y + 30, "$81.3B", GOLD, bold=True)
    elif kind == "flood":
        rect(px, x, y, w, h, (90, 120, 140))
        rect(px, x, y + h // 2, w, h // 2, (40, 90, 140))
        for i in range(4):
            line(px, x + 4 + i * 8, y + h // 2 + 6 + i * 7, x + w - 6, y + h // 2 + 3 + i * 7, (170, 205, 230))
        rect(px, x + 14, y + 12, 22, 20, (170, 120, 80))  # house
        tri(px, x + 10, y + 4, 30, (120, 60, 40))
        rect(px, x + 60, y + 18, 16, 14, (150, 110, 70))
    elif kind == "tower":
        rect(px, x, y, w, h, (30, 30, 54))
        rect(px, x + w // 2 - 7, y + 6, 14, h - 18, (150, 160, 180))  # tower
        rect(px, x + w // 2 - 3, y + 2, 6, 8, GOLD)
        for i in range(3):  # intercept arcs
            for a in range(20, 90, 6):
                rad = math.radians(a)
                put(px, int(x + 12 + i * 8 + 34 * math.cos(rad)), int(y + h - 8 - 34 * math.sin(rad)), (255, 190, 80))
        rect(px, x + w // 2 + 10, y + 16, 10, 6, RED)  # damage flash
    elif kind == "boat":
        rect(px, x, y, w, h, (60, 110, 150))
        rect(px, x, y + h - 16, w, 16, (30, 80, 130))
        for i in range(5):
            line(px, x + i * 22, y + h - 10, x + 12 + i * 22, y + h - 14, (190, 220, 240))
        line(px, x + 18, y + h - 18, x + 78, y + h - 18, (120, 70, 40), 4)  # hull tilted
        line(px, x + 24, y + h - 18, x + 70, y + h - 30, (120, 70, 40), 3)
        for i in range(4):
            circle(px, x + 30 + i * 12, y + h - 26, 3, GOLD, fill=True)
    elif kind == "cricket":
        rect(px, x, y, w, h, (60, 130, 70))
        rect(px, x + w // 2 - 5, y + 8, 10, h - 16, (210, 190, 150))  # pitch
        rect(px, x + w // 2 - 9, y + h - 18, 18, 4, (240, 240, 240))  # crease
        line(px, x + w // 2 + 8, y + 20, x + w // 2 + 22, y + 34, (240, 220, 90), 3)  # bat swing
        circle(px, x + w // 2 + 30, y + 14, 3, RED, fill=True)
        draw_text(px, x + 6, y + 6, "243/5", WHITE, bold=True)
    elif kind == "probe":
        rect(px, x, y, w, h, (8, 10, 24))
        for i in range(18):
            put(px, x + rng.randrange(w), y + rng.randrange(h), (230, 230, 220))
        circle(px, x + 30, y + 22, 12, (200, 200, 210))
        rect(px, x + 44, y + 18, 22, 8, GOLD)  # bus
        line(px, x + 55, y + 22, x + 88, y + 8, (120, 200, 255), 2)  # signal
        line(px, x + 55, y + 22, x + 88, y + 34, (120, 200, 255), 1)
    elif kind == "swirl":
        rect(px, x, y, w, h, (24, 40, 96))
        for r in range(26, 4, -4):
            circle(px, x + w // 2, y + h // 2, r, (240, 210, 90) if r % 8 == 2 else (90, 140, 220))
        rect(px, x, y + h - 10, w, 10, (30, 60, 40))
        circle(px, x + 12, y + 10, 4, (250, 240, 180), fill=True)
    else:
        rect(px, x, y, w, h, GREY)


# ---------------------------------------------------------------- layout
def main():
    px = new_canvas()
    rect(px, 0, 0, W, H, PAPER)
    rng = random.Random(20261120)
    for _ in range(260):  # paper grain, deterministic
        put(px, rng.randrange(W), rng.randrange(H), PAPER2)

    # ---- date rail (left edge)
    rect(px, 0, 0, 30, H, INK)
    for i, hh in enumerate(range(0, 25, 2)):
        y = 70 + i * 74
        line(px, 8, y, 22, y, FAINT, 1)
        draw_text(px, 4, y + 4, "%02d" % hh, (210, 205, 190))
    # vertical "20 NOV" markers down the rail
    label = "20 NOV * 20 NOV * 20 NOV"
    for i, ch in enumerate(label):
        g = _F.get(ch, _F[" "])
        for ry in range(7):
            for rx in range(5):
                if g[ry][rx] == "#":
                    put(px, 23 + rx, 640 + i * 11 + ry, GOLD)
    draw_text(px, 4, 46, "UTC", GOLD, bold=True)

    X0 = 38
    XR = W - 10

    # ---- masthead
    draw_text_big(px, X0, 8, "THE FULL LEDGER", INK, sx=3, sy=3)
    draw_text(px, X0, 36, "FRIDAY, 20 NOVEMBER 2026", RED, bold=True, scale_x=2)
    draw_text(px, 560, 36, "50 STORIES | 7 REGIONS | ONE PAGE", INK, bold=True)
    line(px, X0, 54, XR, 54, INK, 3)
    line(px, X0, 59, XR, 59, INK, 1)

    # ---- hero row
    hy, hh = 64, 154
    hw = (XR - X0 - 3 * 8) // 4
    for i, (reg, head, deck, src) in enumerate(HEROES):
        x = X0 + i * (hw + 8)
        col = REGION_COLORS[reg]
        rect(px, x, hy, hw, 4, col)
        scene(px, HERO_KINDS[i], x, hy + 6, hw, 74, 100 + i)
        yy = hy + 84
        for ln in wrap(head, 19):
            draw_text_big(px, x + 2, yy, ln, INK, sx=2, sy=2)
            yy += 16
        for ln in wrap(deck, 39)[:2]:
            draw_text(px, x + 2, yy, ln, (52, 50, 44))
            yy += 11
        draw_text(px, x + 2, yy + 1, src.upper() + " | 20 NOV", col, bold=True)

    # ---- region columns
    top = hy + hh + 8
    bottom = 944
    col_w = (XR - X0 - 12) // 2
    columns = [
        [("EUROPE", [s for s in STORIES[4:] if s[0] == "EUROPE"]),
         ("ASIA", [s for s in STORIES[4:] if s[0] == "ASIA"]),
         ("GLOBAL", [s for s in STORIES[4:] if s[0] == "GLOBAL"])],
        [("AMERICAS", [s for s in STORIES[4:] if s[0] == "AMERICAS"]),
         ("MIDDLE EAST", [s for s in STORIES[4:] if s[0] == "MIDDLE EAST"]),
         ("AFRICA", [s for s in STORIES[4:] if s[0] == "AFRICA"]),
         ("OCEANIA", [s for s in STORIES[4:] if s[0] == "OCEANIA"])],
    ]
    region_total = {"EUROPE": 9, "ASIA": 10, "AMERICAS": 14, "MIDDLE EAST": 4,
                    "AFRICA": 5, "OCEANIA": 1, "GLOBAL": 7}
    panel_count = 4

    def block_height(items):
        hgt = 18
        for it in items:
            hgt += 44 if it[1] in PANEL_KIND else 22
        return hgt

    for ci, blocks in enumerate(columns):
        x = X0 + ci * (col_w + 12)
        heights = [block_height(items) for _, items in blocks]
        leftover = max(0, bottom - top - sum(heights))
        gaps = [leftover // len(blocks) + (1 if i < leftover % len(blocks) else 0)
                for i in range(len(blocks))]
        y = top
        for bi, (reg, items) in enumerate(blocks):
            col = REGION_COLORS[reg]
            rect(px, x, y, col_w, 15, col)
            draw_text(px, x + 5, y + 2, reg + "  (" + str(region_total[reg]) + ")", WHITE, bold=True)
            y += 18
            for (r, head, deck, src) in items:
                kind = PANEL_KIND.get(head)
                if kind:
                    panel_count += 1
                    ph = 42
                    scene(px, kind, x, y, 104, ph, 500 + panel_count)
                    tx = x + 110
                    tw = col_w - 110
                    draw_text(px, tx, y, head[:tw // 7], INK, bold=True)
                    dl = wrap(deck, tw // 6 - 2)
                    for j, ln in enumerate(dl[:2]):
                        draw_text(px, tx, y + 12 + j * 11, ln, (52, 50, 44))
                    draw_text(px, tx, y + 33, src.upper() + " | 20 NOV", col, bold=True)
                    y += ph + 2
                else:
                    tag = src.upper() + " 20NOV"
                    limit = (col_w - text_w(tag, True) - 12) // 7
                    draw_text(px, x, y, head[:limit], INK, bold=True)
                    draw_text(px, x + col_w - text_w(tag, True), y, tag, col, bold=True)
                    dl = wrap(deck, col_w // 6)
                    draw_text(px, x, y + 11, dl[0] if dl else "", (52, 50, 44))
                    y += 22
            y += gaps[bi]
        # column rule
        if ci == 0:
            line(px, x + col_w + 5, top, x + col_w + 5, bottom, FAINT, 1)

    # ---- by the numbers
    ny = 954
    line(px, X0, ny - 4, XR, ny - 4, INK, 2)
    tw8 = (XR - X0 - 7 * 6) // 8
    for i, (num, lab) in enumerate(NUMBERS):
        x = X0 + i * (tw8 + 6)
        rect(px, x, ny, tw8, 40, PAPER2)
        rect(px, x, ny, tw8, 3, GOLD)
        draw_text(px, x + 5, ny + 7, num, RED, bold=True, scale_x=2)
        draw_text(px, x + 5, ny + 27, lab[:tw8 // 6 - 1], GREY)

    # ---- footer
    fy = 1000
    line(px, X0, fy - 3, XR, fy - 3, INK, 1)
    draw_text(px, X0, fy + 2,
              "EVERY STORY CROSS-CHECKED AGAINST AT LEAST TWO REPORTS - 20 NOVEMBER 2026 (UTC)",
              INK, bold=True)
    draw_text(px, XR - text_w("THE FULL LEDGER", True), fy + 2, "THE FULL LEDGER", RED, bold=True)

    data = encode_png(px)
    with open("entry.png", "wb") as f:
        f.write(data)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if os.path.isdir(outdir):
        with open(os.path.join(outdir, "entry.png"), "wb") as f:
            f.write(data)
    print("STORY_COUNT=%d" % len(STORIES))
    print("PANEL_COUNT=%d" % panel_count)


def encode_png(px):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += px[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))


if __name__ == "__main__":
    main()
