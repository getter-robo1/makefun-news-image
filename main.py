#!/usr/bin/env python3
"""news-image-20261124: draw one 1024x1024 front-page image summing up the
world news of Tuesday 24 November 2026 and write it to /output/entry.png.

Pure Python 3 standard library only (os, sys, zlib, struct): no network, no
randomness, no timestamps, no third-party packages, so the grader's two runs
write byte-identical PNGs. All news is baked in as constants below.

Rendering is done by hand: a small RGB canvas, a few drawing primitives, and
a 5x7 bitmap font scaled up for headlines and body text.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# --------------------------------------------------------------------------
# 5x7 bitmap font (printable ASCII 32..126). Each glyph is 7 rows of 5 bits,
# written as strings of '0' (off) and '1' (on), top row first.
# --------------------------------------------------------------------------
FONT = {
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10101", "01110", "00101", "01111", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01110", "10001", "10010", "01010", "10101", "10010", "01011"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '*': ("00000", "01010", "01110", "11111", "01110", "01010", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ',': ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10001", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ';': ("00000", "00100", "00000", "00000", "00100", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10101", "10010", "01110"),
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    '\\': ("10000", "10000", "01000", "01000", "00100", "00100", "00010"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '^': ("00100", "01010", "00000", "00000", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '`': ("01000", "01000", "00100", "00000", "00000", "00000", "00000"),
    'a': ("00000", "00000", "01111", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "01110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "01110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10001", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '{': ("00011", "00100", "00100", "01100", "00100", "00100", "00011"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '}': ("11000", "00100", "00100", "00110", "00100", "00100", "11000"),
    '~': ("00000", "00000", "01101", "10101", "00000", "00000", "00000"),
}


# --------------------------------------------------------------------------
# Minimal PNG writer (truecolour RGB, filter 0, one IDAT chunk, no ancillary
# chunks, so output is fully deterministic).
# --------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, buf, w, h):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: None
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# --------------------------------------------------------------------------
# Canvas: an RGB bytearray with simple drawing primitives.
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        # Bresenham, with a square brush of size t for thickness.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        # Midpoint circle; filled by scanlines when fill=True.
        x = 0
        y = r
        d = 1 - r
        pts = []
        while x <= y:
            pts.append((x, y))
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        if fill:
            for px, py in pts:
                self.fill_rect(cx - px, cy - py, 2 * px + 1, 1, color)
                self.fill_rect(cx - px, cy + py, 2 * px + 1, 1, color)
                self.fill_rect(cx - py, cy - px, 2 * py + 1, 1, color)
                self.fill_rect(cx - py, cy + px, 2 * py + 1, 1, color)
        else:
            for px, py in pts:
                for sx, sy in ((px, py), (py, px), (-px, py), (-py, px),
                               (px, -py), (py, -px), (-px, -py), (-py, -px)):
                    self._px(cx + sx, cy + sy, color)

    def ellipse(self, cx, cy, rx, ry, color, fill=True):
        # Filled ellipse by scanlines (or outline by sampling the rim).
        if fill:
            for dy in range(-ry, ry + 1):
                half = int(rx * (1 - (dy * dy) / float(ry * ry)) ** 0.5)
                self.fill_rect(cx - half, cy + dy, 2 * half + 1, 1, color)
        else:
            import math
            for deg in range(0, 360, 2):
                a = math.radians(deg)
                self._px(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), color)

    def triangle(self, pts, color):
        # Filled triangle by scanline rasterisation.
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin = max(0, min(y0, y1, y2))
        ymax = min(self.h - 1, max(y0, y1, y2))
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, y, xb - xa + 1, 1, color)


# --------------------------------------------------------------------------
# Text: the 5x7 font drawn at integer scale. Character advance is 6*scale
# (5 pixels of glyph + 1 pixel of tracking); line height is 9*scale.
# --------------------------------------------------------------------------
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def draw_text_right(cv, x, y, text, scale, color):
    draw_text(cv, x - text_width(text, scale), y, text, scale, color)


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    max_chars = max(1, (max_w + scale) // (6 * scale))
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is hard-split.
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, text, scale, color, max_w, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    lh = leading if leading is not None else 9 * scale
    for line in wrap_text(text, scale, max_w):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


# --------------------------------------------------------------------------
# Small pictogram icons, drawn with the same primitives.
# --------------------------------------------------------------------------
def icon_globe(cv, x, y, s, ink, red):
    # A globe: circle, meridians, equator, and a red crack across it.
    r = s // 2
    cx, cy = x + r, y + r
    cv.circle(cx, cy, r, ink, fill=False)
    cv.ellipse(cx, cy, r // 2, r, ink, fill=False)
    cv.ellipse(cx, cy, r, r // 3, ink, fill=False)
    cv.hline(x, cy, s, ink, 2)
    # A jagged crack across the globe (one broken line, not an X).
    crack = [(x + s // 4, y + s // 6),
             (x + 2 * s // 5, y + s // 3),
             (x + s // 3, y + s // 2),
             (x + 11 * s // 20, y + 3 * s // 5),
             (x + s // 2, y + 4 * s // 5),
             (x + 2 * s // 3, y + 11 * s // 12)]
    for (ax, ay), (bx, by) in zip(crack, crack[1:]):
        cv.line(ax, ay, bx, by, red, 5)


def icon_ship(cv, x, y, s, ink, blue):
    # A cargo ship on waves.
    cv.fill_rect(x + s // 6, y + s // 3, 2 * s // 3, s // 6, ink)
    cv.triangle([(x + s // 6, y + s // 2), (x + 5 * s // 6, y + s // 2),
                 (x + 3 * s // 4, y + 2 * s // 3)], ink)
    cv.fill_rect(x + s // 2 - 2, y + s // 8, 4, s // 4, ink)
    cv.fill_rect(x + s // 2, y + s // 8, s // 5, s // 10, blue)
    for i, wy in enumerate((y + 3 * s // 4, y + 5 * s // 6)):
        cv.hline(x + i * s // 8, wy, s - i * s // 4, blue, 3)


def icon_shield(cv, x, y, s, ink, blue):
    # A shield with Estonia's blue-black-white bars.
    w = 3 * s // 4
    h = s
    x0 = x + (s - w) // 2
    cv.fill_rect(x0, y, w, h // 3, blue)
    cv.fill_rect(x0, y + h // 3, w, h // 3, ink)
    cv.fill_rect(x0, y + 2 * h // 3, w, h // 3, (245, 245, 245))
    cv.rect(x0, y, w, h, ink, 3)
    cv.triangle([(x0 + w // 2 - 6, y + h - 2), (x0 + w // 2 + 6, y + h - 2),
                 (x0 + w // 2, y + h + s // 6)], ink)


def icon_flame(cv, x, y, s, orange, red):
    # A flame: two stacked teardrops.
    cx = x + s // 2
    cv.circle(cx, y + 2 * s // 3, s // 4, orange, fill=True)
    cv.triangle([(cx - s // 4, y + 2 * s // 3), (cx + s // 4, y + 2 * s // 3),
                 (cx, y + s // 6)], orange)
    cv.circle(cx, y + 3 * s // 4, s // 7, red, fill=True)
    cv.triangle([(cx - s // 7, y + 3 * s // 4), (cx + s // 7, y + 3 * s // 4),
                 (cx, y + s // 2)], red)


def icon_train(cv, x, y, s, ink, teal):
    # A train front on tracks.
    w = 2 * s // 3
    x0 = x + (s - w) // 2
    cv.fill_rect(x0, y + s // 6, w, s // 2, teal)
    cv.fill_rect(x0 + w // 8, y + s // 4, w // 4, s // 6, (251, 247, 238))
    cv.fill_rect(x0 + 5 * w // 8, y + s // 4, w // 4, s // 6, (251, 247, 238))
    cv.fill_rect(x0, y + s // 2, w, s // 12, ink)
    cv.circle(x0 + w // 4, y + 2 * s // 3, s // 14, ink, fill=True)
    cv.circle(x0 + 3 * w // 4, y + 2 * s // 3, s // 14, ink, fill=True)
    cv.hline(x, y + 5 * s // 6, s, ink, 3)


def icon_burst(cv, x, y, s, ink, red):
    # An explosion starburst.
    cx, cy = x + s // 2, y + s // 2
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        cv.line(cx, cy, cx + dx * s // 2, cy + dy * s // 2, ink, 4)
    cv.circle(cx, cy, s // 6, red, fill=True)
    cv.circle(cx, cy, s // 12, (251, 247, 238), fill=True)


# --------------------------------------------------------------------------
# Palette.
# --------------------------------------------------------------------------
PAPER = (251, 247, 238)
INK = (22, 19, 14)
RED = (166, 25, 46)
BLUE = (31, 78, 121)
TEAL = (20, 82, 74)
GRAY = (107, 101, 90)
LIGHT = (233, 226, 211)
ORANGE = (204, 102, 0)

MX = 36            # side margin
RX = W - MX        # right edge of the content column (988)
CW = RX - MX       # content width (952)

# --------------------------------------------------------------------------
# The day's news, baked in. Every fact below was reported in the world press
# on 23-24 November 2026; wording is kept to what was reported, no hype.
# --------------------------------------------------------------------------
LEAD = {
    "kicker": "CLIMATE - COP31 - ANTALYA",
    "head1": "COP31 COLLAPSES",
    "head2": "NO FOSSIL-FUEL DEAL",
    "body": ("After two weeks in Antalya, 194 nations reject the draft "
             "Antalya Pact. It never mentions fossil fuels, so the EU and "
             "island states refuse it."),
}

SECONDARY = [
    {
        "kicker": "STRAIT OF HORMUZ",
        "head": ["25 SEAFARERS", "KILLED AT SEA"],
        "body": "UN counts 25 killed around the Strait of Hormuz since February.",
        "accent": BLUE,
        "icon": "ship",
    },
    {
        "kicker": "ESTONIA - RUSSIA",
        "head": ["RUSSIA WARNS OF", "'OPEN WAR'"],
        "body": "Moscow warns Tallinn over its six-month border closure.",
        "accent": RED,
        "icon": "shield",
    },
    {
        "kicker": "BANTEN, INDONESIA",
        "head": ["FIRE KILLS 24", "IN BANTEN"],
        "body": "Candy factory blaze; about 30 still missing.",
        "accent": ORANGE,
        "icon": "flame",
    },
    {
        "kicker": "INDIA - NEPAL",
        "head": ["INDIA PLEDGES", "$1.6BN TO NEPAL"],
        "body": "Aid after floods, plus a new Saryu-Kamala Express rail link.",
        "accent": TEAL,
        "icon": "train",
    },
]

KYIV_HEAD = "KYIV HIT; SHIP BURNS AT SEA"
KYIV_BODY = ("Russian drones hit the Kyiv region; cargo ship Sparta II "
             "burns in the Gulf of Finland.")

ALSO_2 = "BEPICOLOMBO ENTERS MERCURY ORBIT  -  CHESS WORLD CHAMPIONSHIP OPENS IN GENEVA"

FOOTER = "Compiled from world news reports of 24 November 2026."


def draw_icon(cv, kind, x, y, s, ink):
    if kind == "ship":
        icon_ship(cv, x, y, s, ink, BLUE)
    elif kind == "shield":
        icon_shield(cv, x, y, s, ink, BLUE)
    elif kind == "flame":
        icon_flame(cv, x, y, s, ORANGE, RED)
    elif kind == "train":
        icon_train(cv, x, y, s, ink, TEAL)


def draw_cell(cv, x, y, w, h, story):
    cv.fill_rect(x, y, 6, h, story["accent"])
    cv.fill_rect(x + 6, y, w - 6, h, LIGHT)
    ix = x + w - 52
    draw_icon(cv, story["icon"], ix, y + 10, 44, INK)
    draw_text(cv, x + 20, y + 12, story["kicker"], 2, RED)
    draw_text(cv, x + 20, y + 38, story["head"][0], 4, INK)
    draw_text(cv, x + 20, y + 74, story["head"][1], 4, INK)
    draw_para(cv, x + 20, y + 114, story["body"], 3, INK, w - 40, leading=25)


def draw_page():
    cv = Canvas(W, H, PAPER)

    # ---- Masthead ----
    cv.fill_rect(MX, 26, CW, 4, INK)
    draw_text_centered(cv, W // 2, 40, "THE WORLD TODAY", 9, INK)
    draw_text_centered(cv, W // 2, 112, "TUESDAY, 24 NOVEMBER 2026", 4, INK)
    cv.fill_rect(MX, 150, CW, 4, RED)

    # ---- Lead story: COP31 ----
    icon_globe(cv, MX, 176, 180, INK, RED)
    tx = MX + 204
    draw_text(cv, tx, 176, LEAD["kicker"], 3, RED)
    draw_text(cv, tx, 206, LEAD["head1"], 7, INK)
    draw_text(cv, tx, 262, LEAD["head2"], 5, INK)
    draw_para(cv, tx, 308, LEAD["body"], 3, INK, RX - tx, leading=27)

    # ---- Divider ----
    cv.fill_rect(MX, 434, CW, 2, INK)

    # ---- Secondary grid: 2 x 2 ----
    cell_w = 460
    cell_h = 190
    positions = [(MX, 448), (MX + 492, 448), (MX, 652), (MX + 492, 652)]
    for pos, story in zip(positions, SECONDARY):
        draw_cell(cv, pos[0], pos[1], cell_w, cell_h, story)

    # ---- Kyiv strip ----
    sy = 852
    cv.fill_rect(MX, sy, CW, 104, LIGHT)
    cv.rect(MX, sy, CW, 104, INK, 2)
    icon_burst(cv, MX + 20, sy + 22, 60, INK, RED)
    draw_text(cv, MX + 104, sy + 14, KYIV_HEAD, 4, INK)
    draw_para(cv, MX + 104, sy + 50, KYIV_BODY, 3, INK,
              RX - (MX + 104) - 16, leading=26)

    # ---- Also today (red label, ink items) ----
    ax = draw_text(cv, MX, 966, "ALSO TODAY", 2, RED)
    draw_text(cv, ax, 966, "  -  VERSTAPPEN WINS LAS VEGAS GP  -  ALCARAZ WINS ATP FINALS", 2, INK)
    draw_text(cv, MX, 984, ALSO_2, 2, INK)

    # ---- Footer ----
    draw_text_centered(cv, W // 2, 1006, FOOTER, 2, GRAY)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = draw_page()
    write_png(os.path.join(out_dir, "entry.png"), page.buf, W, H)


if __name__ == "__main__":
    main()
